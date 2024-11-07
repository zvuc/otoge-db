# import ipdb
import requests
import json
import os
import re
from bs4 import BeautifulSoup
from shared.common_func import *
from maimai.paths import *
from datetime import datetime

SGIMERA_URL = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_data_prism.js'
SGIMERA_DICT_URL = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_prism_.js'

# Update on top of existing music-ex
def update_const_data():
    print_message(f"Fetch chart constants", 'H2', log=True)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added', game.HASH_KEYS)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    sgimera_js = fetch_js_data(SGIMERA_URL)
    sgimera_data = parse_sgimera_data(sgimera_js)

    sgimera_dict_js = fetch_js_data(SGIMERA_DICT_URL)
    sgimera_dict = parse_sgimera_dict(sgimera_dict_js)


    for song in target_song_list:
        update_song_with_sgimera_data(song, sgimera_data, sgimera_dict)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

def fetch_js_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Function to parse data from SGIMERA_URL
def parse_sgimera_data(js_content):
    # Regex to match each level result constant (lvxx_rslt)
    pattern = re.compile(r"const lv(\d+)_rslt = (\[.*?\]);", re.DOTALL)
    matches = pattern.findall(js_content)

    sgimera_data = {}

    # Iterate over each match (lvxx_rslt)
    for base_level, chart_data in matches:
        base_level = int(base_level)  # Convert base level to integer
        chart_lists = eval(chart_data)  # Evaluate the array for lists of songs

        # Determine decimal level values based on the length of each chart_list
        max_decimal_level = len(chart_lists) - 1

        for idx, chart_list in enumerate(chart_lists):
            decimal_level = max_decimal_level - idx  # Calculate the decimal level
            level_constant = f"{base_level}.{decimal_level}"

            # Parse each entry in the chart list
            for song_html in chart_list:
                # Extract chart type and song title
                match = re.search(r"<span class='(wk_[a-z]+)(?:_n)?'>\s*([^<]+)\s*</span>", song_html)
                if not match:
                    continue

                chart_class, song_title = match.groups()

                # Determine chart type suffix based on class name
                if chart_class.startswith("wk_m"):
                    chart_suffix = "lev_mas_i"
                elif chart_class.startswith("wk_r"):
                    chart_suffix = "lev_remas_i"
                elif chart_class.startswith("wk_e"):
                    chart_suffix = "lev_exp_i"
                elif chart_class.startswith("wk_a"):
                    chart_suffix = "lev_adv_i"
                else:
                    continue

                # Handle [dx] suffix in song title
                if "[dx]" in song_title:
                    song_title = song_title.replace("[dx]", "").strip()
                    chart_suffix = f"dx_{chart_suffix}"

                # Prepare data dictionary entry
                if song_title not in sgimera_data:
                    sgimera_data[song_title] = {"title": song_title}

                # Add level constant for the appropriate chart type
                sgimera_data[song_title][chart_suffix] = level_constant

    return sgimera_data

# Function to parse data from SGIMERA_DICT_URL
def parse_sgimera_dict(js_content):
    sgimera_dict = []

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

        # Handle missing fields by assigning them a default value
        entry_data = {
            "dx": int(dx),
            "v": int(version),
            "title": nn if nn else name,
            "ico": ico if ico else None
        }

        sgimera_dict.append(entry_data)

    return sgimera_dict

def update_song_with_sgimera_data(song, sgimera_data, sgimera_dict):
    header_printed = [0]
    # Format song image URL for comparison
    song_icon = os.path.splitext(song['image_url'])[0]

    # Find matching entry in sgimera_dict by title and icon
    target_entry = None
    for entry in sgimera_dict:
        if entry['ico'] == song_icon:
            target_entry = entry
            break

    if not target_entry:
        return False  # No match found

    # Update song with matching sgimera_data
    title_key = target_entry['title']
    if title_key in sgimera_data:
        sgimera_entry = sgimera_data[title_key]
        for key, level in sgimera_entry.items():
            if key == "title":
                continue  # Skip the title field in sgimera_entry

            chart_base = key.split('_i')[0]  # e.g., dx_lev_adv_i -> dx_lev_adv
            song_level_key = chart_base  # Expected level key in song

            # Check if song has the chart level key
            if song_level_key in song:
                song_chart_level = song[song_level_key]

                # Convert sgimera_level_constant to "chart level form"
                sgimera_level_constant = float(level)
                base_level = int(sgimera_level_constant)  # Drop the decimal
                decimal_part = sgimera_level_constant - base_level

                # Format sgimera level according to the specified chart level form
                if decimal_part >= 0.6:
                    sgimera_chart_level_form = f"{base_level}+"
                else:
                    sgimera_chart_level_form = str(base_level)

                # Compare song_chart_level and formatted sgimera level as strings
                if sgimera_chart_level_form == song_chart_level:
                    if key not in song or not song[key]:
                        lazy_print_song_header(f"{song['sort']}, {song['title']}, {song['version']}", header_printed, log=True)
                        print_message(f"Updated chart constant ({song_level_key}: {level})", bcolors.OKGREEN, log=True)

                        song[key] = level  # Update song with the sgimera level constant

    return True

