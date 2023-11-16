import requests
import urllib.request
import json
import re
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

CHARACTER_TABLE = {
    "星咲 あかり": "FIRE",
    "藤沢 柚子": "LEAF",
    "三角 葵": "AQUA",
    "高瀬 梨緒": "AQUA",
    "結城 莉玖": "FIRE",
    "藍原 椿": "LEAF",
    "桜井 春菜": "FIRE",
    "早乙女 彩華": "AQUA",
    "井之原 小星": "LEAF",
    "柏木 咲姫": "AQUA",
    "九條 楓": "LEAF",
    "逢坂 茜": "FIRE",
    "珠洲島 有栖": "AQUA",
    "日向 千夏": "LEAF",
    "柏木 美亜": "FIRE",
    "東雲 つむぎ": "AQUA",
    "皇城 セツナ": "FIRE"
}

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


def renew_music_ex_data(new_song_list, local_music_ex_json_path, server_music_jacket_base_url, local_diffs_log_path):
    if len(new_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    f = open("diffs.txt", 'w')

    with open(local_music_ex_json_path, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    for song in new_song_list:
        _download_song_jacket(song, server_music_jacket_base_url)
        _add_song_data_to_ex_data(song, local_music_ex_data)
        _record_new_song_jacket_id(song, local_diffs_log_path)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " new song data downloaded : " + song['title'])

    with open(local_music_ex_json_path, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _download_song_jacket(song, server_music_jacket_base_url):
    urllib.request.urlretrieve(server_music_jacket_base_url + song['image_url'], 'jacket/' + song['image_url'])

def _record_new_song_jacket_id(song, local_diffs_log_path):
    with open(local_diffs_log_path, 'a', encoding='utf-8') as f:
        f.write('jacket/' + song['image_url'] + '\n')


def _add_song_data_to_ex_data(song, ex_data):
    ex_data.append(_add_song_new_data_name(song))

def _parse_wikiwiki(song, wiki):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")

    overview = tables[0].select("tr")
    overview_heads = [tr.find('th').text for tr in overview]
    overview_data = [td.select('td:not([rowspan])')[0].text for td in overview]
    overview_hash = dict(zip(overview_heads, overview_data))

    character_level = overview_hash["対戦相手"].split(" Lv.")
    character = character_level[0]
    level = character_level[1]

    details = tables[1]
    details_heads = [th.text for th in details.select("thead th")]
    details_data = [[cell.text for cell in level.select("th,td")] for level in details.select("tbody tr")]

    for level in details_data:
        level_hash = dict(zip(details_heads, level))

        if level_hash['難易度'] == 'BASIC':
            song["lev_bas_notes"] = level_hash["総ノート数"]
            song["lev_bas_bells"] = level_hash["BELL"]
            song["lev_bas_i"] = level_hash["譜面定数"]
            song["lev_bas_designer"] = level_hash["譜面製作者"]
        elif level_hash['難易度'] == 'ADVANCED':
            song["lev_adv_notes"] = level_hash["総ノート数"]
            song["lev_adv_bells"] = level_hash["BELL"]
            song["lev_adv_i"] = level_hash["譜面定数"]
            song["lev_adv_designer"] = level_hash["譜面製作者"]
        elif level_hash['難易度'] == 'EXPERT':
            song["lev_exc_notes"] = level_hash["総ノート数"]
            song["lev_exc_bells"] = level_hash["BELL"]
            song["lev_exc_i"] = level_hash["譜面定数"]
            song["lev_exc_designer"] = level_hash["譜面製作者"]
        elif level_hash['難易度'] == 'MASTER':
            song["lev_mas_notes"] = level_hash["総ノート数"]
            song["lev_mas_bells"] = level_hash["BELL"]
            song["lev_mas_i"] = level_hash["譜面定数"]
            song["lev_mas_designer"] = level_hash["譜面製作者"]
        elif level_hash['難易度'] == 'LUNATIC':
            song["lev_lnt_notes"] = level_hash["総ノート数"]
            song["lev_lnt_bells"] = level_hash["BELL"]
            song["lev_lnt_i"] = level_hash["譜面定数"]
            song["lev_lnt_designer"] = level_hash["譜面製作者"]

    song['enemy_lv'] = level
    song['enemy_type'] = CHARACTER_TABLE.get(character, None)
    song['bpm'] = overview_hash['BPM']

    return song


def _add_song_new_data_name(song):
    song['enemy_lv'] = ""
    song['enemy_type'] = ""
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

    url = 'https://wikiwiki.jp/gameongeki/' + song['title']
    wiki = requests.get(url)

    if not wiki.ok:
        return song
    else:
        return _parse_wikiwiki(song, wiki)

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
