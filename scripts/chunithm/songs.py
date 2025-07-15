# import ipdb
import requests
import urllib.request
import json
import copy
from chunithm.paths import *
from chunithm import wiki
from shared.common_func import *
from datetime import datetime

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = json_to_hash_value_map(local_music_data)

    old_local_music_data = copy.deepcopy(local_music_data)

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = json_to_hash_value_map(server_music_data)

    added_songs = []
    removed_songs = []
    
    # Compare sets of IDs to identify added and removed songs
    added_ids = set(server_music_map.keys()) - set(local_music_map.keys())
    removed_ids = set(local_music_map.keys()) - set(server_music_map.keys())

    if added_ids:
        with open(LOCAL_MUSIC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(server_music_data, f, ensure_ascii=False, indent=2)

        added_songs = [server_music_map[id] for id in added_ids]

    removed_songs = [local_music_map[id] for id in removed_ids]

    updated_songs = []
    unchanged_songs = []
    for id, server_song in server_music_map.items():
        if id in local_music_map:
            local_song = local_music_map[id]
            if server_song != local_song:
                # Song has been updated, include it in the updated_songs list
                updated_songs.append(server_song)
            else:
                unchanged_songs.append(server_song)
    
    return added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data




def renew_music_ex_data(added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data):
    print_message(f"Fetch new songs", 'H2')

    if len(added_songs) == 0 and len(updated_songs) == 0:
        print_message("Nothing updated", '')
        return

    f = open(LOCAL_DIFFS_LOG_PATH, 'w')

    try:
        with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
            local_music_ex_data = json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create it
        local_music_ex_data = []
        with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_data, f)

    if game.ARGS.markdown:
        print_message(f"Newly added songs", 'H3')
        print_message(f"|Jacket|Song|")
        print_message(f"|--|--|")

    # added_songs
    for song in added_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        _download_song_jacket(song)
        _add_song_data_to_ex_data(song, local_music_ex_data)

        if game.ARGS.markdown:
            print_message(f"|<img src=\"https://github.com/zvuc/otoge-db/blob/chunithm-staging/chunithm/jacket/{song['image']}?raw=true\" width=\"120\">|**{song['title']}**<br>{song['artist']}|")
        else:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- New song added", bcolors.OKGREEN)

        _record_diffs(song, song_hash, 'new')


    if game.ARGS.markdown:
        print_message(f"Updated Songs", 'H3')

    # Iterate through updated songs
    # For the list of updated songs, go through each of them in older song list
    # Find the same song in ex_data list then update any changed keys
    for song in updated_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- Couldn't find matching song in music-ex.json", bcolors.WARNING)
            continue

        if old_song == song:
            continue

        if old_song and dest_ex_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in old_song or old_song[key] != value:
                    dest_ex_song[key] = value

                    if key == 'lev_ult':
                        dest_ex_song['lev_ult_i'] = ""
                        dest_ex_song['lev_ult_notes'] = ""
                        dest_ex_song['lev_ult_notes_tap'] = ""
                        dest_ex_song['lev_ult_notes_hold'] = ""
                        dest_ex_song['lev_ult_notes_slide'] = ""
                        dest_ex_song['lev_ult_notes_air'] = ""
                        dest_ex_song['lev_ult_notes_flick'] = ""
                        dest_ex_song['lev_ult_designer'] = ""
                        dest_ex_song['lev_ult_chart_link'] = ""

                        lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                        song_diffs[0] += 1
                        dest_ex_song['date_updated'] = f"{datetime.now().strftime('%Y%m%d')}"
                        print_message(f"- ULTIMA chart added", bcolors.OKGREEN)

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in song:
                    del dest_ex_song[key]

            if not detect_key_removals_or_modifications(song, old_song, song_diffs):
                # all other cases where something changed
                lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                print_message(f"- Updated data", bcolors.OKGREEN)

            _record_diffs(song, song_hash, 'updated')
        else:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- Couldn't find destination song", bcolors.FAIL)

    # Iterate through unchanged songs
    for song in unchanged_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
            print_message(f"- Couldn't find destination song", bcolors.WARNING)
            continue

        if old_song and dest_ex_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in old_song or old_song[key] != value:
                    dest_ex_song[key] = value

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in song:
                    del dest_ex_song[key]

    if len(removed_songs) != 0:
        try:
            with open(LOCAL_MUSIC_EX_DELETED_JSON_PATH, 'r', encoding='utf-8') as f:
                local_music_ex_deleted_data = json.load(f)
        except FileNotFoundError:
            # If the file doesn't exist, create it
            local_music_ex_deleted_data = []
            with open(LOCAL_MUSIC_EX_DELETED_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(local_music_ex_deleted_data, f)

        if game.ARGS.markdown:
            print_message(f"Removed Songs", 'H3')

        # removed_songs
        for song in removed_songs:
            song_diffs = [0]
            song_hash = generate_hash_from_keys(song)
            existing_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

            if existing_song:
                # delete matched item
                # ipdb.set_trace()
                local_music_ex_data.remove(existing_song)
                archive_deleted_song(existing_song, local_music_ex_deleted_data)

                if song['we_kanji'] == "":
                    lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                    print_message(f"- Removed song", bcolors.OKBLUE)
                else:
                    lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                    print_message(f"- Removed song (WE)[{song['we_kanji']}]", bcolors.OKBLUE)

        sort_and_save_json(local_music_ex_deleted_data, LOCAL_MUSIC_EX_DELETED_JSON_PATH)

    sort_and_save_json(local_music_ex_data, LOCAL_MUSIC_EX_JSON_PATH)



def _download_song_jacket(song):
    urllib.request.urlretrieve(SERVER_MUSIC_JACKET_BASE_URL + song['image'], 'chunithm/jacket/' + song['image'])

def _record_diffs(song, song_hash, diff_type):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song_hash + '\n')


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_ex_data_template(song))

