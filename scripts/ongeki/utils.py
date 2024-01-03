# import ipdb
import requests
import urllib.request
import json
from shared.common_func import *
from ongeki.paths import *

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
    "皇城セツナ": "FIRE"
}

def load_new_song_data():
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)
        local_music_map = _json_to_id_value_map(local_music_data)

    server_music_data = requests.get(SERVER_MUSIC_DATA_URL).json()
    server_music_map = _json_to_id_value_map(server_music_data)

    if len(server_music_map) > len(local_music_map):
        with open(LOCAL_MUSIC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(server_music_data, f, ensure_ascii=False, indent=2)

    return [server_music_map[id] for id in server_music_map if id not in local_music_map]


def _json_to_id_value_map(json):
    return {int(song['id']):song for song in json}


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
        print_message(f"New song added: {song}", bcolors.OKGREEN, args)
        
        if not skipwiki:
            _update_song_wiki_data(song, args)
            
        _record_new_song_jacket_id(song)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song):
    urllib.request.urlretrieve(SERVER_MUSIC_JACKET_BASE_URL + song['image_url'], 'jacket/' + song['image_url'])

def _record_new_song_jacket_id(song):
    with open(LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write('jacket/' + song['image_url'] + '\n')


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
    song['version'] = "bright MEMORY"
    song['wikiwiki_url'] = ""

    return song
