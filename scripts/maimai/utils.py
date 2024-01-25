import ipdb
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import requests
import urllib.request
import json
import os
import shutil
from maimai.paths import *
from maimai import wiki
from shared.common_func import *

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = _json_to_id_value_map(local_music_data)

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = _json_to_id_value_map(server_music_data)

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
    
    return added_songs, updated_songs, unchanged_songs, removed_songs


def _json_to_id_value_map(json):
    return {_maimai_generate_hash(song):song for song in json}

def _maimai_generate_hash(song):
    if 'lev_utage' in song:
        return generate_hash(song['title'] + song['lev_utage'] + song['comment'])
    else:
        return generate_hash(song['title'] + song['image_url'])

def renew_music_ex_data(new_song_list, args):
    if len(new_song_list[0]) == 0 and len(new_song_list[1]) == 0:
        print_message("Nothing updated", '', args)
        return

    f = open(LOCAL_DIFFS_LOG_PATH, 'w')

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # added_songs
    for song in new_song_list[0]:
        song_hash = _maimai_generate_hash(song)
        _download_song_jacket(song)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        print_message(f"New song added: {song['title']}", bcolors.OKGREEN, args)

        _record_diffs(song, song_hash, 'new')

    # updated_songs
    for song in new_song_list[1]:
        song_hash = _maimai_generate_hash(song)
        existing_song = next((s for s in local_music_ex_data if _maimai_generate_hash(song) == song_hash), None)

        if existing_song:
            # Update only the keys that have changed
            for key, value in song.items():
                if existing_song.get(key) != value:
                    existing_song[key] = value

            print_message(f"Updated existing song: {song['title']}", bcolors.OKGREEN, args)
            
            _record_diffs(song, song_hash, 'updated')

    # unchanged_songs
    for song in new_song_list[2]:
        song_hash = _maimai_generate_hash(song)
        existing_song = next((s for s in local_music_ex_data if _maimai_generate_hash(song) == song_hash), None)

        if existing_song:
            # Update only the keys that have changed
            for key, value in song.items():
                if existing_song.get(key) != value:
                    existing_song[key] = value
            

    if not args.skipwiki:
        for song in new_song_list[0]:
            wiki.update_song_wiki_data(song, args)
        for song in new_song_list[1]:
            wiki.update_song_wiki_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song):
    # ipdb.set_trace();
    try:
        response = requests.get(SERVER_MUSIC_JACKET_BASE_URL + song['image_url'], verify=False, stream=True)

        if response.status_code == 200:
            filename = os.path.join('maimai/jacket', song['image_url'])
            with open(filename, 'wb') as file:
                response.raw.decode_content = True
                # file.write(response.content)
                shutil.copyfileobj(response.raw, file)

            print(f"Image downloaded successfully and saved as {filename}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Could not download: {e}")

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

        song['lev_utage_notes_designer'] = ""

    # song['version_name'] = ""
    song['wiki_url'] = ""
    song['date'] = ""

    return song
