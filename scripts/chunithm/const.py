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

SHEETS_ID = '1UgalRHELZBe4Wb4yKXffBJ6juj57bHgSdEWphCDsByE'
SHEETS_BASE_URL = f'https://docs.google.com/spreadsheets/d/{SHEETS_ID}/export?format=csv&id={SHEETS_ID}&gid='

CHARTS = [
    # ['lev_bas', 'BAS'],
    ['lev_adv', 'ADV'],
    ['lev_exp', 'EXP'],
    ['lev_mas', 'MAS'],
    ['lev_ult', 'ULT']
]
CUR_VERSION_SHEET = '1971412612'
SHEETS_MAP = {
    '672636621': ['15', '15+'],
    '262760047': ['14+'],
    '2099154164': ['14'],
    '1700582700': ['13+'],
    '487918628': ['13+'],
    '252479953': ['13'],
    '2103723114': ['12+'],
    '1659819067': ['12'],
    '847410292': ['11+'],
    '872334439': ['10','10+','11'],
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

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added')

    if len(target_song_list) == 0:
        print_message("(Nothing to update)", bcolors.ENDC, log=True)
        return

    total_diffs = [0]

    for song in target_song_list:
        _update_song_const_data(song, total_diffs)

    sort_and_save_json(local_music_ex_data, LOCAL_MUSIC_EX_JSON_PATH)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def _update_song_const_data(song, total_diffs):
    header_printed = [0]
    song_id = song['id']
    title = song['title']
    normalized_title = normalize_title(song['title'])
    # version = song['version']

    for [chart, chart_diff] in CHARTS:
        key_chart_i = f'{chart}_i'
        found_sheet = None

        # If --overwrite is not set, skip charts with existing values
        if not game.ARGS.overwrite:
            if key_chart_i in song and song[key_chart_i] != '':
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Chart const already exists! ({chart_diff})", bcolors.ENDC, log=True, is_verbose=True)
                continue

        # Skip if utage
        if song['we_kanji'] != '':
            lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
            print_message(f"Skipping song (World's End)", bcolors.ENDC, log=True, is_verbose=True)
            return

        # Check if chart type exists in current song
        song_lv = song[chart] if chart in song else None
        if not song_lv:
            continue

        # Skip chart if lv is under minimum threshold
        if evaluate_lv_num(song_lv, f'>={MIN_LV}') is False:
            continue;

        # First lookup latest version sheet
        value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_diff, CUR_VERSION_SHEET, header_printed)

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
                value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_diff, sheet, header_printed)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # Last try: look in ALL sheets instead of just correct sheets
        if value_chart_i is None:
            for key, value in SHEETS_MAP.items():
                sheet = key
                value_chart_i = _find_chart_in_sheet(song, song_lv, normalized_title, chart_diff, sheet, header_printed)

                if value_chart_i is not None:
                    found_sheet = sheet
                    break;

        # If value found in sheet is not empty, write to song
        if value_chart_i is not None:
            # If value is placeholder, don't write
            if value_chart_i in ['', '-']:
                lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Constant is empty ({chart_diff}, {song_lv})", bcolors.ENDC, log=True, is_verbose=True)

            # If value is valid
            elif re.fullmatch(r'\d+\.\d', value_chart_i):
                # If lev_xxx_i doesn't exist yet, create it:
                if key_chart_i not in song:
                    total_diffs[0] += 1

                    lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                    print_message(f"Added chart constant ({chart_diff}: {value_chart_i})", bcolors.OKGREEN, log=True)

                    song[key_chart_i] = str(value_chart_i)

                # If existing chart const is empty
                if song[key_chart_i] == "":
                    total_diffs[0] += 1

                    lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                    print_message(f"Updated chart constant ({chart_diff}: {value_chart_i})", bcolors.OKGREEN, log=True)

                    song[key_chart_i] = str(value_chart_i)

                # If there is already a value
                else:
                    # previous value is different
                    if song[key_chart_i] != str(value_chart_i):
                        if game.ARGS.overwrite:
                            total_diffs[0] += 1
                            lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True)
                            print_message(
                                f"Overwrote chart constant ({chart_diff}: {song[key_chart_i]} → {value_chart_i}) "
                                f"{f'[Sheet: {found_sheet}]' if not game.ARGS.no_verbose else ''}",
                                bcolors.WARNING, log=True
                            )

                            song[key_chart_i] = str(value_chart_i)
                        else:
                            lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                            print_message(f"No change ({chart_diff}: {value_chart_i})", bcolors.ENDC, log=True, is_verbose=True)
                    # value is same
                    else:
                        lazy_print_song_header(f"{song['id']}, {song['title']}", header_printed, log=True, is_verbose=True)
                        print_message(f"No change ({chart_diff}: {value_chart_i})", bcolors.ENDC, log=True, is_verbose=True)

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

def _find_chart_in_sheet(song, song_lv, normalized_title, chart_diff, sheet_name, header_printed):
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

                # For NEW sheet: 曲名 譜面 ジャンル 表示Lv 定数
                # For all else: 曲名 譜面 ジャンル SUN+ LMN
                if normalize_title(columns[0]) == normalized_title and columns[1] == chart_diff:
                    value_chart_i = columns[4]

                if value_chart_i is not None:
                    break

            if value_chart_i is not None:
                break

    return value_chart_i
