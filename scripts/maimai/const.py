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

errors_log = LOCAL_ERROR_LOG_PATH
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
            target_song_list = filter_songs_by_id_range(local_music_ex_data, 'sort', id_from, id_to)
        else:
            target_song_list = filter_songs_by_id(local_music_ex_data, 'sort', song_id)
    elif date_from != 0 or date_until != 0:
        latest_date = int(get_last_date(LOCAL_MUSIC_EX_JSON_PATH))

        if date_from == 0:
            date_from = latest_date

        if date_until == 0:
            date_until = latest_date

        target_song_list = filter_songs_by_date(local_music_ex_data, 'date', date_from, date_until)
    else:
        # get id list from diffs.txt
        target_song_list = filter_songs_from_diffs(local_music_ex_data, _maimai_generate_hash(song))


    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        _update_song_const_data(song, args)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _maimai_generate_hash(song):
    if 'lev_utage' in song:
        return generate_hash(song['title'] + song['lev_utage'] + song['kanji'])
    else:
        return generate_hash(song['title'] + song['image_url'])



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
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL, args, errors_log)


def _update_song_const_data(song, args):
    sort = song['sort']
    title = song['title']
    normalized_title = normalize_title(song['title'])
    version = song['version']

    print_message(f"{sort}, {title}, {version}", bcolors.ENDC, args, errors_log)

    charts = [
        ['lev_bas', 'STD', 'BAS'],
        ['lev_adv', 'STD', 'ADV'],
        ['lev_exp', 'STD', 'EXP'],
        ['lev_mas', 'STD', 'MAS'],
        ['lev_remas', 'STD', 'REMAS'],
        ['dx_lev_bas', 'DX', 'BAS'],
        ['dx_lev_adv', 'DX', 'ADV'],
        ['dx_lev_exp', 'DX', 'EXP'],
        ['dx_lev_mas', 'DX', 'MAS'],
        ['dx_lev_remas', 'DX', 'REMAS'],
    ]

    for [chart, chart_type, chart_diff] in charts:
        key_chart_i = f'{chart}_i'

        # # Skip if constant value is already filled
        # if key_chart_i in song and song[key_chart_i] != '':
        #     print_message(f"Chart const already exists! ({key_chart_i})", bcolors.ENDC, args)
        #     continue

        # Skip if utage
        if 'lev_utage' in song:
            print_message(f"Skipping song (Utage)", bcolors.ENDC, args, errors_log)
            return

        # Check if chart type exists in current song
        song_lv = song[chart] if chart in song else None
        if not song_lv:
            continue

        # First lookup latest version sheet
        value_chart_i = _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, 'BUDDiES新曲')

        # If const is not found in latest ver sheet, lookup old version sheets next
        if value_chart_i is None:
            if song_lv in ['14', '14+', '15']:
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
                # print_message(f"Chart not in sheet ({version}, {chart}, {song_lv})", bcolors.ENDC, args)
                continue

            value_chart_i = _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, sheet_name)

        # If value is not empty, write to song
        if value_chart_i is not None:
            if value_chart_i != '' and value_chart_i != '-':
                song[key_chart_i] = value_chart_i
                print_message(f"Updated chart constant ({key_chart_i}: {value_chart_i})", bcolors.OKGREEN, args, errors_log)
            # If value is placeholder, don't write
            elif value_chart_i == '' or value_chart_i == '-':
                print_message(f"Constant is empty ({chart}, {song_lv})", bcolors.WARNING, args, errors_log)
        # If value is not found
        else:
            # Print message in red if value should have been found
            # If this message prints, high chance that title was not matched properly
            if song_lv in ['12', '12+', '13', '13+', '14', '14+', '15']:
                print_message(f"Chart not found in sheet ({chart}, {song_lv})", bcolors.FAIL, args, errors_log)
            else:
                print_message(f"Chart not found in sheet ({chart}, {song_lv})", bcolors.ENDC, args, errors_log)

    return song

def _find_chart_in_sheet(song_lv, normalized_title, chart_type, chart_diff, sheet_name):
    lv_sheet_url = SHEETS_BASE_URL + sheet_name
    lv_sheet_file_path = f'{sheet_name}.csv'

    # ipdb.set_trace()

    # Read local file first, request and cache if it doesn't exist
    file_full_path = os.path.join(LOCAL_CACHE_DIR, lv_sheet_file_path)
    if not os.path.exists(file_full_path):
        _get_and_save_page_to_local(lv_sheet_url, file_full_path, args)

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

                # For 12+, 12: (title) 譜面1 譜面2 旧定数 新定数
                if columns[0] == normalized_title and columns[1] == chart_type and columns[2] == chart_diff:
                    value_chart_i = columns[4]

                # For 13, 13+, 14以上: (title) ジャンル 譜面1 譜面2 旧定数 新定数
                if columns[0] == normalized_title and columns[2] == chart_type and columns[3] == chart_diff:
                    value_chart_i = columns[5]

                if value_chart_i is not None:
                    break

            if value_chart_i is not None:
                break

    return value_chart_i
