# import ipdb
import requests
import os
import shutil
import json
import re
import csv
import sys
from shared.common_func import *
from maimai.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

SHEETS_ID = '1vSqx2ghJKjWwCLrDEyZTUMSy5wkq_gY4i0GrJgSreQc'
SHEETS_BASE_URL = f'https://docs.google.com/spreadsheets/d/{SHEETS_ID}/gviz/tq?tqx=out:csv&sheet='
LOCAL_CACHE_DIR = 'maimai/google_sheets_cache'

# Update on top of existing music-ex
def update_const_data(args):
    print_message(f"Starting chart const search", bcolors.ENDC, args)

    date_from = args.date_from
    date_until = args.date_until
    song_id = args.id
    clear_cache = args.clear_cache

    if clear_cache:
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

    # prioritize id search if provided
    if song_id != 0:
        if '-' in song_id:
            id_from = song_id.split('-')[0]
            id_to = song_id.split('-')[-1]
            target_song_list = _filter_songs_by_id_range(local_music_ex_data, id_from, id_to)
        else:
            target_song_list = _filter_songs_by_id(local_music_ex_data, song_id)
    elif date_from != 0 or date_until != 0:
        latest_date = int(get_last_date(LOCAL_MUSIC_EX_JSON_PATH))

        if date_from == 0:
            date_from = latest_date

        if date_until == 0:
            date_until = latest_date

        target_song_list = _filter_songs_by_date(local_music_ex_data, date_from, date_until)
    else:
        # get id list from diffs.txt
        target_song_list = _filter_songs_from_diffs(local_music_ex_data)


    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        _update_song_const_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _filter_songs_by_date(song_list, date_from, date_until):
    target_song_list = []

    for song in song_list:
        song_date_int = int(song.get("date"))

        if date_from <= song_date_int <= date_until:
            target_song_list.append(song)

    return target_song_list

def _filter_songs_by_id_range(song_list, id_from, id_to):
    target_song_list = []

    for song in song_list:
        song_id_int = int(song.get("sort"))

        if int(id_from) <= song_id_int <= int(id_to):
            target_song_list.append(song)

    return target_song_list

def _filter_songs_from_diffs(song_list):
    with open(LOCAL_DIFFS_LOG_PATH, 'r') as f:
        diff_lines = f.readlines()

    # Create a set of identifiers from the lines in diffs.txt
    prefixes_to_remove = ['NEW ', 'UPDATED ']
    for prefix in prefixes_to_remove:
        diff_lines = [line.replace(prefix, '') for line in diff_lines]

    unique_id = {line.strip() for line in diff_lines}

    target_song_list = []
    # Filter songs based on the identifiers
    for song in song_list:
        song_hash = _maimai_generate_hash(song)

        if song_hash in unique_id:
            target_song_list.append(song)

    return target_song_list

def _maimai_generate_hash(song):
    if 'lev_utage' in song:
        return generate_hash(song['title'] + song['lev_utage'] + song['kanji'])
    else:
        return generate_hash(song['title'] + song['image_url'])

def _filter_songs_by_id(song_list, song_id):
    target_song_list = []

    for song in song_list:
        if int(song_id) == int(song.get("sort")):
            target_song_list.append(song)

    return target_song_list


def _get_and_save_page_to_local(url, output_path, args):
    # ipdb.set_trace()
    response = requests.get(url)
    response.encoding = 'ansi'

    if not os.path.exists(LOCAL_CACHE_DIR):
        os.makedirs(LOCAL_CACHE_DIR)

    if response.status_code == 200:
        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print_message(f"Saved {url} to {output_path}", bcolors.OKBLUE, args)
    else:
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL, args)


