import const
import requests
import json
import ipdb
import re
from terminal import bcolors
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup, Comment

VERSION_MAPPING = {
    'ONGEKI': '01',
    'ONGEKI plus': '01',
    'SUMMER': '02',
    'SUMMER plus': '02',
    'RED': '03',
    'RED plus': '03',
    'bright': '04',
    'bright MEMORY': '04'
}

sdvxin_base_url = 'https://sdvx.in/ongeki/sort/'

# Update on top of existing music-ex
def update_chartguide_data(date_from, date_until, song_id, nocolors, escape):
    
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
        _update_song_chartguide_data(song, nocolors, escape)

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


def _update_song_chartguide_data(song, nocolors, escape):
    _print_message("Searching for chart link", song, nocolors, bcolors.ENDC, escape)

    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
        .replace('"', '”')
    )

    version_num = VERSION_MAPPING.get(song['version'])

    if song['lunatic'] == '1':
        charts = ['luna']
    else:
        charts = ['exp','mas']
    

    for chart in charts:
        if chart == 'luna':
            lv_page_url = sdvxin_base_url + 'lunatic.htm'
            target_key = 'lev_lnt_chart_link'
        elif chart == 'exp':
            lv_page_url = sdvxin_base_url + song['lev_exc'] + '.htm'
            target_key = 'lev_exc_chart_link' 
        elif chart == 'mas':
            lv_page_url = sdvxin_base_url + song['lev_mas'] + '.htm'
            target_key = 'lev_mas_chart_link' 

        if not song[target_key] == '':
            _print_message(f"Link already exists! ({chart})", song, nocolors, bcolors.ENDC, escape)
            continue

        request = requests.get(lv_page_url)
        request.encoding = 'ansi'

        soup = BeautifulSoup(request.text, 'html.parser')
        song_dict = {}

        # Find all script tags with src attribute starting with "/ongeki/"
        script_tags = soup.find_all('script', src=lambda s: s and s.startswith("/ongeki/0"))

        # Extract song_id and song_title and add to the dictionary
        for script_tag in script_tags:
            extracted_song_id = script_tag['src'].split('/')[-1].split('sort.js')[0]
            
            # Find the trailing HTML comment (song_title)
            extracted_song_title = script_tag.find_next(text=lambda text:isinstance(text, Comment))
            
            if extracted_song_title:
                extracted_song_title = extracted_song_title.strip()
                song_dict[extracted_song_id] = extracted_song_title

        song_id = _extract_song_id(song_dict, song['title'])

        if song_id:
            song[target_key] = version_num + '/' + song_id + chart
            _print_message(f"Updated chart link ({chart})", song, nocolors, bcolors.OKGREEN, escape)
        else:
            _print_message("No matching ID", song, nocolors, bcolors.FAIL, escape)
            return

    return song

def _extract_song_id(song_dict, song_title):
    # ipdb.set_trace()
    for song_id, title in song_dict.items():
        if title == song_title:
            return song_id


def get_last_date(LOCAL_MUSIC_JSON_PATH):
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def _print_message(message, song, nocolors, color_name, escape):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    if song:
        song_id = song['id']

        # if --escape is set
        if escape:
            song_title = ' : ' + song['title'].replace("'", r"\'")
        else:
            song_title = ' : ' + song['title']
    else:
        song_id = ''
        song_title = ''

    # if --nocolors is set
    if nocolors:
        color_name = ''
        reset_color = ''

    print(timestamp + color_name + ' ' + song_id + ' ' + message + song_title + reset_color)
