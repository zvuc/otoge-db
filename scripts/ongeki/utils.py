# import ipdb
import requests
import urllib.request
import json
from ongeki.paths import *
from ongeki import wiki
from shared.common_func import *

HASH_KEYS = ['title', 'artist', 'date', 'lunatic']
HASH_KEYS_EX = ['title', 'artist', 'date_added', 'lunatic']

CHARACTER_TABLE = {
    "星咲あかり": "FIRE",
    "藤沢柚子": "LEAF",
    "三角葵": "AQUA",
    "高瀬梨緒": "AQUA",
    "結城莉玖": "FIRE",
    "藍原椿": "LEAF",
    "桜井春菜": "FIRE",
    "早乙女彩華": "AQUA",
    "井之原小星": "LEAF",
    "柏木咲姫": "AQUA",
    "九條楓": "LEAF",
    "逢坂茜": "FIRE",
    "珠洲島有栖": "AQUA",
    "日向千夏": "LEAF",
    "柏木美亜": "FIRE",
    "東雲つむぎ": "AQUA",
    "皇城セツナ": "FIRE",
    "あかニャン": "FIRE",
    "みどニャン": "LEAF",
    "あおニャン": "AQUA"
}

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = json_to_hash_value_map(local_music_data, *HASH_KEYS)

    old_local_music_data = local_music_data

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = json_to_hash_value_map(server_music_data, *HASH_KEYS)

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
        lazy_print_song_header(f"{song['title']}", song_diffs, args, log=True)
        print_message(f"- New song added", bcolors.OKGREEN, args)

        _record_diffs(song, song_hash, 'new')

    # Iterate through updated songs
    # For the list of updated songs, go through each of them in older song list
    # Find the same song in ex_data list then update any changed keys
    for song in updated_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song, *HASH_KEYS)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS_EX) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, log=True)
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

            # Check for removed keys
            for key in old_song.copy():
                # maimai uses 'date' key for recording NEW markers... ignore them
                # if key == 'date':
                #     continue
                if key not in song:
                    del dest_ex_song[key]


            if not detect_key_removals_or_modifications(song, old_song, song_diffs):
                # all other cases where something changed
                lazy_print_song_header(f"{song['title']}", song_diffs, args, log=True)
                print_message(f"- Updated existing song", bcolors.OKGREEN, args)

            _record_diffs(song, song_hash, 'updated')


    # Iterate through unchanged songs
    for song in unchanged_songs:
        song_diffs = [0]
        song_hash = generate_hash_from_keys(song, *HASH_KEYS)
        old_song = next((s for s in old_local_music_data if generate_hash_from_keys(s, *HASH_KEYS) == song_hash), None)
        dest_ex_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS_EX) == song_hash), None)

        # Song can't be found in music-ex.json
        if not dest_ex_song:
            lazy_print_song_header(f"{song['title']}", song_diffs, args, log=True)
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
            existing_song = next((s for s in local_music_ex_data if generate_hash_from_keys(s, *HASH_KEYS_EX) == song_hash), None)

            if existing_song:
                # delete matched item
                local_music_ex_data.remove(existing_song)
                archive_deleted_song(existing_song, local_music_ex_deleted_data)

                lazy_print_song_header(f"{song['title']}", song_diffs, args, log=True)
                print_message(f"- Removed song", bcolors.OKBLUE, args)

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
    urllib.request.urlretrieve(SERVER_MUSIC_JACKET_BASE_URL + song['image_url'], 'ongeki/jacket/' + song['image_url'])

def _record_diffs(song, song_hash, diff_type):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song_hash + '\n')


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_ex_data_template(song))

def _add_ex_data_template(song):
    song['enemy_lv'] = ""
    song['enemy_type'] = CHARACTER_TABLE.get(song['character'].replace(' ', ''), '')
    song['bpm'] = ""
    song['lev_bas_i'] = ""
    song['lev_bas_notes'] = ""
    song['lev_bas_bells'] = ""
    song['lev_bas_designer'] = ""
    song['lev_adv_i'] = ""
    song['lev_adv_notes'] = ""
    song['lev_adv_bells'] = ""
    song['lev_adv_designer'] = ""
    song['lev_adv_chart_link'] = ""
    song['lev_exc_i'] = ""
    song['lev_exc_notes'] = ""
    song['lev_exc_bells'] = ""
    song['lev_exc_designer'] = ""
    song['lev_exc_chart_link'] = ""
    song['lev_mas_i'] = ""
    song['lev_mas_notes'] = ""
    song['lev_mas_bells'] = ""
    song['lev_mas_designer'] = ""
    song['lev_mas_chart_link'] = ""
    song['lev_lnt_i'] = ""
    song['lev_lnt_notes'] = ""
    song['lev_lnt_bells'] = ""
    song['lev_lnt_designer'] = ""
    song['lev_lnt_chart_link'] = ""
    song['version'] = "bright MEMORY Act.3"
    song['wikiwiki_url'] = ""

    # Rename 'date' key to 'date_added' if it exists
    if 'date' in song:
        song['date_added'] = song['date']
        del song['date']

    return song

