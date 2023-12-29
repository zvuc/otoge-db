import const
import requests
import os
import shutil
import json
import ipdb
import re
from terminal import bcolors
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

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

PAGES = {
    "/sort/1.htm",
    "/sort/2.htm",
    "/sort/3.htm",
    "/sort/4.htm",
    "/sort/5.htm",
    "/sort/6.htm",
    "/sort/7.htm",
    "/sort/7+.htm",
    "/sort/8.htm",
    "/sort/8+.htm",
    "/sort/9.htm",
    "/sort/9+.htm",
    "/sort/10.htm",
    "/sort/10+.htm",
    "/sort/11.htm",
    "/sort/11+.htm",
    "/sort/12.htm",
    "/sort/12+.htm",
    "/sort/13.htm",
    "/sort/13+.htm",
    "/sort/14.htm",
    "/sort/14+.htm",
    "/sort/15.htm",
    "/sort/15+.htm",
    "/sort/lunatic.htm"
}

SDVXIN_BASE_URL = 'https://sdvx.in/ongeki'
LOCAL_CACHE_DIR = 'sdvxin_cache'

# Update on top of existing music-ex
def update_chartguide_data(date_from, date_until, song_id, nocolors, escape, clear_cache):
    _print_message(f"Starting chart link search", nocolors, bcolors.ENDC, escape)

    if clear_cache:
        try:
            # Delete the directory and its contents
            shutil.rmtree(LOCAL_CACHE_DIR)
            print(f"Cleared local cache")
        except FileNotFoundError:
            print(f"Directory not found: {LOCAL_CACHE_DIR}")
        except Exception as e:
            print(f"Error deleting directory: {e}")

    with open(const.LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

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

def _get_and_save_page_to_local(url, nocolors, escape):
    # ipdb.set_trace()
    full_url = SDVXIN_BASE_URL + url
    response = requests.get(full_url)
    response.encoding = 'ansi'

    if not os.path.exists(LOCAL_CACHE_DIR):
        os.makedirs(LOCAL_CACHE_DIR)

    if response.status_code == 200:
        # Extract the filename from the URL
        filename = url.lstrip('/').replace('/', '_')
        output_path = os.path.join(LOCAL_CACHE_DIR, filename)

        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        _print_message(f"Saved {url} to {output_path}", nocolors, bcolors.OKBLUE, escape)
    else:
        _print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", nocolors, bcolors.FAIL, escape)


def _update_song_chartguide_data(song, nocolors, escape):
    _print_message(f"{song['id']} {song['title']}", nocolors, bcolors.ENDC, escape)

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

    

    if song['lunatic']:
        charts = ['luna']
    else:
        charts = ['exp','mst']

    for chart in charts:
        if chart == 'luna':
            lv_page_url = '/sort/lunatic.htm'
            lv_page_file_path = '/sort_lunatic.htm'
            target_key = 'lev_lnt_chart_link'
            url_pattern = '/ongeki/luna'
        elif chart == 'exp':
            lv_page_url = '/sort/' + song['lev_exc'] + '.htm'
            lv_page_file_path = '/sort_' + song['lev_exc'] + '.htm'
            target_key = 'lev_exc_chart_link' 
            url_pattern = '/ongeki/0'
        elif chart == 'mst':
            lv_page_url = '/sort/' + song['lev_mas'] + '.htm'
            lv_page_file_path = '/sort_' + song['lev_mas'] + '.htm'
            target_key = 'lev_mas_chart_link' 
            url_pattern = '/ongeki/0'

        if not song[target_key] == '':
            _print_message(f"Chart link already exists! ({chart.upper()})", nocolors, bcolors.ENDC, escape)
            continue


        # ipdb.set_trace()

        try:
            file_full_path = os.path.join(LOCAL_CACHE_DIR + lv_page_file_path)
            with open(file_full_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            _get_and_save_page_to_local(lv_page_url, nocolors, escape)

            try:
                file_full_path = os.path.join(LOCAL_CACHE_DIR + lv_page_file_path)
                with open(file_full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except:
                _print_message(f"Cache not found ({lv_page_file_path})", nocolors, bcolors.ENDC, escape)
        except Exception as e:
            _print_message(f"Error reading file: {e}", nocolors, bcolors.FAIL, escape)
            sys.exit(1)

        soup = BeautifulSoup(content, 'html.parser')
        song_dict = {}

        # Find all script tags with src attribute starting with "/ongeki/"
        script_tags = soup.find_all('script', src=lambda s: s and s.startswith(url_pattern))

        # Extract script tag src and song_title and add to the dictionary
        for script_tag in script_tags:
            script_src = script_tag['src']
            
            # Find the trailing HTML comment (song_title)
            extracted_song_title = script_tag.find_next(text=lambda text:isinstance(text, Comment))
            
            if extracted_song_title:
                extracted_song_title = extracted_song_title.strip()
                song_dict[script_src] = extracted_song_title

        # ipdb.set_trace()

        song_id = _extract_song_id(song, song_dict, song['title'], nocolors, escape)

        if song_id:
            # extract song_id from src
            if chart == 'luna':
                song_id = song_id.split('/')[-1].split(f'.js')[0]
                song[target_key] = chart + '/' + song_id
            elif 'sort' in script_src:
                song_id = song_id.split('/')[-1].split(f'sort.js')[0]
                song[target_key] = song_id[:2] + '/' + song_id + chart

            _print_message(f"Updated chart link ({chart.upper()})", nocolors, bcolors.OKGREEN, escape)
        else:
            _print_message("No matching ID", nocolors, bcolors.FAIL, escape)
            with open(const.LOCAL_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write('No matching ID : ' + song['id'] + ' ' + song['title'] + '\n')
            return

    return song

def _extract_song_id(song, song_dict, song_title, nocolors, escape):
    for song_id, title in song_dict.items():
        title = title.lower()
        song_title = song_title.lower()

        if title == song_title:
            return song_id
        else: 
            # try fallback pairs
            song_title_alt = (
                song_title
                .replace('ä', 'a')
                .replace('å', 'a')
                .replace('ø', 'o')
                .replace('é', 'e')
                .replace('ö', 'o')
                .replace('☆', '')
                .replace('♥', '')
                .replace('♡', '')
                .replace('！', '!')
                .replace('"', '”')
            )
            if title == song_title_alt:
                return song_id
            else:
                # try removing subtitle
                pattern = re.compile(r'[-～].*?[-～]')
                song_title_wo_subtitle = re.sub(pattern, '', song_title).strip()
                
                if title == song_title_wo_subtitle:
                    _print_message(f"WARNING: matched without subtitle", nocolors, bcolors.WARNING, escape)
                    with open(const.LOCAL_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
                        f.write('WARNING - matched without subtitle : ' + song['id'] + ' ' + song['title'] + '\n')
                    return song_id
                else:
                    match_similarity = _compare_strings(title, song_title)
                    if match_similarity > 80:
                        _print_message(f"Found closest match ({round(match_similarity,2)}%)", nocolors, bcolors.WARNING, escape)
                        return song_id


def _compare_strings(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity_percentage = (intersection / union) * 100
    return similarity_percentage

def get_last_date(LOCAL_MUSIC_JSON_PATH):
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def _print_message(message, nocolors, color_name, escape):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    if escape:
        message = message.replace("'", r"\'")

    # if --nocolors is set
    if nocolors:
        color_name = ''
        reset_color = ''

    print(timestamp + ' ' + color_name + message + reset_color)
