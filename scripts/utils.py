import requests
import urllib.request
import json
import re
from datetime import datetime
from functools import reduce

def load_new_song_data(local_music_json_path, server_music_json_path):
    with open(local_music_json_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = _json_to_id_value_map(local_music_data)

    server_music_data = requests.get(server_music_json_path).json()
    server_music_map = _json_to_id_value_map(server_music_data)
    
    if len(server_music_map) > len(local_music_map):
        with open(local_music_json_path, 'w', encoding='utf-8') as f:
            json.dump(server_music_data, f, ensure_ascii=False, indent=2)

    return [server_music_map[id] for id in server_music_map if id not in local_music_map]


def _json_to_id_value_map(json):
    return {int(song['id']):song for song in json}


def renew_music_ex_data(new_song_list, local_music_ex_json_path, server_music_jacket_base_url):
    if len(new_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    with open(local_music_ex_json_path, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    for song in new_song_list:
        _download_song_jacket(song, server_music_jacket_base_url)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " new song data downloaded : " + song['title'])

    with open(local_music_ex_json_path, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song, server_music_jacket_base_url):
    urllib.request.urlretrieve(server_music_jacket_base_url + song['image_url'], 'jacket/' + song['image_url'])


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_song_new_data_name(song))


def _add_song_new_data_name(song):
    song['enemy_lv'] = ""
    song['enemy_type'] = ""
    song['lev_bas_i'] = ""
    song['lev_adv_i'] = ""
    song['lev_exc_i'] = ""
    song['lev_mas_i'] = ""
    song['lev_lnt_i'] = ""
    return song

def renew_lastupdated(local_music_json_path, local_html_path):
    with open(local_music_json_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = f"DATA: {reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')}"
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {lastupdated} {local_html_path}")

    with open(local_html_path, 'r', encoding='utf-8') as f:
        local_html_data = f.read()

    local_html_data = re.sub(r'(<[^>]+ class="lastupdated"[^>]*>).*(</[^>]+>)',
                             rf'\1<span>{lastupdated}</span>\2',
                             local_html_data,
                             flags=re.IGNORECASE)

    with open(local_html_path, 'w', encoding='utf-8') as f:
        f.write(local_html_data)
