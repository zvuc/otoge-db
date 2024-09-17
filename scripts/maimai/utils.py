# import ipdb
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import ipdb
import requests
import urllib.request
import urllib3
import json
import os
import shutil
from maimai.paths import *
from maimai import wiki
from shared.common_func import *
from datetime import datetime

errors_log = LOCAL_ERROR_LOG_PATH

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
    local_music_map = json_to_hash_value_map(local_music_data)

    old_local_music_data = local_music_data

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
            # Remove the "sort" key from both server_song and local_song
            server_song_without_sort = {k: v for k, v in server_song.items() if k != "sort"}
            local_song_without_sort = {k: v for k, v in local_song.items() if k != "sort"}

            if server_song_without_sort != local_song_without_sort:
                # Song has been updated (excluding the "sort" key), include it in the updated_songs list
                updated_songs.append(server_song)
            else:
                # Maimai always updates the "sort" value so let's keep it updated...
                unchanged_songs.append(server_song)
    
    return added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data


def renew_music_ex_data(added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data, args):
    print_message(f"Fetch new songs", 'H2')

    if len(added_songs) == 0 and len(updated_songs) == 0:
        print_message("Nothing updated", '', args)
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

    # added_songs
    for song in added_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
        print_message(f"- New song added", bcolors.OKGREEN, args)
        _download_song_jacket(song, args)
        _add_song_data_to_ex_data(song, local_music_ex_data)

        _record_diffs(song, song_hash, 'new')

    # Iterate through updated songs
    # For the list of updated songs, go through each of them in older song list
    # Find the same song in ex_data list then update any changed keys
    for song in updated_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

        added_charts_sets = {
            "added_charts_dx": {"dx_lev_bas", "dx_lev_adv", "dx_lev_exp", "dx_lev_mas"},
            "added_charts": {"lev_bas", "lev_adv", "lev_exp", "lev_mas"},
            "added_charts_dx_remas": {"dx_lev_remas"},
            "added_charts_remas": {"lev_remas"}
        }

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
            print_message(f"- Couldn't find matching song in music-ex.json", bcolors.WARNING, args)
            continue

        if old_song == song:
            continue

        if old_song and dest_ex_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
                if key not in old_song or old_song[key] != value:
                    dest_ex_song[key] = value

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
                if key not in song:
                    del dest_ex_song[key]

            # Check if new charts have been added
            new_added_keys = set(song.keys()) - set(old_song.keys())


            # Check which set is a subset of new_added_keys
            matching_set_name = next(
                (name for name, chart_set in added_charts_sets.items() if chart_set.issubset(new_added_keys)),
                None
            )

            if matching_set_name:
                dest_ex_song['date_updated'] = f"{datetime.now().strftime('%Y%m%d')}"
                lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)

                if matching_set_name == "added_charts_dx":
                    print_message(f"- DX charts added", bcolors.OKGREEN, args)
                elif matching_set_name == "added_charts":
                    print_message(f"- STD charts added", bcolors.OKGREEN, args)
                elif matching_set_name == "added_charts_dx_remas":
                    print_message(f"- RE:MASTER (DX) chart added", bcolors.OKGREEN, args)
                elif matching_set_name == "added_charts_remas":
                    print_message(f"- RE:MASTER (STD) chart added", bcolors.OKGREEN, args)
            else:
                if not detect_key_removals_or_modifications(song, old_song, song_diffs, args):
                    # all other cases where something changed
                    lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                    print_message(f"- Updated data", bcolors.OKGREEN, args)

            _record_diffs(song, song_hash, 'updated')


    # Iterate through unchanged songs
    for song in unchanged_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
            print_message(f"- Couldn't find matching song in music-ex.json", bcolors.WARNING, args)
            continue

        if old_song and dest_ex_song:
            # Check for changes, additions, or removals
            for key, value in song.items():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
                if key not in old_song or old_song[key] != value:
                    dest_ex_song[key] = value

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                if key == 'date':
                    continue
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

        # removed_songs
        for song in removed_songs:
            song_diffs = [0]
            song_hash = generate_hash_from_keys(song)
            existing_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s) == song_hash), None)

            if existing_song:
                # delete matched item
                local_music_ex_data.remove(existing_song)
                archive_deleted_song(existing_song, local_music_ex_deleted_data)

                lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                print_message(f"- Removed song", bcolors.FAIL, args)

        with open(LOCAL_MUSIC_EX_DELETED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_deleted_data, f, ensure_ascii=False, indent=2)

    if not args.skipwiki:
        for song in added_songs:
            wiki.update_song_wiki_data(song, args)
        for song in updated_songs:
            wiki.update_song_wiki_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song, args):
    try:
        response = requests.get(SERVER_MUSIC_JACKET_BASE_URL + song['image_url'], verify=False, stream=True)

        if response.status_code == 200:
            filename = os.path.join('maimai/jacket', song['image_url'])
            with open(filename, 'wb') as file:
                response.raw.decode_content = True
                # file.write(response.content)
                shutil.copyfileobj(response.raw, file)

            print_message(f"- Jacket downloaded: {filename}", bcolors.ENDC, args, errors_log)
        else:
            print_message(f"- Failed to download image. Status code: {response.status_code}", bcolors.FAIL, args, errors_log)
    except Exception as e:
        print_message(f"- Could not download: {e}", bcolors.FAIL, args, errors_log)

