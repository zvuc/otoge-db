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

# SGIMERA_URL = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_data_prism.js'
SGIMERA_URL = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_prism_.js'

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

    sgimera_js = fetch_js_data(SGIMERA_URL)
    sgimera_data = parse_sgimera_data(sgimera_js)

    total_diffs = [0]

    for song in target_song_list:
        update_song_with_sgimera_data(song, sgimera_data, total_diffs)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def fetch_js_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


# Function to parse data from SGIMERA_URL
def parse_sgimera_data(js_content):
    sgimera_data = {}

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

        sgimera_data[name] = {
            "dx": int(dx),
            "v": int(version),
            "lv": [int(log2(x)) if x > 0 and log2(x).is_integer() else -1 for x in map(int, levels)],
            "title": name,
            "ico": ico if ico else None
        }


    return sgimera_data

chart_suffixes = {
    1: "lev_adv",
    2: "lev_exp",
    3: "lev_mas",
    4: "lev_remas"
}
def update_song_with_sgimera_data(song, sgimera_data, total_diffs):
    header_printed = [0]

    if 'lev_utage' in song:
        lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True, is_verbose=True)
        print_message(f"Skipping (utage)", bcolors.ENDC, log=True, is_verbose=True)

        return False

    # Format song image URL for comparison
    song_icon = os.path.splitext(song['image_url'])[0]

    # Find matching entry in sgimera_dict by title and icon
    target_entry = None
    for title, entry in sgimera_data.items():
        if entry['ico'] == song_icon:
            target_entry = entry
            break

    if not target_entry:
        return False  # No match found

    for idx, decimal_part in enumerate(target_entry['lv']):
        if decimal_part == -1 or idx == 0: # Skip Basic
            continue

        chart_key = chart_suffixes[idx]

        if target_entry['dx'] == 1:
            chart_key = f"dx_{chart_key}"

        base_level = float(song[chart_key].replace("+", ".6"))
        chart_const = (base_level * 10 + decimal_part) / 10

        chart_key += "_i"

        if chart_const is not None:
            # ipdb.set_trace()
            if chart_key in song and song[chart_key] == str(chart_const):
                lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True, is_verbose=True)
                print_message(f"No change ({chart_key}: {chart_const})", bcolors.ENDC, log=True, is_verbose=True)
            else:
                total_diffs[0] += 1

                lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                print_message(f"Updated chart constant ({chart_key}: {chart_const})", bcolors.OKGREEN, log=True)

                song[chart_key] = str(chart_const)  # Update song with the sgimera level constant

    return True

