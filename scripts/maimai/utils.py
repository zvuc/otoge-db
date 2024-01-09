import ipdb
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import requests
import urllib.request
import json
import os
import shutil
from maimai.paths import *
from shared.common_func import *

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = _json_to_id_value_map(local_music_data)

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = _json_to_id_value_map(server_music_data)

    if len(server_music_map) > len(local_music_map):
        with open(LOCAL_MUSIC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(server_music_data, f, ensure_ascii=False, indent=2)

    return [server_music_map[sort] for sort in server_music_map if sort not in local_music_map]


def _json_to_id_value_map(json):
    return {int(song['sort']):song for song in json}


def renew_music_ex_data(new_song_list, args):
    if len(new_song_list) == 0:
        print_message("Nothing updated", '', args)
        return

    f = open("diffs.txt", 'w')

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    for song in new_song_list:
        _download_song_jacket(song)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        print_message(f"New song added: {song['title']}", bcolors.OKGREEN, args)
        
        if not args.skipwiki:
            _update_song_wiki_data(song, args)
            
        _record_new_song_jacket_id(song)

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

def _record_new_song_jacket_id(song):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write('jacket/' + song['image_url'] + '\n')


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
        song['lev_utage_notes'] = ""
        song['lev_utage_notes_tap'] = ""
        song['lev_utage_notes_hold'] = ""
        song['lev_utage_notes_slide'] = ""
        song['lev_utage_notes_touch'] = ""
        song['lev_utage_notes_break'] = ""

    # song['version_name'] = ""
    song['wiki_url'] = ""
    song['date'] = ""

    return song