def _record_diffs(song, song_hash, diff_type):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song_hash + '\n')


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_ex_data_template(song))

def _add_ex_data_template(song):
    song['bpm'] = ""

    levels = ['bas', 'adv', 'exp', 'mas', 'remas']

    for level in levels:
        if f'lev_{level}' in song:
            # song[f'lev_{level}_i'] = ""
            song[f'lev_{level}_notes'] = ""
            song[f'lev_{level}_notes_tap'] = ""
            song[f'lev_{level}_notes_hold'] = ""
            song[f'lev_{level}_notes_slide'] = ""
            # song[f'lev_{level}_notes_touch'] = ""
            song[f'lev_{level}_notes_break'] = ""

            if level not in ['bas', 'adv']:
                song[f'lev_{level}_i'] = ""
                song[f'lev_{level}_designer'] = ""
                # song[f'lev_{level}_chart_link'] = ""

        if f'dx_lev_{level}' in song:
            song[f'dx_lev_{level}_i'] = ""
            song[f'dx_lev_{level}_notes'] = ""
            song[f'dx_lev_{level}_notes_tap'] = ""
            song[f'dx_lev_{level}_notes_hold'] = ""
            song[f'dx_lev_{level}_notes_slide'] = ""
            song[f'dx_lev_{level}_notes_touch'] = ""
            song[f'dx_lev_{level}_notes_break'] = ""

            if level not in ['bas', 'adv']:
                song[f'dx_lev_{level}_designer'] = ""
                # song[f'dx_lev_{level}_chart_link'] = ""

    if 'kanji' in song:
        if 'buddy' in song:
            song['lev_utage_left_notes'] = ""
            song['lev_utage_left_notes_tap'] = ""
            song['lev_utage_left_notes_hold'] = ""
            song['lev_utage_left_notes_slide'] = ""
            song['lev_utage_left_notes_touch'] = ""
            song['lev_utage_left_notes_break'] = ""
            song['lev_utage_right_notes'] = ""
            song['lev_utage_right_notes_tap'] = ""
            song['lev_utage_right_notes_hold'] = ""
            song['lev_utage_right_notes_slide'] = ""
            song['lev_utage_right_notes_touch'] = ""
            song['lev_utage_right_notes_break'] = ""
        else:
            song['lev_utage_notes'] = ""
            song['lev_utage_notes_tap'] = ""
            song['lev_utage_notes_hold'] = ""
            song['lev_utage_notes_slide'] = ""
            song['lev_utage_notes_touch'] = ""
            song['lev_utage_notes_break'] = ""

        song['lev_utage_designer'] = song['comment']

    # song['version_name'] = ""
    song['wiki_url'] = ""

    if 'release' in song and song['release'] != '000000':
        song['date_added'] = f"{parse_date('',song['release']).strftime('%Y%m%d')}"
    else:
        song['date_added'] = f"{datetime.now().strftime('%Y%m%d')}"

    song['intl'] = "0"
    song['date_intl_added'] = "000000"

    return song

def print_keys_change(song, old_song, song_diffs, args):
    # Define the possible level keys (both normal and dx versions)
    level_keys = {"lev_bas", "lev_adv", "lev_exp", "lev_mas", "lev_remas",
                  "dx_lev_bas", "dx_lev_adv", "dx_lev_exp", "dx_lev_mas", "dx_lev_remas"}

    other_keys = {
        "artist",
        "catcode",
        "date",
        "kanji",
        "comment",
        "image_url",
        "key",
        "release",
        "title",
        "title_kana",
        "version"
    }

    any_changes = False

    # Iterate over each key in level_keys
    for key in level_keys:
        # Check if the key exists in both song and old_song
        if key in song and key in old_song:
            # Compare the values of the key in both dictionaries
            if song[key] != old_song[key]:
                # Print the difference in the format: key: old_value -> new_value

                # Lazy-print song name
                lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)

                print_message(f"- Level changed! {key}: {old_song[key]} → {song[key]}", bcolors.OKBLUE, args)
                any_changes = True

    for key in other_keys:
        # Check if the key exists in both song and old_song
        if key in song and key in old_song:
            # Compare the values of the key in both dictionaries
            if song[key] != old_song[key]:
                # Print the difference in the format: key: old_value -> new_value

                # Lazy-print song name
                lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)

                print_message(f"- {key}: {old_song[key]} → {song[key]}", bcolors.ENDC, args)
                any_changes = True

    return any_changes

# Check for keys that are removed or modified and print the changes.
def detect_key_removals_or_modifications(song, old_song, song_diffs, args):
    keys_removed = False

    # Check for key removal (keys in old_song but not in song)
    for key in old_song:
        if key == "date":
            continue
        if key not in song:
            # Most likely, "key" (unlock status) is removed
            # Lazy-print song name
            lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)

            print_message(f"- Song is now unlocked by default", bcolors.OKGREEN, args)
            keys_removed = True

    # Check for key modification
    keys_changed = print_keys_change(song, old_song, song_diffs, args)

    # Return True if any keys are removed or modified
    return keys_changed or keys_removed
