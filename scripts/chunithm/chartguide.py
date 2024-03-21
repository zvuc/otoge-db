# import ipdb
import requests
import os
import shutil
import json
import re
from shared.common_func import *
from chunithm.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

errors_log = LOCAL_ERROR_LOG_PATH
HASH_KEYS = ['title', 'artist', 'we_kanji']

VERSION_MAPPING = {
    "無印": "01",
    "PLUS": "01",
    "AIR": "02",
    "AIR+": "02",
    "STAR": "03",
    "STAR+": "03",
    "AMAZON": "04",
    "AMAZON+": "04",
    "CRYSTAL": "05",
    "CRYSTAL+": "05",
    "PARADISE": "06",
    "PARADISE×": "06",
    "NEW": "07",
    "NEW+": "07",
    "SUN": "08",
    "SUN+": "08",
    "LUMINOUS": "09"
}

PAGES = {
    "/new.html",
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
    "/sort/ultima.htm",
    "/end.htm"
}

SDVXIN_BASE_URL = 'https://sdvx.in/'
GAME_NAME = 'chunithm'
LOCAL_CACHE_DIR = GAME_NAME + '/sdvxin_cache'

# Update on top of existing music-ex
def update_chartguide_data(args):
    print_message(f"Starting chart link search", bcolors.ENDC, args)

    if args.clear_cache:
        try:
            # Delete the directory and its contents
            shutil.rmtree(LOCAL_CACHE_DIR)
            print(f"Cleared local cache")
        except FileNotFoundError:
            print(f"Directory not found: {LOCAL_CACHE_DIR}")
        except Exception as e:
            print(f"Error deleting directory: {e}")

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added', HASH_KEYS, args)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        _update_song_chartguide_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

def _get_and_save_page_to_local(url, args):
    full_url = SDVXIN_BASE_URL + GAME_NAME + url

    # Handle main page (new songs)
    if url == '':
        full_url = SDVXIN_BASE_URL + GAME_NAME + '.html'

    response = requests.get(full_url)
    response.encoding = 'ansi'

    if not os.path.exists(LOCAL_CACHE_DIR):
        os.makedirs(LOCAL_CACHE_DIR)

    if response.status_code == 200:
        # Extract the filename from the URL
        filename = 'new.html'

        if url != '':
            filename = url.lstrip('/').replace('/', '_')

        output_path = os.path.join(LOCAL_CACHE_DIR, filename)

        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print_message(f"Saved {url} to {output_path}", bcolors.OKBLUE, args, errors_log, args.no_verbose)
    else:
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL, args)


