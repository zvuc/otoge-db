# import ipdb
import requests
import json
import copy
import random
import time
from shared.common_func import *
from ongeki.paths import *
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

TARGET_KEYS = [
    "bpm",
    "enemy_lv",
    "enemy_type",
    "_notes",
    "_designer"
]

# Update on top of existing music-ex
def update_songs_extra_data():
    print_message(f"Fetch latest wiki data", 'H2', log=True)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added', game.HASH_KEYS_EX)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    total_diffs = [0]

    for song in target_song_list:
        update_song_wiki_data(song, total_diffs)

        # Sort the song dictionary before saving
        sorted_song = sort_dict_keys(song)
        song.clear()  # Clear the original song dictionary
        song.update(sorted_song)

        with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def update_song_wiki_data(song, total_diffs):
    header_printed = [0]

    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
        .replace('"', '”')
        .replace('?', '？')
    )

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        if game.ARGS.noskip:
            # Check if any values are empty
            if any(value == "" for key, value in song.items() if any(target in key for target in TARGET_KEYS)) or game.ARGS.overwrite:
                url = song['wikiwiki_url']
                try:
                    wiki = requests.get(url, timeout=5, headers=request_headers, allow_redirects=True)
                    _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)
                    # Give some time before continuing
                    time.sleep(random.randint(1,2))
                    return
                except requests.RequestException as e:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                    print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True)
                    return song
            else:
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("(Skipping - all data already present)", bcolors.ENDC, log=True, is_verbose=True)
        else:
            # Skip if URL present
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("(Skipping - URL already exists)", bcolors.ENDC, log=True, is_verbose=True)

    # If not, guess URL from title
    else:
        guess_url = wiki_base_url + title
        wiki = requests.get(guess_url, timeout=5, headers=request_headers, allow_redirects=True)

        if not wiki.ok:
            # try replacing special character as fallback
            title = title.replace('\'', '’')
            guess_url = wiki_base_url + title
            wiki = requests.get(guess_url, timeout=5, headers=request_headers, allow_redirects=True)

            if not wiki.ok:
                # give up!
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                print_message("Failed to guess wiki page", bcolors.FAIL, log=True)
                return song

            else:
                url = guess_url
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Found URL by guess!", bcolors.OKBLUE, log=True, is_verbose=True)
                return _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)
                
        else:
            url = guess_url
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Found URL by guess!", bcolors.OKBLUE, log=True, is_verbose=True)
            return _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)


def _parse_wikiwiki(song, wiki, url, total_diffs, header_printed):
    critical_errors = [0]

    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', class_='tooltip'):
        footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Wiki page not found - invalid page", bcolors.FAIL, log=True)
        critical_errors[0] += 1
        return song

    # find the overview table
    overview_table = None
    
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            second_row_th = rows[1].find('th')
            if second_row_th and second_row_th.get_text(strip=True) == 'タイトル':
                img_in_first_col = rows[0].find('td',{'rowspan': True})
                if img_in_first_col:
                    overview_table = table
                    break

    if overview_table:
        overview_heads = overview_table.select('th')

        if song['lunatic'] == '1':
            overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]
        else:
            overview_data = [head.find_parent('tr').select('td:not([rowspan])') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text for data in overview_data]
        overview_dict = dict(zip(overview_heads, overview_data))

        # Find enemy lv data
        if 'LV.' in overview_dict["対戦相手"].upper():
            enemy_info = overview_dict["対戦相手"].upper().split("LV.")
            enemy_name = enemy_info[0]
            enemy_lv = enemy_info[1]

            if enemy_lv and not enemy_lv == '○':
                diff_count = [0]
                update_song_key(song, 'enemy_lv', enemy_lv, diff_count=diff_count)

                if diff_count[0] > 0:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                    print_message("Added Enemy Lv", bcolors.OKGREEN, log=True)


            # If character name includes type info, use it
            for enemy_type in game.ENEMY_TYPES:
                diff_count = [0]

                if enemy_type in enemy_name:
                    default_overwrite = game.ARGS.overwrite
                    game.ARGS.overwrite = True
                    update_song_key(song, 'enemy_type', enemy_type, diff_count=diff_count)

                    game.ARGS.overwrite = default_overwrite

                    if diff_count[0] > 0:
                        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                        print_message("Updated enemy type", bcolors.OKGREEN, log=True)
                        break

        else:
            # fail
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Warning - enemy lv not found", bcolors.WARNING, log=True, is_verbose=True)
            
    else:
        # fail
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - no overview table", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1


    # find the charts table
    charts_table = None
    for table in tables:
        th_elements = table.select('th:nth-of-type(1), th:nth-of-type(2)')
        if len(th_elements) > 2 and th_elements[0].get_text(strip=True) == '難易度' and th_elements[1].get_text(strip=True) == '楽曲Lv':
            charts_table = table
            break
    
    # Update chart details
    if charts_table:
        charts_table_head = [th.text for th in charts_table.select("thead th")]
        charts_data = [[cell.text for cell in chart.select("th,td")] for chart in charts_table.select("tbody tr")]

        if any(charts_table_head) and '難易度' in charts_table_head[0]:
            for chart_details in charts_data:
                chart_dict = dict(zip(charts_table_head, chart_details))

                if song['lunatic'] == '' and chart_dict['難易度'] == 'BASIC':
                    _update_song_chart_details(song, chart_dict, 'bas', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'ADVANCED':
                    _update_song_chart_details(song, chart_dict, 'adv', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'EXPERT':
                    _update_song_chart_details(song, chart_dict, 'exc', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'MASTER':
                    _update_song_chart_details(song, chart_dict, 'mas', header_printed)
                elif song['lunatic'] == '1' and chart_dict['難易度'] == 'LUNATIC':
                    _update_song_chart_details(song, chart_dict, 'lnt', header_printed)
        else:
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
            print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True)
            critical_errors[0] += 1
    else:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True)
        critical_errors[0] += 1
    
    # Update BPM
    if overview_dict['BPM']:
        diff_count = [0]
        update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

        if diff_count[0] > 0:
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
            print_message("Added BPM", bcolors.OKGREEN, log=True)

    if song['wikiwiki_url'] != url and critical_errors[0] == 0:
        song['wikiwiki_url'] = url
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Saved wiki URL", bcolors.OKBLUE)

    if old_song == song:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Done (Nothing updated)", bcolors.ENDC, log=True, is_verbose=True)
    else:
        total_diffs[0] += 1
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN)

    return song


def _update_song_chart_details(song, chart_dict, chart, header_printed):
    details_diff_count = [0]
    designer_diff_count = [0]
    update_song_key(song, f"lev_{chart}_notes", chart_dict["総ノート数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_bells", chart_dict["BELL"], remove_comma=True, diff_count=details_diff_count)
    # update_song_key(song, f"lev_{chart}_i", chart_dict["譜面定数"], diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN)

    update_song_key(song, f"lev_{chart}_designer", chart_dict["譜面製作者"], diff_count=designer_diff_count)

    if designer_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN)
