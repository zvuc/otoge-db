# import ipdb
import requests
import os
import shutil
import json
import re
import csv
import sys
from shared.common_func import *
from chunithm.paths import *
from datetime import datetime

errors_log = LOCAL_ERROR_LOG_PATH
SHEETS_ID = '1Nhr-lC1u11WPkUPVTatnNrKWCmVLglaA6hZHgh56N6w'
SHEETS_BASE_URL = f'https://docs.google.com/spreadsheets/d/{SHEETS_ID}/export?format=csv&id={SHEETS_ID}&sheet='
LOCAL_CACHE_DIR = 'chunithm/google_sheets_cache'
CHARTS = [
    # ['lev_bas', 'BAS'],
    ['lev_adv', '', 'ADV'],
    ['lev_exp', '', 'EXP'],
    ['lev_mas', '', 'MAS'],
    ['lev_ult', '', 'ULT']
]
CUR_VERSION_SHEET = '新曲のみ'
SHEETS_MAP = {
    '14%2B,15': ['14', '14+', '15'],
    '14': ['14'],
    '13.8～13.9': ['13+'],
    '13.5～13.7': ['13+'],
    '13': ['13'],
    '12%2B': ['12+'],
    '12': ['12'],
    '11%2B': ['11+'],
    '11以下': ['10','10+','11'],
}
MIN_LV = '10'

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

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date', 'id', args)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        _update_song_const_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _update_song_const_data(song, args):
    song_diffs = [0]
    song_id = song['id']
    title = song['title']
    normalized_title = normalize_title(song['title'])
    # version = song['version']

    print_message(f"{song_id}, {title}", 'HEADER', args, errors_log, args.no_verbose)

    for [chart, chart_type, chart_diff] in CHARTS:
        key_chart_i = f'{chart}_i'
        found_sheet = None

        # # Skip if constant value is already filled
        # if key_chart_i in song and song[key_chart_i] != '':
        #     print_message(f"Chart const already exists! ({key_chart_i})", bcolors.ENDC, args)
        #     continue

        # Skip if utage
        if song['we_kanji'] != '':
            print_message(f"Skipping song (World's End)", bcolors.ENDC, args, errors_log, args.no_verbose)
            return

        # Check if chart type exists in current song
        song_lv = song[chart] if chart in song else None
        if not song_lv:
            continue

        # Skip chart if lv is under minimum threshold
        if evaluate_lv_num(song_lv, f'>={MIN_LV}') is False:
            continue;

        # First lookup latest version sheet
        value_chart_i = _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, CUR_VERSION_SHEET, args)

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
                value_chart_i = _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, sheet, args)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # Last try: look in ALL sheets instead of just correct sheets
        if value_chart_i is None:
            for key, value in SHEETS_MAP.items():
                sheet = key
                value_chart_i = _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, sheet, args)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # If value is not empty, write to song
        if value_chart_i is not None:
            if value_chart_i != '' and value_chart_i != '-':
                if song[key_chart_i] == value_chart_i:
                    print_message(f"No change ({chart_diff}: {value_chart_i}) [Sheet: {found_sheet}]", bcolors.ENDC, args, errors_log, args.no_verbose)
                else:
                    song[key_chart_i] = value_chart_i
                    lazy_print_song_header(f"{song_id}, {title}", song_diffs, args, errors_log)
                    print_message(f"Updated chart constant ({chart_diff}: {value_chart_i}) [Sheet: {found_sheet}]", bcolors.OKGREEN, args, errors_log)
            # If value is placeholder, don't write
            elif value_chart_i == '' or value_chart_i == '-':
                print_message(f"Constant is empty ({chart_diff}, {song_lv})", bcolors.WARNING, args, errors_log, args.no_verbose)
        # If value is not found
        else:
            # Print message in red if value should have been found
            # If this message prints, high chance that title was not matched properly
            if evaluate_lv_num(song_lv, '>=11'):
                print_message(f"Chart not found in sheet ({chart_diff}, {song_lv})", bcolors.FAIL, args, errors_log)
            elif evaluate_lv_num(song_lv, '>=10') and chart == 'lev_mas':
                print_message(f"Chart not found in sheet ({chart_diff}, {song_lv})", bcolors.FAIL, args, errors_log)
            else:
                print_message(f"Chart not found in sheet ({chart_diff}, {song_lv})", bcolors.ENDC, args, errors_log, args.no_verbose)

    return song

def _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, sheet_name, args):
    lv_sheet_url = SHEETS_BASE_URL + sheet_name
    lv_sheet_file_path = f'{sheet_name}.csv'

    # Read local file first, request and cache if it doesn't exist
    file_full_path = os.path.join(LOCAL_CACHE_DIR, lv_sheet_file_path)
    if not os.path.exists(file_full_path):
        get_and_save_page_to_local(lv_sheet_url, file_full_path, args, LOCAL_CACHE_DIR)

        if not os.path.exists(file_full_path):
            print_message(f"Cache not found ({lv_sheet_file_path})", bcolors.ENDC, args, errors_log)
            sys.exit(1)


    # PARSE!
    value_chart_i = None
    with open(file_full_path) as f:
        for row in csv.reader(f):
            length = len(row)
            for i in range(length):
                columns = [
                    normalize_title(row[i]).strip(),
                    normalize_title(row[i + 1]).strip() if i + 1 < length else '',
                    normalize_title(row[i + 2]).strip() if i + 2 < length else '',
                    normalize_title(row[i + 3]).strip() if i + 3 < length else '',
                    normalize_title(row[i + 4]).strip() if i + 4 < length else '',
                    normalize_title(row[i + 5]).strip() if i + 5 < length else '',
                ]

                # For NEW sheet: 曲名 譜面 ジャンル 表示Lv 定数
                # For all else: 曲名 譜面 ジャンル SUN+ LMN
                if columns[0] == normalized_title and columns[1] == chart_diff:
                    value_chart_i = columns[4]

                if value_chart_i is not None:
                    break

            if value_chart_i is not None:
                break

    return value_chart_i