def _update_song_const_data(song, args):
    sort = song['sort']
    title = _normalize(song['title'])
    version = song['version']

    print_message(f"{sort}, {title}, {version}", bcolors.ENDC, args)

    charts = [
        ['lev_bas', 'STD', 'BAS'],
        ['lev_adv', 'STD', 'ADV'],
        ['lev_exp', 'STD', 'EXP'],
        ['lev_mas', 'STD', 'MAS'],
        ['lev_remas', 'STD', 'ReMAS'],
        ['dx_lev_bas', 'DX', 'BAS'],
        ['dx_lev_adv', 'DX', 'ADV'],
        ['dx_lev_exp', 'DX', 'EXP'],
        ['dx_lev_mas', 'DX', 'MAS'],
        ['dx_lev_remas', 'DX', 'ReMAS'],
    ]

    for [chart, type1, type2] in charts:
        key_chart_i = f'{chart}_i'

        # # Skip if constant value is already filled
        # if key_chart_i in song and song[key_chart_i] != '':
        #     print_message(f"Chart const already exists! ({key_chart_i})", bcolors.ENDC, args)
        #     continue

        # Check if chart type exists in current song
        song_lv = song[chart] if chart in song else None
        if not song_lv:
            continue

        # Find sheet
        if len(version) == 5 and version[:2] == '24': # 24000
            sheet_name = 'BUDDiES新曲'
        elif song_lv in ['14', '14+', '15']:
            sheet_name = '14以上'
        elif song_lv == '13+':
            sheet_name = '13%2B'
        elif song_lv == '13':
            sheet_name = '13'
        elif song_lv == '12+':
            sheet_name = '12%2B'
        elif song_lv == '12':
            sheet_name = '12'
        else:
            print_message(f"Not in sheet ({version}, {chart}, {song_lv})", bcolors.ENDC, args)
            continue

        lv_sheet_url = SHEETS_BASE_URL + sheet_name
        lv_sheet_file_path = f'{sheet_name}.csv'


        # ipdb.set_trace()

        # Read local file first, request and cache if it doesn't exist
        file_full_path = os.path.join(LOCAL_CACHE_DIR, lv_sheet_file_path)
        if not os.path.exists(file_full_path):
            _get_and_save_page_to_local(lv_sheet_url, file_full_path, args)

            if not os.path.exists(file_full_path):
                print_message(f"Cache not found ({lv_sheet_file_path})", bcolors.ENDC, args)
                sys.exit(1)


        # PARSE!
        value_chart_i = None
        with open(file_full_path) as f:
            for row in csv.reader(f):
                length = len(row)
                for i in range(length):
                    columns = [
                        _normalize(row[i]).strip(),
                        _normalize(row[i + 1]).strip() if i + 1 < length else '',
                        _normalize(row[i + 2]).strip() if i + 2 < length else '',
                        _normalize(row[i + 3]).strip() if i + 3 < length else '',
                        _normalize(row[i + 4]).strip() if i + 4 < length else '',
                        _normalize(row[i + 5]).strip() if i + 5 < length else '',
                    ]

                    # For 12+, 12: (title) 譜面1 譜面2 旧定数 新定数
                    if columns[0] == title and columns[1] == type1 and columns[2] == type2:
                        value_chart_i = columns[4]

                    # For 13, 13+, 14以上: (title) ジャンル 譜面1 譜面2 旧定数 新定数
                    if columns[0] == title and columns[2] == type1 and columns[3] == type2:
                        value_chart_i = columns[5]

                    if value_chart_i is not None:
                        break

                if value_chart_i is not None:
                    break

        if value_chart_i is not None and value_chart_i != '' and value_chart_i != '-':
            song[key_chart_i] = value_chart_i
            print_message(f"Updated chart const ({key_chart_i}: {value_chart_i})", bcolors.OKGREEN, args)
        else:
            print_message(f"No matching chart const found ({chart}, {song_lv})", bcolors.FAIL, args)

    return song

def _normalize(string: str):
    return (
        string
        .replace('＆', '&')
        .replace('：', ':')
        .replace('［', '[')
        .replace('］', ']')
        .replace('＃', '#')
        .replace('”', '"')
        .replace('！', '!')
        .replace('？', '?')
        .replace('　', ' ')
    )
