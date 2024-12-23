# import ipdb
import requests
import os
import shutil
import json
import re
import csv
import sys
from shared.common_func import *
from ongeki.paths import *
from datetime import datetime

SHEETS_ID = '1a7nDEG8N3QQUHl3WDwZedInX3_0EMSpU7qUuW89Lq3c'
SHEETS_BASE_URL = f'https://docs.google.com/spreadsheets/d/{SHEETS_ID}/export?format=csv&id={SHEETS_ID}&gid='
LOCAL_SHEETS_CACHE_DIR = 'ongeki/google_sheets_cache'

CHARTS = [
    # ['lev_bas', 'BAS'],
    ['lev_adv', '', 'ADVANCED'],
    ['lev_exc', '', 'EXPERT'],
    ['lev_mas', '', 'MASTER'],
    ['lev_lnt', '', 'LUNATIC']
]
CUR_VERSION_SHEET = '1885837597'
SHEETS_MAP = {
    '607247191': ['14+', '15', '15+'],
    '1614592040': ['14'],
    '995212684': ['13+'],
    '1830291633': ['13'],
    '664628079': ['12+'],
    '967700523': ['12'],
    '1430431771': ['11+'],
    '964137998': ['11'],
    '1086958346': ['10+'],
    '1121689670': ['10']
}
MIN_LV = '10'

# Update on top of existing music-ex
def update_const_data():
    print_message(f"Fetch chart constants", 'H2', log=True)

    if game.ARGS.clear_cache:
        try:
            # Delete the directory and its contents
            shutil.rmtree(LOCAL_SHEETS_CACHE_DIR)
            print(f"Cleared local cache")
        except FileNotFoundError:
            print(f"Directory not found: {LOCAL_SHEETS_CACHE_DIR}")
        except Exception as e:
            print(f"Error deleting directory: {e}")

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added', game.HASH_KEYS_EX)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        _update_song_const_data(song)

        # Sort the song dictionary before saving
        sorted_song = sort_dict_keys(song)
        song.clear()  # Clear the original song dictionary
        song.update(sorted_song)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _update_song_const_data(song):
    header_printed = [0]
    song_id = song['id']
    title = song['title']
    normalized_title = normalize_title(song['title'])
    # version = song['version']

    for [chart, chart_type, chart_diff] in CHARTS:
        key_chart_i = f'{chart}_i'
        found_sheet = None

        # If --overwrite is not set, skip charts with existing values
        if not game.ARGS.overwrite:
            if key_chart_i in song and song[key_chart_i] != '':
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Chart const already exists! ({key_chart_i})", bcolors.ENDC, log=True, is_verbose=True)
                continue

        if 'ソロver' in title:
            normalized_title = normalize_title(re.sub(r'\s*-\s*.*ソロver\.-$', '', title))


        # Check if chart type exists in current song
        song_lv = song[chart] if chart in song else None
        if not song_lv:
            continue

        # Skip chart if lv is under minimum threshold
        if evaluate_lv_num(song_lv, f'>={MIN_LV}') is False:
            continue;

        # First lookup latest version sheet
        value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_type, chart_diff, CUR_VERSION_SHEET, header_printed)

        # If value was found
        if value_chart_i is not None:
            found_sheet = CUR_VERSION_SHEET
        # If const is not found in latest ver sheet, lookup old version sheets next
        else:
            respective_sheets = []
            for key, value in SHEETS_MAP.items():
                if song_lv in value:
                    respective_sheets.append(key)

            for sheet in respective_sheets:
                value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_type, chart_diff, sheet, header_printed)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # Last try: look in ALL sheets instead of just correct sheets
        if value_chart_i is None:
            for key, value in SHEETS_MAP.items():
                sheet = key
                value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_type, chart_diff, sheet, header_printed)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # If value is not empty, write to song
        if value_chart_i is not None:
            if value_chart_i != '' and value_chart_i != '-':
                if key_chart_i in song and song[key_chart_i] == value_chart_i:
                    lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"No change ({chart_diff}: {value_chart_i}) [Sheet: {found_sheet}]", bcolors.ENDC, log=True, is_verbose=True)
                else:
                    song[key_chart_i] = value_chart_i
                    lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                    print_message(f"Updated chart constant ({chart_diff}: {value_chart_i}) [Sheet: {found_sheet}]", bcolors.OKGREEN, log=True)
            # If value is placeholder, don't write
            elif value_chart_i == '' or value_chart_i == '-':
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Constant is empty ({chart_diff}, {song_lv})", bcolors.WARNING, log=True, is_verbose=True)
        # If value is not found
        else:
            # Print message in red if value should have been found
            # If this message prints, high chance that title was not matched properly
            if evaluate_lv_num(song_lv, '>=11'):
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                print_message(f"Chart with matching song not found in sheet ({chart_diff}, {song_lv})", bcolors.FAIL, log=True)
            elif evaluate_lv_num(song_lv, '>=10') and chart == 'lev_mas':
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                print_message(f"Chart with matching song not found in sheet ({chart_diff}, {song_lv})", bcolors.FAIL, log=True)
            else:
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Chart with matching song not found in sheet ({chart_diff}, {song_lv})", bcolors.ENDC, log=True, is_verbose=True)

    return song

def _find_chart_in_sheet(song, song_lv, normalized_title, chart_type, chart_diff, sheet_name, header_printed):
    lv_sheet_url = SHEETS_BASE_URL + sheet_name
    lv_sheet_file_path = f'{sheet_name}.csv'

    # Read local file first, request and cache if it doesn't exist
    file_full_path = os.path.join(LOCAL_SHEETS_CACHE_DIR, lv_sheet_file_path)
    if not os.path.exists(file_full_path):
        get_and_save_page_to_local(lv_sheet_url, file_full_path, LOCAL_SHEETS_CACHE_DIR)

        if not os.path.exists(file_full_path):
            lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
            print_message(f"Cache not found ({lv_sheet_file_path})", bcolors.ENDC, log=True, is_verbose=True)
            sys.exit(1)


    # PARSE!
    value_chart_i = None
    with open(file_full_path) as f:
        for row in csv.reader(f):
            length = len(row)
            for i in range(length):
                columns = [
                    row[i].strip(),
                    row[i + 1].strip() if i + 1 < length else '',
                    row[i + 2].strip() if i + 2 < length else '',
                    row[i + 3].strip() if i + 3 < length else '',
                    row[i + 4].strip() if i + 4 < length else '',
                    row[i + 5].strip() if i + 5 < length else '',
                ]

                if normalize_title(columns[0]) == normalized_title and columns[1] == chart_diff:
                    # For NEW sheet: 曲名 難易度 Lv 定数
                    if sheet_name == CUR_VERSION_SHEET:
                        value_chart_i = columns[3]
                    # For all else: 曲名 難易度 ジャンル 旧 新定数
                    else:
                        value_chart_i = columns[4]

                if value_chart_i is not None:
                    break

            if value_chart_i is not None:
                break

    return value_chart_i
