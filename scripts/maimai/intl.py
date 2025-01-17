import ipdb
import requests
import json
import re
import copy
import random
import time
from shared.common_func import *
from maimai.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

# wiki_url = 'https://silentblue.remywiki.com/maimai_DX:BUDDiES_PLUS_(Asia)'
wiki_url = 'https://silentblue.remywiki.com/maimai_DX:PRiSM_(Asia)'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

def sync_json_data():
    print_message(f"Syncing song data from JP to INTL", 'H2', log=True, is_verbose=True)

    # Read data from the first JSON file
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        src_music_data = json.load(f)

    # Read data from the second JSON file
    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        dest_music_data = json.load(f)

    src_music_map = json_to_hash_value_map(src_music_data)

    dest_music_map = json_to_hash_value_map(dest_music_data)
    old_dest_music_data = copy.deepcopy(dest_music_data)

    added_songs = []
    removed_songs = []

    # Compare sets of IDs to identify added and removed songs
    added_ids = set(src_music_map.keys()) - set(dest_music_map.keys())
    removed_ids = set(dest_music_map.keys()) - set(src_music_map.keys())

    updated_songs = []
    unchanged_songs = []
    for id, src_song in src_music_map.items():
        if id in dest_music_map:
            local_song = dest_music_map[id]
            # Remove the "sort" key from both server_song and local_song
            src_song_without_sort = {k: v for k, v in src_song.items() if k != "sort"}
            local_song_without_sort = {k: v for k, v in local_song.items() if k != "sort"}

            if src_song_without_sort != local_song_without_sort:
                # Song has been updated (excluding the "sort" key), include it in the updated_songs list
                updated_songs.append(src_song)
            else:
                # Maimai always updates the "sort" value so let's keep it updated...
                unchanged_songs.append(src_song)

    # if added_ids:
    #     added_songs = [src_music_map[id] for id in added_ids]

    #     for song in added_songs:
    #         song_diffs = [0]
    #         dest_music_data.append(song)
    #         lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
    #         print_message(f"- Song copied from JP data", bcolors.OKGREEN)

    #     print_message(f"Added {len(added_songs)} new songs to {LOCAL_INTL_MUSIC_EX_JSON_PATH}.", log=True)


    if removed_ids:
        removed_songs = [dest_music_map[id] for id in removed_ids]

        for song in removed_songs:
            song_diffs = [0]
            song_hash = generate_hash_from_keys(song)
            existing_song = next((s for s in dest_music_data if generate_hash_from_keys(s) == song_hash), None)

            if existing_song:
                # dest_music_data.remove(existing_song)
                lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                print_message(f"- Warning: Song does not exist in JP data", bcolors.FAIL)

        # print_message(f"Removed {len(removed_songs)} songs from {LOCAL_INTL_MUSIC_EX_JSON_PATH}.", log=True)

    # Iterate through updated songs
    # For the list of updated songs, go through each of them in older song list
    # Find the same song in ex_data list then update any changed keys
    for song in updated_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_dest_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_song = next((s for s in dest_music_data if generate_hash_from_keys(s) == song_hash), None)

        added_charts_sets = {
            "added_charts_dx": {"dx_lev_bas", "dx_lev_adv", "dx_lev_exp", "dx_lev_mas"},
            "added_charts": {"lev_bas", "lev_adv", "lev_exp", "lev_mas"},
            "added_charts_dx_remas": {"dx_lev_remas"},
            "added_charts_remas": {"lev_remas"}
        }

        # Song can't be found in music-ex.json
        if not dest_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- Couldn't find matching song in music-ex.json", bcolors.WARNING)
            continue

        if old_song == song:
            continue

        if old_song and dest_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # Don't update these keys
                if key in ['date', 'version', 'intl', 'release', 'date_intl_added', 'date_intl_updated']:
                    continue

                # overwrite silently
                if key == 'sort':
                    dest_song[key] = value
                    continue

                # Don't copy keys that don't exist in INTL
                # They might be keys for new added charts in existing songs that are not yet added to INTL

                # if key not in old_song:
                #     lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                #     print_message(f"- Added key {key}: {song[key]}", bcolors.OKGREEN)
                #     dest_song[key] = value
                if key not in old_song:
                    continue
                elif old_song[key] != value and value != "":
                    if old_song[key] == "":
                        lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                        print_message(f"- Added value for {key}: {song[key]}", bcolors.OKBLUE)
                        dest_song[key] = value
                    else:
                        lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                        print_message(f"- Overwrote {key}: {old_song[key]} → {song[key]}", bcolors.OKBLUE)
                        dest_song[key] = value

            # # Check for removed keys
            # for key in old_song:
            #     # maimai uses 'date' key for recording NEW markers... ignore them
            #     if key == 'date' or key == 'version':
            #         continue
            #     if key not in song:
            #         del dest_song[key]

            # # Check if new charts have been added
            # new_added_keys = set(song.keys()) - set(old_song.keys())

            # if song['title'] == "幻想に咲いた花":
            #     ipdb.set_trace()

            # # Check which set is a subset of new_added_keys
            # matching_set_name = next(
            #     (name for name, chart_set in added_charts_sets.items() if chart_set.issubset(new_added_keys)),
            #     None
            # )

            # if matching_set_name:
            #     dest_song['date_updated'] = f"{datetime.now().strftime('%Y%m%d')}"
            #     lazy_print_song_header(f"{song['title']}", song_diffs, log=True)

            #     if matching_set_name == "added_charts_dx":
            #         print_message(f"- DX charts added", bcolors.OKGREEN)
            #     elif matching_set_name == "added_charts":
            #         print_message(f"- STD charts added", bcolors.OKGREEN)
            #     elif matching_set_name == "added_charts_dx_remas":
            #         print_message(f"- RE:MASTER (DX) chart added", bcolors.OKGREEN)
            #     elif matching_set_name == "added_charts_remas":
            #         print_message(f"- RE:MASTER (STD) chart added", bcolors.OKGREEN)


            # record_diffs(song, song_hash, 'updated')


    # Iterate through unchanged songs
    for song in unchanged_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_dest_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_song = next((s for s in dest_music_data if generate_hash_from_keys(s) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- Couldn't find matching song in {LOCAL_INTL_MUSIC_EX_JSON_PATH}", bcolors.WARNING)
            continue

        if old_song and dest_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
                if key not in old_song or old_song[key] != value:
                    dest_song[key] = value

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
                if key not in song:
                    del dest_song[key]

    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(dest_music_data, f, ensure_ascii=False, indent=2)


# Update on top of existing music-ex
def add_intl_info():
    total_diffs = [0]

    print_message(f"Update International ver. song data from RemyWiki", 'H2', log=True, is_verbose=True)

    # Load JSON data
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_intl_music_ex_data = json.load(f)

    # Get Wiki page
    print_message(f"Request URL: {wiki_url}", bcolors.ENDC, log=True, is_verbose=True)
    try:
        wiki = requests.get(wiki_url, timeout=5, headers=request_headers, allow_redirects=True)
    except requests.RequestException as e:
        print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True, is_verbose=True)
        return


    # Parse HTML
    soup = BeautifulSoup(wiki.text, 'html.parser')

    # Find all tables with class 'bluetable'
    song_list = soup.find('span', id="New_Songs_/_DX_Charts", class_="mw-headline")
    table = song_list.find_next('table', class_='bluetable')
    rows = table.find_all('tr')

    # Initialize a dictionary to store songs

    # Iterate through each row
    for row in rows:
        wiki_song = {}
        header_printed = [0]

        # Reset utility vars
        song_matched = False
        # If this is empty, it means the song has single chart type (dx/std unknown)
        wiki_chart_type = ''
        # If B/A/E/M fields are empty, it means only Re:MAS is added at this time
        only_remas = False

        matched_jp_song = None
        matched_jp_old_song = None
        matched_intl_song = None
        matched_intl_old_song = None
        jp_song_matched = False
        intl_song_matched = False

        song_details = row.find_all('td')

        # skip header rows
        if len(song_details) <= 1:
            continue

        # Find the closest previous th tag to get the datestamp
        date_stamp = None
        prev_th = row.find_previous('th')
        while prev_th:
            if prev_th.get('id') and re.match(r'\d{8}', prev_th['id']):
                date_stamp = prev_th
                break
            prev_th = prev_th.find_previous('th')

        if date_stamp:
            # Extract the date in yyyymmdd format if the id attribute matches
            date = date_stamp['id']
        else:
            # Skip if no datestamp found
            continue

        # Check if it's a UTAGE song
        utage_td = row.find('td', style="color:white; background:#dc39b8;", colspan="4")

        if utage_td:
            # Extract kanji and stars from UTAGE row
            title = song_details[1].text.strip()
            artist = song_details[2].text.strip()
            kanji = song_details[0].text.strip()[0]
            lev_utage = song_details[3].text.strip()

            # Add song to dictionary with date
            wiki_song = {
                'title': normalize_title(title),
                'artist': normalize_title(artist),
                'date': date,
                'kanji': kanji,
                'lev_utage': lev_utage
            }

        # Non-UTAGE song
        else:
            # If <small> tag is present, it means the song has both chart types
            small_tag = song_details[0].find('small')
            if small_tag:
                chart_type_text = small_tag.text.strip()

                if 'Standard' in chart_type_text:
                    wiki_chart_type = 'std'
                else:
                    wiki_chart_type = 'dx'


            title = song_details[0].find('a').text.strip()
            artist = song_details[1].text.strip()
            lev_bas = song_details[2].text.strip()
            lev_adv = song_details[3].text.strip()
            lev_exp = song_details[4].text.strip()
            lev_mas = song_details[5].text.strip()
            lev_remas = song_details[6].text.strip()

            # Add song to dictionary with date
            wiki_song = {
                'title': normalize_title(title),
                'artist': normalize_title(artist),
                'date': date,
                'lev_bas': lev_bas,
                'lev_adv': lev_adv,
                'lev_exp': lev_exp,
                'lev_mas': lev_mas,
                'lev_remas': lev_remas
            }

            # Set only_remas and is_update
            if (wiki_song['lev_bas'] == '-' and
                wiki_song['lev_adv'] == '-' and
                wiki_song['lev_exp'] == '-' and
                wiki_song['lev_mas'] == '-' and
                wiki_song['lev_remas'] != '-'):
                only_remas = True

            # If song needs unlock
            if 'Unlockable' in row.find_previous('th').text.strip():
                wiki_song['key_intl'] = True


        # Match wiki song with song from JP JSON file
        for song in local_music_ex_data:
            if utage_td:
                if 'kanji' in song and 'kanji' in wiki_song:
                    if (normalize_title(song['title']) == f'[{wiki_song['kanji']}]{wiki_song['title']}' and
                        normalize_title(song['artist']) == wiki_song['artist'] and
                        song['kanji'] == wiki_song['kanji']):

                        if ('lev_utage' in song and song['lev_utage'] == wiki_song['lev_utage'] or
                        'dx_lev_utage' in song and song['dx_lev_utage'] == wiki_song['lev_utage']):
                            matched_jp_song = song
                            matched_jp_old_song = copy.copy(song)
                            jp_song_matched = True
                            break
            else:
                # Match with title and artist
                if (normalize_title(song['title']) == wiki_song['title'] and normalize_title(song['artist']) == wiki_song['artist']):

                    # If wiki_chart_type is not explicitly set (single chart type)
                    # Get chart type from JSON song
                    if wiki_chart_type == '':
                        # Check chart type in json:
                        if 'lev_bas' in song:
                            wiki_chart_type == 'std'
                        elif 'dx_lev_bas' in song:
                            wiki_chart_type == 'dx'

                    if wiki_chart_type == 'std':
                        # if song only has remas added
                        if only_remas:
                            if song['lev_remas'] != wiki_song['lev_remas']:
                                lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                                if game.ARGS.strict:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['lev_remas']} vs Wiki: {wiki_song['lev_remas']})", bcolors.FAIL, log=True, is_verbose=True)
                                    continue
                                else:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['lev_remas']} vs Wiki: {wiki_song['lev_remas']})", bcolors.WARNING, log=True, is_verbose=True)

                        # Song has other charts added but levels mismatch
                        else:
                            if ((song['lev_bas'] != wiki_song['lev_bas'] or
                                song['lev_adv'] != wiki_song['lev_adv'] or
                                song['lev_exp'] != wiki_song['lev_exp'] or
                                song['lev_mas'] != wiki_song['lev_mas'])):

                                lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                                if game.ARGS.strict:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['lev_bas']}/{song['lev_adv']}/{song['lev_exp']}/{song['lev_mas']} vs Wiki: {wiki_song['lev_bas']}/{wiki_song['lev_adv']}/{wiki_song['lev_exp']}/{wiki_song['lev_mas']})", bcolors.FAIL, log=True, is_verbose=True)
                                    continue
                                else:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['lev_bas']}/{song['lev_adv']}/{song['lev_exp']}/{song['lev_mas']} vs Wiki: {wiki_song['lev_bas']}/{wiki_song['lev_adv']}/{wiki_song['lev_exp']}/{wiki_song['lev_mas']})", bcolors.WARNING, log=True, is_verbose=True)

                    elif wiki_chart_type == 'dx':
                        # if song only has remas added
                        if only_remas:
                            if song['dx_lev_remas'] != wiki_song['lev_remas']:
                                lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                                if game.ARGS.strict:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['dx_lev_remas']} vs Wiki: {wiki_song['dx_lev_remas']})", bcolors.FAIL, log=True, is_verbose=True)
                                    continue
                                else:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['dx_lev_remas']} vs Wiki: {wiki_song['dx_lev_remas']})", bcolors.WARNING, log=True, is_verbose=True)

                        # Song has other DX charts added but levels mismatch
                        else:
                            if ('dx_lev_bas' in song and
                                    ((song['dx_lev_bas'] != wiki_song['lev_bas'] or
                                    song['dx_lev_adv'] != wiki_song['lev_adv'] or
                                    song['dx_lev_exp'] != wiki_song['lev_exp'] or
                                    song['dx_lev_mas'] != wiki_song['lev_mas']))
                                ):

                                lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                                if game.ARGS.strict:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['dx_lev_bas']}/{song['dx_lev_adv']}/{song['dx_lev_exp']}/{song['dx_lev_mas']} vs Wiki: {wiki_song['dx_lev_bas']}/{wiki_song['dx_lev_adv']}/{wiki_song['dx_lev_exp']}/{wiki_song['dx_lev_mas']})", bcolors.FAIL, log=True, is_verbose=True)
                                    continue
                                else:
                                    print_message(f"- One of the levels were not matched. (JSON: {song['dx_lev_bas']}/{song['dx_lev_adv']}/{song['dx_lev_exp']}/{song['dx_lev_mas']} vs Wiki: {wiki_song['dx_lev_bas']}/{wiki_song['dx_lev_adv']}/{wiki_song['dx_lev_exp']}/{wiki_song['dx_lev_mas']})", bcolors.WARNING, log=True, is_verbose=True)

                    matched_jp_song = song
                    matched_jp_old_song = copy.copy(song)
                    jp_song_matched = True
                    break

        # Match wiki song with song from INTL JSON file
        for intl_song in local_intl_music_ex_data:
            # UTAGE
            if utage_td:
                if 'kanji' in intl_song and 'kanji' in wiki_song:
                    if (normalize_title(intl_song['title']) == f'[{wiki_song['kanji']}]{wiki_song['title']}' and
                        normalize_title(intl_song['artist']) == wiki_song['artist'] and
                        intl_song['kanji'] == wiki_song['kanji']):

                        if ('lev_utage' in intl_song and intl_song['lev_utage'] == wiki_song['lev_utage'] or
                        'dx_lev_utage' in intl_song and intl_song['dx_lev_utage'] == wiki_song['lev_utage']):
                            matched_intl_song = intl_song
                            matched_intl_old_song = copy.copy(intl_song)
                            jp_song_matched = True
                            break

            # else
            else:
                if (normalize_title(intl_song['title']) == wiki_song['title'] and normalize_title(song['artist']) == wiki_song['artist']):
                    matched_intl_song = intl_song
                    matched_intl_old_song = copy.copy(intl_song)
                    intl_song_matched = True
                    break

        # if utage_td and wiki_song['title'] == 'アンビバレンス':
        #     ipdb.set_trace()



        # If song is not yet in INTL data
        if jp_song_matched is True and intl_song_matched is False:
            if matched_jp_song['intl'] == '0':

                # Copy song from JP data
                local_intl_music_ex_data.append(matched_jp_song)
                matched_intl_song = local_intl_music_ex_data[-1]
                intl_song_matched = True
                matched_jp_song['intl'] = "1"
                matched_intl_song['intl'] = "1"

                if utage_td:
                    lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
                else:
                    lazy_print_song_header(f"{title}", header_printed, log=True)

                print_message(f"- Song copied from JP data to INTL", bcolors.OKGREEN)
                print_message(f"- Marked as available in Intl ver.", bcolors.OKGREEN, log=True)

        # If song is already in INTL data (most likely partially)
        elif jp_song_matched is True and intl_song_matched is True:
            if matched_jp_song['intl'] != '0':

                # copy missing keys to INTL from JP
                if wiki_chart_type == 'std':
                    if only_remas:
                        for key in [
                            'lev_remas',
                            'lev_remas_i',
                            'lev_remas_notes',
                            'lev_remas_notes_tap',
                            'lev_remas_notes_hold',
                            'lev_remas_notes_slide',
                            'lev_remas_notes_break',
                            'lev_remas_designer'
                        ]:
                            if key in matched_jp_song:
                                matched_intl_song[key] = matched_jp_song[key]

                        if matched_intl_old_song != matched_intl_song:
                            lazy_print_song_header(f"{title}", header_printed, log=True)
                            print_message(f"- Copied RE:MASTER (Std) chart from JP data to INTL", bcolors.OKGREEN, log=True)
                    else:
                        for key in [
                            'lev_bas',
                            'lev_bas_i',
                            'lev_bas_notes',
                            'lev_bas_notes_tap',
                            'lev_bas_notes_hold',
                            'lev_bas_notes_slide',
                            'lev_bas_notes_break',
                            'lev_bas_designer',
                            'lev_adv',
                            'lev_adv_i',
                            'lev_adv_notes',
                            'lev_adv_notes_tap',
                            'lev_adv_notes_hold',
                            'lev_adv_notes_slide',
                            'lev_adv_notes_break',
                            'lev_adv_designer',
                            'lev_exp',
                            'lev_exp_i',
                            'lev_exp_notes',
                            'lev_exp_notes_tap',
                            'lev_exp_notes_hold',
                            'lev_exp_notes_slide',
                            'lev_exp_notes_break',
                            'lev_exp_designer',
                            'lev_mas',
                            'lev_mas_i',
                            'lev_mas_notes',
                            'lev_mas_notes_tap',
                            'lev_mas_notes_hold',
                            'lev_mas_notes_slide',
                            'lev_mas_notes_break',
                            'lev_mas_designer',
                        ]:
                            if key in matched_jp_song:
                                matched_intl_song[key] = matched_jp_song[key]

                        if matched_intl_old_song != matched_intl_song:
                            lazy_print_song_header(f"{title}", header_printed, log=True)
                            print_message(f"- Copied Std charts from JP data to INTL", bcolors.OKGREEN, log=True)

                if wiki_chart_type == 'dx':
                    if only_remas:
                        for key in [
                            'dx_lev_remas',
                            'dx_lev_remas_i',
                            'dx_lev_remas_notes',
                            'dx_lev_remas_notes_tap',
                            'dx_lev_remas_notes_hold',
                            'dx_lev_remas_notes_slide',
                            'dx_lev_remas_notes_break',
                            'dx_lev_remas_designer'
                        ]:
                            if key in matched_jp_song:
                                matched_intl_song[key] = matched_jp_song[key]

                        if matched_intl_old_song != matched_intl_song:
                            lazy_print_song_header(f"{title}", header_printed, log=True)
                            print_message(f"- Copied RE:MASTER (DX) chart from JP data to INTL", bcolors.OKGREEN, log=True)
                    else:
                        for key in [
                            'dx_lev_bas',
                            'dx_lev_bas_i',
                            'dx_lev_bas_notes',
                            'dx_lev_bas_notes_tap',
                            'dx_lev_bas_notes_hold',
                            'dx_lev_bas_notes_slide',
                            'dx_lev_bas_notes_break',
                            'dx_lev_bas_designer',
                            'dx_lev_adv',
                            'dx_lev_adv_i',
                            'dx_lev_adv_notes',
                            'dx_lev_adv_notes_tap',
                            'dx_lev_adv_notes_hold',
                            'dx_lev_adv_notes_slide',
                            'dx_lev_adv_notes_break',
                            'dx_lev_adv_designer',
                            'dx_lev_exp',
                            'dx_lev_exp_i',
                            'dx_lev_exp_notes',
                            'dx_lev_exp_notes_tap',
                            'dx_lev_exp_notes_hold',
                            'dx_lev_exp_notes_slide',
                            'dx_lev_exp_notes_break',
                            'dx_lev_exp_designer',
                            'dx_lev_mas',
                            'dx_lev_mas_i',
                            'dx_lev_mas_notes',
                            'dx_lev_mas_notes_tap',
                            'dx_lev_mas_notes_hold',
                            'dx_lev_mas_notes_slide',
                            'dx_lev_mas_notes_break',
                            'dx_lev_mas_designer',
                        ]:
                            if key in matched_jp_song:
                                matched_intl_song[key] = matched_jp_song[key]

                        if matched_intl_old_song != matched_intl_song:
                            lazy_print_song_header(f"{title}", header_printed, log=True)
                            print_message(f"- Copied DX charts from JP data to INTL", bcolors.OKGREEN, log=True)

                    if 'date_intl_updated' not in matched_intl_song or int(wiki_song['date']) > int(song['date_intl_updated']):
                        matched_intl_song['date_intl_updated'] = wiki_song['date']
                        matched_jp_song['date_intl_updated'] = wiki_song['date']
                        print_message(f"- Added Intl updated date ({wiki_song['date']})", bcolors.OKBLUE, log=True)


        if intl_song_matched is True:
            if utage_td:
                if matched_jp_song['intl'] == '0':
                    matched_intl_song['intl'] = "1"
                    matched_jp_song['intl'] = "1"
                    lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
                    print_message(f"- Marked as available in Intl ver.", bcolors.OKGREEN, log=True)


                if ('date_intl_added' not in song or song['date_intl_added'] == '000000'):
                    matched_intl_song['date_intl_added'] = wiki_song['date']
                    matched_jp_song['date_intl_added'] = wiki_song['date']
                    lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
                    print_message(f"- Intl added date (UTAGE) ({wiki_song['date']})", bcolors.OKGREEN, log=True)
                else:
                    if 'date_intl_updated' not in song and int(wiki_song['date']) > int(song['date_intl_added']):
                        matched_intl_song['date_intl_updated'] = wiki_song['date']
                        matched_jp_song['date_intl_updated'] = wiki_song['date']
                        lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
                        print_message(f"- Intl updated date (UTAGE) ({wiki_song['date']})", bcolors.OKBLUE, log=True)

                    # If date from wiki is later than existing date, consider it as updated date
                    elif 'date_intl_updated' in song and int(wiki_song['date']) > int(song['date_intl_updated']):
                        matched_intl_song['date_intl_updated'] = wiki_song['date']
                        matched_jp_song['date_intl_updated'] = wiki_song['date']
                        lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
                        print_message(f"- Intl updated date (UTAGE) ({wiki_song['date']})", bcolors.OKBLUE, log=True)
            else:
                if ('date_intl_added' not in matched_jp_song or matched_jp_song['date_intl_added'] == '000000'):
                    matched_intl_song['date_intl_added'] = wiki_song['date']
                    matched_jp_song['date_intl_added'] = wiki_song['date']
                    lazy_print_song_header(f"{title}", header_printed, log=True)
                    print_message(f"- Added Intl added date ({wiki_song['date']})", bcolors.OKGREEN, log=True)
                else:
                    if 'date_intl_updated' not in matched_jp_song and int(wiki_song['date']) > int(matched_jp_song['date_intl_added']):
                        matched_intl_song['date_intl_updated'] = wiki_song['date']
                        matched_jp_song['date_intl_updated'] = wiki_song['date']
                        lazy_print_song_header(f"{title}", header_printed, log=True)
                        print_message(f"- Added Intl updated date ({wiki_song['date']})", bcolors.OKBLUE, log=True)

                    # If date from wiki is later than existing date, consider it as updated date
                    elif 'date_intl_updated' in matched_jp_song and int(wiki_song['date']) > int(matched_jp_song['date_intl_updated']):
                        matched_intl_song['date_intl_updated'] = wiki_song['date']
                        matched_jp_song['date_intl_updated'] = wiki_song['date']
                        lazy_print_song_header(f"{title}", header_printed, log=True)
                        print_message(f"- Added Intl updated date ({wiki_song['date']})", bcolors.OKBLUE, log=True)




        # Write unlockable
        if 'key_intl' in wiki_song and ('key_intl' not in matched_jp_song or matched_jp_song['key_intl'] == ''):
            matched_intl_song['key_intl'] = "○"
            matched_jp_song['key_intl'] = "○"

            lazy_print_song_header(f"{title}", header_printed, log=True)
            print_message(f"- Marked as unlockable in Intl ver", bcolors.OKBLUE, log=True)



        # if song['title'] == "One Step Ahead":
        #     ipdb.set_trace()

        if matched_intl_old_song is not None and matched_intl_old_song == matched_intl_song:
            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)
            print_message("- Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
        else:
            total_diffs[0] += 1


        # if song was not matched (if break was not triggered)
        if intl_song_matched is not True:
            if utage_td:
                lazy_print_song_header(f"[{kanji}] {title}", header_printed, log=True)
            else:
                lazy_print_song_header(f"{title}", header_printed, log=True)

            print_message(f"- Song not found in JSON file", bcolors.FAIL, log=True)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


    # sort before saving
    for song in local_intl_music_ex_data:
        sorted_song = sort_dict_keys(song)
        song.clear()
        song.update(sorted_song)

    # Write updated JSON data to file
    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_intl_music_ex_data, f, ensure_ascii=False, indent=2)

    # Write updated JSON data to file
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

