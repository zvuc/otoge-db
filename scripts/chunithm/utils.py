# import ipdb
import requests
import urllib.request
import json
from chunithm.paths import *
from chunithm import wiki
from shared.common_func import *
from datetime import datetime

HASH_KEYS = ['title', 'artist', 'we_kanji']

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = json_to_hash_value_map(local_music_data, generate_hash_from_keys, *HASH_KEYS)

    old_local_music_data = local_music_data

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = json_to_hash_value_map(server_music_data, generate_hash_from_keys, *HASH_KEYS)

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




def renew_music_ex_data(added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data, args):
    print_message(f"Fetch new songs", 'H2', args)

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
        song_hash = generate_hash_from_keys(song, *HASH_KEYS)
        _download_song_jacket(song)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
        print_message(f"- New song added", bcolors.OKGREEN, args)

        _record_diffs(song, song_hash, 'new')

    # Iterate through updated songs
    # For the list of updated songs, go through each of them in older song list
    # Find the same song in ex_data list then update any changed keys
    for song in updated_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song, *HASH_KEYS)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)

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
                # if key == 'date':
                #     continue
                if key not in old_song or old_song[key] != value:
                    dest_ex_song[key] = value

                    if key == 'lev_ult':
                        song_diffs[0] += 1
                        dest_ex_song['date_updated'] = f"{datetime.now().strftime('%Y%m%d')}"
                        lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                        print_message(f"- ULTIMA chart added", bcolors.OKGREEN, args)

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in song:
                    del dest_ex_song[key]

            if not detect_key_removals_or_modifications(song, old_song, song_diffs, args):
                # all other cases where something changed
                lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                print_message(f"- Updated data", bcolors.OKGREEN, args)

            _record_diffs(song, song_hash, 'updated')
        else:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
            print_message(f"- Couldn't find destination song", bcolors.FAIL, args)

    # Iterate through unchanged songs
    for song in unchanged_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song, *HASH_KEYS)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
            print_message(f"- Couldn't find destination song", bcolors.WARNING, args)
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

        # removed_songs
        for song in removed_songs:
            song_diffs = [0]
            song_hash = generate_hash_from_keys(song, *HASH_KEYS)
            existing_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)

            if existing_song:
                # delete matched item
                # ipdb.set_trace()
                local_music_ex_data.remove(existing_song)
                archive_deleted_song(existing_song, local_music_ex_deleted_data)

                if song['we_kanji'] == "":
                    lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                    print_message(f"- Removed song", bcolors.OKBLUE, args)
                else:
                    lazy_print_song_header(f"{song['title']}", song_diffs, args, errors_log, always_print=True)
                    print_message(f"- Removed song (WE)[{song['we_kanji']}]", bcolors.OKBLUE, args)


        with open(LOCAL_MUSIC_EX_DELETED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_deleted_data, f, ensure_ascii=False, indent=2)

    if not args.skipwiki:
        for song in added_songs:
            wiki.update_song_wiki_data(song, args)
        for song in updated_songs:
            wiki.update_song_wiki_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)



def _download_song_jacket(song):
    urllib.request.urlretrieve(SERVER_MUSIC_JACKET_BASE_URL + song['image'], 'chunithm/jacket/' + song['image'])

def _record_diffs(song, song_hash, diff_type):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song_hash + '\n')


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_ex_data_template(song))

def _add_ex_data_template(song):
    song['bpm'] = ""
    song['lev_bas_i'] = ""
    song['lev_bas_notes'] = ""
    song['lev_bas_notes_tap'] = ""
    song['lev_bas_notes_hold'] = ""
    song['lev_bas_notes_slide'] = ""
    song['lev_bas_notes_air'] = ""
    song['lev_bas_notes_flick'] = ""
    song['lev_bas_designer'] = ""
    song['lev_bas_chart_link'] = ""
    song['lev_adv_i'] = ""
    song['lev_adv_notes'] = ""
    song['lev_adv_notes_tap'] = ""
    song['lev_adv_notes_hold'] = ""
    song['lev_adv_notes_slide'] = ""
    song['lev_adv_notes_air'] = ""
    song['lev_adv_notes_flick'] = ""
    song['lev_adv_designer'] = ""
    song['lev_adv_chart_link'] = ""
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
    song['lev_ult_i'] = ""
    song['lev_ult_notes'] = ""
    song['lev_ult_notes_tap'] = ""
    song['lev_ult_notes_hold'] = ""
    song['lev_ult_notes_slide'] = ""
    song['lev_ult_notes_air'] = ""
    song['lev_ult_notes_flick'] = ""
    song['lev_ult_designer'] = ""
    song['lev_ult_chart_link'] = ""
    song['lev_we_notes'] = ""
    song['lev_we_notes_tap'] = ""
    song['lev_we_notes_hold'] = ""
    song['lev_we_notes_slide'] = ""
    song['lev_we_notes_air'] = ""
    song['lev_we_notes_flick'] = ""
    song['lev_we_designer'] = ""
    song['lev_we_chart_link'] = ""
    song['version'] = "LUMINOUS+"
    song['wikiwiki_url'] = ""
    song['date_added'] = f"{datetime.now().strftime('%Y%m%d')}"
    song['intl'] = "0"

    return song

def print_keys_change(song, old_song, song_diffs, args):
    # Define the possible level keys (both normal and dx versions)
    level_keys = {
        "lev_bas",
        "lev_adv",
        "lev_exp",
        "lev_mas",
        "lev_ult"
    }

    other_keys = {
        "artist",
        "catname",
        "newflag",
        "image",
        "release",
        "title",
        "reading"
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
