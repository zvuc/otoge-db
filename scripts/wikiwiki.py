import const
import requests
import json
import ipdb
from terminal import bcolors
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'

# Update on top of existing music-ex
def update_songs_extra_data(date_from, date_until, song_id, msgcolor):
    # ipdb.set_trace()
    with open(const.LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # prioritize id search if provided
    if not song_id == 0:
        target_song_list = _filter_songs_by_id(local_music_ex_data, song_id)
    else:
        latest_date = int(get_last_date(const.LOCAL_MUSIC_EX_JSON_PATH))

        if date_from == 0:
            date_from = latest_date

        if date_until == 0:
            date_until = latest_date

        target_song_list = _filter_songs_by_date(local_music_ex_data, date_from, date_until)


    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    f = open("diffs.txt", 'w')

    for song in target_song_list:
        _update_song_wiki_data(song, msgcolor)

    with open(const.LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _filter_songs_by_date(song_list, date_from, date_until):
    target_song_list = []

    for song in song_list:
        song_date_int = int(song.get("date"))

        if date_from <= song_date_int <= date_until:
            target_song_list.append(song)

    return target_song_list


def _filter_songs_by_id(song_list, song_id):
    target_song_list = []

    for song in song_list:
        if song_id == int(song.get("id")):
            target_song_list.append(song)

    return target_song_list


def _update_song_wiki_data(song, msgcolor):
    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
        .replace('"', '”')
    )

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        url = song['wikiwiki_url']
        wiki = requests.get(url)

        _print_message(bcolors.OKBLUE, song, "(URL already present!)", msgcolor)
        return _parse_wikiwiki(song, wiki, url, msgcolor)

    # If not, guess URL from title
    else:
        guess_url = wiki_base_url + title
        wiki = requests.get(guess_url)

        if not wiki.ok:
            # try replacing special character as fallback
            title = title.replace('\'', '’')
            guess_url = wiki_base_url + title
            wiki = requests.get(guess_url)

            if not wiki.ok:
                # give up
                _print_message(bcolors.FAIL, song, "failed to guess wiki page", msgcolor)
                return song

            else:
                url = guess_url
                return _parse_wikiwiki(song, wiki, url, msgcolor)
                
        else:
            url = guess_url
            
            return _parse_wikiwiki(song, wiki, url, msgcolor)


def _parse_wikiwiki(song, wiki, url, msgcolor):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        _print_message(bcolors.FAIL, song, "Parse failed! Skipping song", msgcolor)
        return song

    # find the overview table
    overview_table = None
    
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            second_row_th = rows[1].find('th')
            if second_row_th and second_row_th.get_text(strip=True) == 'タイトル':
                img_in_first_col = rows[0].find('td',{'rowspan': True})
                if img_in_first_col:
                    overview_table = table
                    break

    if overview_table:
        overview_heads = overview_table.select('th')

        if song['lunatic'] == '1':
            overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]
        else:
            overview_data = [head.find_parent('tr').select('td:not([rowspan])') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text for data in overview_data]
        overview_hash = dict(zip(overview_heads, overview_data))

        # Find enemy lv data
        if 'LV.' in overview_hash["対戦相手"].upper():
            enemy_info = overview_hash["対戦相手"].upper().split("LV.")
            enemy_name = enemy_info[0]
            enemy_lv = enemy_info[1]
            song['enemy_lv'] = enemy_lv

            # If character name includes type info, use it
            if 'FIRE' in enemy_name:
                song['enemy_type'] = 'FIRE'
            elif 'AQUA' in enemy_name:
                song['enemy_type'] = 'AQUA'
            elif 'LEAF' in enemy_name:
                song['enemy_type'] = 'LEAF'

        else:
            # fail
            _print_message(bcolors.WARNING, song, "Warning - enemy lv not found", msgcolor)
            
    else:
        # fail
        _print_message(bcolors.WARNING, song, "Warning - overview table not found", msgcolor)


    # find the charts table
    charts_table = None
    for table in tables:
        th_elements = table.select('th:nth-of-type(1), th:nth-of-type(2)')
        if len(th_elements) > 2 and th_elements[0].get_text(strip=True) == '難易度' and th_elements[1].get_text(strip=True) == '楽曲Lv':
            charts_table = table
            break
    
    if charts_table:
        charts_table_head = [th.text for th in charts_table.select("thead th")]
        charts_data = [[cell.text for cell in level.select("th,td")] for level in charts_table.select("tbody tr")]

        if any(charts_table_head) and '難易度' in charts_table_head[0]:
            for chart_details in charts_data:
                level_hash = dict(zip(charts_table_head, chart_details))

                if song['lunatic'] == '' and level_hash['難易度'] == 'BASIC':
                    song["lev_bas_notes"] = level_hash["総ノート数"].replace(',', '')
                    song["lev_bas_bells"] = level_hash["BELL"].replace(',', '')
                    song["lev_bas_i"] = level_hash["譜面定数"]
                    song["lev_bas_designer"] = level_hash["譜面製作者"]
                elif song['lunatic'] == '' and level_hash['難易度'] == 'ADVANCED':
                    song["lev_adv_notes"] = level_hash["総ノート数"].replace(',', '')
                    song["lev_adv_bells"] = level_hash["BELL"].replace(',', '')
                    song["lev_adv_i"] = level_hash["譜面定数"]
                    song["lev_adv_designer"] = level_hash["譜面製作者"]
                elif song['lunatic'] == '' and level_hash['難易度'] == 'EXPERT':
                    song["lev_exc_notes"] = level_hash["総ノート数"].replace(',', '')
                    song["lev_exc_bells"] = level_hash["BELL"].replace(',', '')
                    song["lev_exc_i"] = level_hash["譜面定数"]
                    song["lev_exc_designer"] = level_hash["譜面製作者"]
                elif song['lunatic'] == '' and level_hash['難易度'] == 'MASTER':
                    song["lev_mas_notes"] = level_hash["総ノート数"].replace(',', '')
                    song["lev_mas_bells"] = level_hash["BELL"].replace(',', '')
                    song["lev_mas_i"] = level_hash["譜面定数"]
                    song["lev_mas_designer"] = level_hash["譜面製作者"]
                elif song['lunatic'] == '1' and level_hash['難易度'] == 'LUNATIC':
                    song["lev_lnt_notes"] = level_hash["総ノート数"].replace(',', '')
                    song["lev_lnt_bells"] = level_hash["BELL"].replace(',', '')
                    song["lev_lnt_i"] = level_hash["譜面定数"]
                    song["lev_lnt_designer"] = level_hash["譜面製作者"]
        else:
            _print_message(bcolors.WARNING, song, "Warning - No chart table found", msgcolor)
    else:
        _print_message(bcolors.WARNING, song, "Warning - No chart table found", msgcolor)
    

    song['bpm'] = overview_hash['BPM']

    song['wikiwiki_url'] = url

    _print_message(bcolors.OKGREEN, song, "Updated song extra data from wiki", msgcolor)

    return song



def get_last_date(LOCAL_MUSIC_JSON_PATH):
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def _print_message(color_name, song, message, msgcolor):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    # if --nocolor
    if msgcolor:
        color_name = ''
        reset_color = ''

    print(timestamp + color_name + ' ' + song['id'] + ' ' + message + ' : ' + song['title'] + reset_color)