def _update_song_chartguide_data(song, args):
    song_diffs = [0]
    print_message(f"{song['id']} {song['title']}", 'HEADER', args, errors_log, args.no_verbose)

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

    if song['we_kanji']:
        charts = ['end']
    elif song['lev_ult'] != "":
        charts = ['exp','mst','ult']
    else:
        charts = ['exp','mst']

    for chart in charts:
        lv_page_url = ''
        lv_page_file_path = '/new.html'
        target_key = ''
        url_pattern = ''

        if chart == 'end':
            target_key = 'lev_we_chart_link'
            url_pattern = '/' + GAME_NAME + '/end'
        elif chart == 'exp':
            target_key = 'lev_exp_chart_link'
            url_pattern = '/' + GAME_NAME + '/0'
        elif chart == 'mst':
            target_key = 'lev_mas_chart_link'
            url_pattern = '/' + GAME_NAME + '/0'
        elif chart == 'ult':
            target_key = 'lev_ult_chart_link'
            url_pattern = '/' + GAME_NAME + '/ult'

        if not song[target_key] == '':
            print_message(f"Chart link already exists! ({chart.upper()})", bcolors.ENDC, args, errors_log, args.no_verbose)
            continue

        lazy_print_song_header(f"{song['id']}, {song['title']}", song_diffs, args, errors_log)
        song_id, script_src = _parse_page(song, lv_page_url, lv_page_file_path, target_key, url_pattern, args)

        # Search level-specific pages if not found in main page
        if not song_id:
            if chart == 'end':
                lv_page_url = '/end.htm'
                lv_page_file_path = '/end.htm'
                target_key = 'lev_we_chart_link'
                url_pattern = '/' + GAME_NAME + '/end'
            elif chart == 'exp':
                lv_page_url = '/sort/' + song['lev_exp'] + '.htm'
                lv_page_file_path = '/sort_' + song['lev_exp'] + '.htm'
                target_key = 'lev_exp_chart_link'
                url_pattern = '/' + GAME_NAME + '/0'
            elif chart == 'mst':
                lv_page_url = '/sort/' + song['lev_mas'] + '.htm'
                lv_page_file_path = '/sort_' + song['lev_mas'] + '.htm'
                target_key = 'lev_mas_chart_link'
                url_pattern = '/' + GAME_NAME + '/0'
            elif chart == 'ult':
                lv_page_url = '/sort/ultima.htm'
                lv_page_file_path = '/sort_ultima.htm'
                target_key = 'lev_ult_chart_link'
                url_pattern = '/' + GAME_NAME + '/ult'

            lazy_print_song_header(f"{song['id']}, {song['title']}", song_diffs, args, errors_log)
            song_id, script_src = _parse_page(song, lv_page_url, lv_page_file_path, target_key, url_pattern, args)

        if song_id:
            # extract song_id from src
            if chart == 'ult' or chart == 'end':
                song_id = song_id.split('/')[-1].split(f'.js')[0]
                song[target_key] = chart + '/' + song_id
            elif 'sort' in script_src:
                song_id = song_id.split('/')[-1].split(f'sort.js')[0]
                song[target_key] = song_id[:2] + '/' + song_id + chart

            lazy_print_song_header(f"{song['id']}, {song['title']}", song_diffs, args, errors_log)
            print_message(f"✅ Updated chart link ({chart.upper()})", bcolors.OKGREEN, args)
        else:
            lazy_print_song_header(f"{song['id']}, {song['title']}", song_diffs, args, errors_log)
            print_message("No matching ID", bcolors.FAIL, args)
            with open(LOCAL_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write('No matching ID : ' + song['id'] + ' ' + song['title'] + '\n')
            return

    return song

def _parse_page(song, lv_page_url, lv_page_file_path, target_key, url_pattern, args):
    try:
        file_full_path = os.path.join(LOCAL_CACHE_DIR + lv_page_file_path)
        with open(file_full_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        _get_and_save_page_to_local(lv_page_url, args)

        try:
            file_full_path = os.path.join(LOCAL_CACHE_DIR + lv_page_file_path)
            with open(file_full_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except:
            print_message(f"Cache not found ({lv_page_file_path})", bcolors.ENDC, args)
    except Exception as e:
        print_message(f"Error reading file: {e}", bcolors.FAIL, args)
        sys.exit(1)


    soup = BeautifulSoup(content, 'html.parser')
    song_dict = {}

    # Find all script tags with src attribute starting with "/chunithm/"
    script_tags = soup.find_all('script', src=lambda s: s and s.startswith(url_pattern))

    # Extract script tag src and song_title and add to the dictionary
    script_src = ''
    for script_tag in script_tags:
        script_src = script_tag['src']

        if lv_page_url != '':
            # Find the trailing HTML comment (song_title)
            extracted_song_title = script_tag.find_next(text=lambda text:isinstance(text, Comment))
        else:
            response = requests.get(SDVXIN_BASE_URL + script_src)
            response.encoding = 'ansi'
            js_soup = BeautifulSoup(response.text, 'html.parser')
            extracted_song_title = js_soup.find('div', class_='f1').get_text()

        if extracted_song_title:
            extracted_song_title = extracted_song_title.strip()
            song_dict[script_src] = extracted_song_title

    song_id = _extract_song_id(song, song_dict, song['title'], args)

    return song_id, script_src

def _extract_song_id(song, song_dict, song_title, args):
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
                    print_message(f"WARNING: matched without subtitle", bcolors.WARNING, args)
                    with open(LOCAL_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
                        f.write('WARNING - matched without subtitle : ' + song['id'] + ' ' + song['title'] + '\n')
                    return song_id
                else:
                    match_similarity = _compare_strings(title, song_title)
                    if match_similarity > 80:
                        print_message(f"Found closest match ({round(match_similarity,2)}%)", bcolors.WARNING, args)
                        return song_id


def _compare_strings(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity_percentage = (intersection / union) * 100
    return similarity_percentage

