# import ipdb
import requests
import urllib.request
import json
from chunithm.paths import *
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
    for id, server_song in server_music_map.items():
        if id in local_music_map:
            local_song = local_music_map[id]
            if server_song != local_song:
                # Song has been updated, include it in the updated_songs list
                updated_songs.append(server_song)
    
    return added_songs, updated_songs, removed_songs


def _json_to_id_value_map(json):
    return {int(song['id']):song for song in json}


def renew_music_ex_data(new_song_list, args):
    if len(new_song_list[0]) == 0 and len(new_song_list[1]) == 0:
        print_message("Nothing updated", '', args)
        return

    f = open(LOCAL_DIFFS_LOG_PATH, 'w')

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Add new songs
    for song in new_song_list[0]:
        _download_song_jacket(song)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        print_message(f"New song added: {song['title']}", bcolors.OKGREEN, args)

        if not args.skipwiki:
            _update_song_wiki_data(song, args)
            
        _record_diffs(song, 'new')

    # Update existing songs
    for song in new_song_list[1]:
        # Find the existing song in local_music_ex_data by ID
        existing_song = next((s for s in local_music_ex_data if s['id'] == song['id']), None)

        if existing_song:
            # Update only the keys that have changed
            for key, value in song.items():
                if existing_song.get(key) != value:
                    existing_song[key] = value

            print_message(f"Updated existing song: {song['title']}", bcolors.OKGREEN, args)
            
            if not args.skipwiki:
                _update_song_wiki_data(song, args)
            
            _record_diffs(song, 'updated')

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song):
    urllib.request.urlretrieve(SERVER_MUSIC_JACKET_BASE_URL + song['image'], 'chunithm/jacket/' + song['image'])

def _record_diffs(song, diff_type):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song['id'] + song['image'] + '\n')


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
    song['version'] = ""
    song['wikiwiki_url'] = ""
    song['date'] = ""

    return song