def _add_ex_data_template(song):
    song['bpm'] = ""

    if song['we_kanji'] == "":
        song['lev_bas_i'] = ""
        song['lev_bas_notes'] = ""
        song['lev_bas_notes_tap'] = ""
        song['lev_bas_notes_hold'] = ""
        song['lev_bas_notes_slide'] = ""
        song['lev_bas_notes_air'] = ""
        song['lev_bas_notes_flick'] = ""

        song['lev_adv_i'] = ""
        song['lev_adv_notes'] = ""
        song['lev_adv_notes_tap'] = ""
        song['lev_adv_notes_hold'] = ""
        song['lev_adv_notes_slide'] = ""
        song['lev_adv_notes_air'] = ""
        song['lev_adv_notes_flick'] = ""

        song['lev_exp_i'] = ""
        song['lev_exp_notes'] = ""
        song['lev_exp_notes_tap'] = ""
        song['lev_exp_notes_hold'] = ""
        song['lev_exp_notes_slide'] = ""
        song['lev_exp_notes_air'] = ""
        song['lev_exp_notes_flick'] = ""
        song['lev_exp_designer'] = ""
        song['lev_exp_chart_link'] = ""

        song['lev_mas_i'] = ""
        song['lev_mas_notes'] = ""
        song['lev_mas_notes_tap'] = ""
        song['lev_mas_notes_hold'] = ""
        song['lev_mas_notes_slide'] = ""
        song['lev_mas_notes_air'] = ""
        song['lev_mas_notes_flick'] = ""
        song['lev_mas_designer'] = ""
        song['lev_mas_chart_link'] = ""

    if song['lev_ult'] != "":
        song['lev_ult_i'] = ""
        song['lev_ult_notes'] = ""
        song['lev_ult_notes_tap'] = ""
        song['lev_ult_notes_hold'] = ""
        song['lev_ult_notes_slide'] = ""
        song['lev_ult_notes_air'] = ""
        song['lev_ult_notes_flick'] = ""
        song['lev_ult_designer'] = ""
        song['lev_ult_chart_link'] = ""

    if song['we_kanji'] != "":
        song['lev_we_notes'] = ""
        song['lev_we_notes_tap'] = ""
        song['lev_we_notes_hold'] = ""
        song['lev_we_notes_slide'] = ""
        song['lev_we_notes_air'] = ""
        song['lev_we_notes_flick'] = ""
        song['lev_we_designer'] = ""
        song['lev_we_chart_link'] = ""

    song['version'] = game.CURRENT_JP_VER
    song['wikiwiki_url'] = ""
    song['intl'] = "0"
    song['date_added'] = f"{datetime.now().strftime('%Y%m%d')}"

    return song

