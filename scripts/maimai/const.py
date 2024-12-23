# import ipdb
import requests
import json
import os
import re
from bs4 import BeautifulSoup
from shared.common_func import *
from maimai.paths import *
from datetime import datetime
from math import log2

SGIMERA_URL = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_prism_.js'
# SGIMERA_URL = 'https://gist.githubusercontent.com/myjian/f059331eb9daefeb0dc57ce15e6f73e9/raw/'


# Update on top of existing music-ex
def update_const_data():
    print_message(f"Fetch chart constants", 'H2', log=True)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'sort', 'date_added', generate_hash_from_keys)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    sgimera_js = _fetch_js_data(SGIMERA_URL)
    sgimera_data = _parse_sgimera_data(sgimera_js)

    total_diffs = [0]

    for song in target_song_list:
        _update_song_with_sgimera_data(song, sgimera_data, total_diffs)

        # Sort the song dictionary before saving
        sorted_song = sort_dict_keys(song)
        song.clear()  # Clear the original song dictionary
        song.update(sorted_song)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def _fetch_js_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


# Function to parse data from SGIMERA_URL
def _parse_sgimera_data(js_content):
    sgimera_data = []

    # Parse for legacy format (no decoding needed)
    if game.ARGS.legacy:
        entries = json.loads(js_content)

        for entry in entries:
            if len(entry['lv']) == 5 and entry['lv'][4] == '0':
                entry['lv'].pop(4)

            sgimera_data.append({
                "dx": int(entry['dx']),
                "v": int(entry['debut']),
                "lv": entry['lv'],
                "title": entry['name'],
                "ico": entry['ico'] if 'ico' in entry else None
            })
    else:
        # Regex to find the main dictionary data within the file
        in_lv_data = re.search(r"var in_lv = (\[.*?\]);", js_content, re.DOTALL)
        if not in_lv_data:
            return {}

        entries = re.finditer(
            r"\{dx:(\d+), v:(?:\s|)(\d+), lv:\[(.*?)\], n:`(.*?)`(?:, nn:`(.*?)`|), ico:`(.*?)`(?:, olv:(.*?)|)\}",
            in_lv_data.group(1)
        )

        for entry in entries:
            dx, version, levels, name, nn, ico, olv = entry.groups()

            levels = levels.split(", ")

            if len(levels) > 5 and levels[4] == '0':
                levels[4] = levels[5]
                levels.pop(5)

            sgimera_data.append({
                "dx": int(dx),
                "v": int(version),
                "lv": [int(log2(x)) if x > 0 and log2(x).is_integer() else -1 for x in map(int, levels)],
                "title": name,
                "ico": ico if ico else None
            })

    return sgimera_data

def _match_entry(target_entry, entry, song, dx_type=None):
    """Helper function to set entry details."""
    target_entry['title'] = entry['title']
    target_entry['ico'] = entry.get('ico')
    target_entry['dx'] = dx_type or entry['dx']

    if entry['dx'] == 0:
        target_entry['lv_std'] = entry['lv']
    elif entry['dx'] == 1:
        target_entry['lv_dx'] = entry['lv']

def _update_song_with_sgimera_data(song, sgimera_data, total_diffs):
    header_printed = [0]

    if 'lev_utage' in song:
        lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True, is_verbose=True)
        print_message(f"Skipping (utage)", bcolors.ENDC, log=True, is_verbose=True)

        return False

    # Format song image URL for comparison
    song_icon = os.path.splitext(song['image_url'])[0]



    # Find matching entry in sgimera_dict by title and icon
    target_entry = {}
    # Loop through sgimera_data to find a matching entry
    for entry in sgimera_data:
        if entry['title'] == song['title'] and (entry['ico'] == song_icon or entry['ico'] is None):
            # Check for dual type song
            if 'lev_bas' in song and 'dx_lev_bas' in song:
                if entry['ico'] is None:
                    lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                    print_message("Warning: matched song with just title", bcolors.WARNING, log=True)
                _match_entry(target_entry, entry, song, dx_type=2)

                # Break when both lv_std and lv_dx are set
                if 'lv_std' in target_entry and 'lv_dx' in target_entry:
                    break
            else:
                # Single type song
                if 'lev_bas' in song and entry['dx'] == 0:
                    if entry['ico'] is None:
                        lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                        print_message("Warning: matched song with just title", bcolors.WARNING, log=True)
                    _match_entry(target_entry, entry, song)
                    break
                elif 'dx_lev_bas' in song and entry['dx'] == 1:
                    if entry['ico'] is None:
                        lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                        print_message("Warning: matched song with just title", bcolors.WARNING, log=True)
                    _match_entry(target_entry, entry, song)
                    break

    if 'title' not in target_entry:
        return False  # No match found

    if 'lev_bas' in song and 'dx_lev_bas' in song:
        target_entry_lv = target_entry['lv_std'] + target_entry['lv_dx']
    elif 'dx_lev_bas' in song:
        target_entry_lv = target_entry['lv_dx']
    elif 'lev_bas' in song:
        target_entry_lv = target_entry['lv_std']

    for idx, modifier_num in enumerate(target_entry_lv):
        if modifier_num <= -1 or idx == 0: # Skip Basic
            continue

        if target_entry['dx'] == 2:
            chart_list = game.CHART_LIST + game.CHART_LIST_DX
        elif target_entry['dx'] == 1:
            chart_list = game.CHART_LIST_DX
        else:
            chart_list = game.CHART_LIST

        chart_key = chart_list[idx]

        # Skip if chart doesn't exist
        if chart_key not in song:
            continue

        if game.ARGS.legacy:
            chart_const = float(modifier_num)
        else:
            decimal_part = modifier_num
            base_level = float(song[chart_key].replace("+", ".6"))
            chart_const = (base_level * 10 + decimal_part) / 10

        chart_key += "_i"

        # If lev_xxx_i doesn't exist yet, create it:
        if chart_key not in song:
            total_diffs[0] += 1

            lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
            print_message(f"Added chart constant ({chart_key}: {chart_const})", bcolors.OKGREEN, log=True)

            song[chart_key] = str(chart_const)

            return True

        # If existing chart const is empty
        if song[chart_key] == "":
            total_diffs[0] += 1

            lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
            print_message(f"Updated chart constant ({chart_key}: {chart_const})", bcolors.OKGREEN, log=True)

            song[chart_key] = str(chart_const)  # Update song with the sgimera level constant

        # If there is already a value
        else:
            # previous value is different
            if song[chart_key] != str(chart_const):
                if game.ARGS.overwrite:
                    total_diffs[0] += 1
                    lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                    print_message(f"Overwrote chart constant ({chart_key}: {song[chart_key]} → {chart_const})", bcolors.WARNING, log=True)

                    song[chart_key] = str(chart_const)  # Update song with the sgimera level constant
                else:
                    lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True, is_verbose=True)
                    print_message(f"No change ({chart_key}: {chart_const})", bcolors.ENDC, log=True, is_verbose=True)
            # value is same
            else:
                lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True, is_verbose=True)
                print_message(f"No change ({chart_key}: {chart_const})", bcolors.ENDC, log=True, is_verbose=True)

    return True

