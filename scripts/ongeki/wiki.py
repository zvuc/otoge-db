# import ipdb
import requests
import json
import copy
import random
import time
from shared.common_func import *
from ongeki.paths import *
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'
SDVXIN_BASE_URL = 'https://sdvx.in/'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

TARGET_KEYS = [
    "bpm",
    "lev_bas_notes",
    "lev_bas_bells",
    "lev_adv_notes",
    "lev_adv_bells",
    "lev_exc_notes",
    "lev_exc_bells",
    "lev_mas_notes",
    "lev_mas_bells",
    "_exp_designer",
    "_mas_designer"
]

TARGET_KEYS_LNT = [
    "bpm",
    "lev_lnt_notes",
    "lev_lnt_bells",
    "_lnt_designer",
]

# Update on top of existing music-ex
def update_songs_extra_data():
    print_message(f"Fetch latest wiki data", 'H2', log=True)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added')

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    total_diffs = [0]

    for song in target_song_list:
        update_song_wiki_data(song, total_diffs)

        _fetch_designer_info_from_sdvxin(song, total_diffs)

    sort_and_save_json(local_music_ex_data, LOCAL_MUSIC_EX_JSON_PATH)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def update_song_wiki_data(song, total_diffs):
    header_printed = [0]

    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
        .replace('"', '”')
        .replace('?', '？')
    )

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        if game.ARGS.noskip:
            # Check if any values are empty
            if (
                any(
                    value == ""
                    for key, value in song.items()
                    if any(
                        target in key
                        for target in (
                            TARGET_KEYS_LNT if song.get("lunatic", "") != ""
                            else TARGET_KEYS
                        )
                    )
                )
                or game.ARGS.overwrite
            ):
                url = song['wikiwiki_url']
                try:
                    wiki = requests.get(url, timeout=5, headers=request_headers, allow_redirects=True)
                    _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)
                    # Give some time before continuing
                    time.sleep(random.randint(1,2))
                    return
                except requests.RequestException as e:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                    print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True)
                    return song
            else:
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("(Skipping - all data already present)", bcolors.ENDC, log=True, is_verbose=True)
        else:
            # Skip if URL present
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("(Skipping - URL already exists)", bcolors.ENDC, log=True, is_verbose=True)

    # If not, guess URL from title
    else:
        guess_url = wiki_base_url + title
        wiki = requests.get(guess_url, timeout=5, headers=request_headers, allow_redirects=True)

        if not wiki.ok:
            # try replacing special character as fallback
            title = title.replace('\'', '’')
            guess_url = wiki_base_url + title
            wiki = requests.get(guess_url, timeout=5, headers=request_headers, allow_redirects=True)

            if not wiki.ok:
                # give up!
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                print_message("Failed to guess wiki page", bcolors.FAIL, log=True)
                return song

            else:
                url = guess_url
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Found URL by guess!", bcolors.OKBLUE, log=True, is_verbose=True)
                return _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)
                
        else:
            url = guess_url
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Found URL by guess!", bcolors.OKBLUE, log=True, is_verbose=True)
            return _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)


def _parse_wikiwiki(song, wiki, url, total_diffs, header_printed):
    critical_errors = [0]

    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', class_='tooltip'):
        footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Wiki page not found - invalid page", bcolors.FAIL, log=True)
        critical_errors[0] += 1
        return song

    # find the overview table
    overview_table = None
    
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            second_row_th = rows[1].find('th')
            if second_row_th and second_row_th.get_text(strip=True) == 'タイトル':
                img_in_first_col = rows[0].find('td',{'rowspan': True})
                if img_in_first_col:
                    overview_table = table
                    break

    if overview_table:
        overview_heads = overview_table.select('th')

        if song['lunatic'] == '1':
            overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]
        else:
            overview_data = [head.find_parent('tr').select('td:not([rowspan])') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text for data in overview_data]
        overview_dict = dict(zip(overview_heads, overview_data))

        # Find enemy lv data
        if 'LV.' in overview_dict["対戦相手"].upper():
            enemy_info = overview_dict["対戦相手"].upper().split("LV.")
            enemy_name = enemy_info[0]
            enemy_lv = enemy_info[1]

            if enemy_lv and enemy_lv.isdigit():
                diff_count = [0]
                update_song_key(song, 'enemy_lv', enemy_lv, diff_count=diff_count)

                if diff_count[0] > 0:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                    print_message("Added Enemy Lv", bcolors.OKGREEN, log=True)


            # If character name includes type info, use it
            for enemy_type in game.ENEMY_TYPES:
                diff_count = [0]

                if enemy_type in enemy_name:
                    default_overwrite = game.ARGS.overwrite
                    game.ARGS.overwrite = True
                    update_song_key(song, 'enemy_type', enemy_type, diff_count=diff_count)

                    game.ARGS.overwrite = default_overwrite

                    if diff_count[0] > 0:
                        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                        print_message("Updated enemy type", bcolors.OKGREEN, log=True)
                        break

        else:
            # fail
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Warning - enemy lv not found", bcolors.WARNING, log=True, is_verbose=True)
            
    else:
        # fail
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - no overview table", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1


    # find the charts table
    charts_table = None
    for table in tables:
        th_elements = table.select('th:nth-of-type(1), th:nth-of-type(2)')
        if len(th_elements) > 2 and th_elements[0].get_text(strip=True) == '難易度' and th_elements[1].get_text(strip=True) == '楽曲Lv':
            charts_table = table
            break
    
    # Update chart details
    if charts_table:
        charts_table_head = [th.text for th in charts_table.select("thead th")]
        charts_data = [[cell.text for cell in chart.select("th,td")] for chart in charts_table.select("tbody tr")]

        if any(charts_table_head) and '難易度' in charts_table_head[0]:
            for chart_details in charts_data:
                chart_dict = dict(zip(charts_table_head, chart_details))

                if song['lunatic'] == '' and chart_dict['難易度'] == 'BASIC':
                    _update_song_chart_details(song, chart_dict, 'bas', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'ADVANCED':
                    _update_song_chart_details(song, chart_dict, 'adv', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'EXPERT':
                    _update_song_chart_details(song, chart_dict, 'exc', header_printed)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'MASTER':
                    _update_song_chart_details(song, chart_dict, 'mas', header_printed)
                elif song['lunatic'] == '1' and chart_dict['難易度'] == 'LUNATIC':
                    _update_song_chart_details(song, chart_dict, 'lnt', header_printed)
        else:
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
            print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True)
            critical_errors[0] += 1
    else:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True)
        critical_errors[0] += 1
    
    # Update BPM
    if overview_dict['BPM']:
        diff_count = [0]
        update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

        if diff_count[0] > 0:
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
            print_message("Added BPM", bcolors.OKGREEN, log=True)

    if ('wikiwiki_url' not in song or song['wikiwiki_url'] != url) and critical_errors[0] == 0:
        song['wikiwiki_url'] = url
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Saved wiki URL", bcolors.OKBLUE)

    if old_song == song:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Done (Nothing updated)", bcolors.ENDC, log=True, is_verbose=True)
    else:
        total_diffs[0] += 1
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN)

    return song


def _update_song_chart_details(song, chart_dict, chart, header_printed):
    details_diff_count = [0]
    designer_diff_count = [0]
    update_song_key(song, f"lev_{chart}_notes", chart_dict["総ノート数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_bells", chart_dict["BELL"], remove_comma=True, diff_count=details_diff_count)
    # update_song_key(song, f"lev_{chart}_i", chart_dict["譜面定数"], diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN)

    update_song_key(song, f"lev_{chart}_designer", chart_dict["譜面製作者"], diff_count=designer_diff_count)

    if designer_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN)


def _fetch_designer_info_from_sdvxin(song, total_diffs):
    """
    Update song dict with missing designer info by scraping sdvx.in chart pages.
    Only works for lev_exc, lev_mas, lev_lnt based on song type and current designer info.
    """
    chart_map = {
        'lev_exc': 'E',
        'lev_mas': 'M',
        'lev_lnt': 'L',
    }

    # Determine target charts
    is_lunatic = song.get('lunatic') == '1'
    if is_lunatic:
        target_charts = ['lev_lnt']
    else:
        target_charts = ['lev_exc', 'lev_mas']

    for chart in target_charts:
        designer_key = f"{chart}_designer"
        chart_link_key = f"{chart}_chart_link"

        # Skip if already has designer info or no chart link
        if song.get(designer_key):
            continue

        print_message(f"Fetch missing designer info for {chart.upper()} from sdvx.in", bcolors.OKBLUE, is_verbose=True)

        chart_link = song.get(chart_link_key)
        if not chart_link:
            print_message(f"Skipping: there is no chart link", bcolors.ENDC, is_verbose=True)
            continue

        # Extract version number and song ID
        match = re.match(r'(\d{2})/(\d{5})[a-z]{3}', chart_link)
        if not match:
            print_message(f"Parsing ID from chart link failed", bcolors.FAIL, is_verbose=True)
            continue  # invalid format
        version_num, song_id = match.groups()

        # Construct URL
        url = f"{SDVXIN_BASE_URL}{game.GAME_NAME}/{version_num}/js/{song_id}sort.js"

        try:
            resp = requests.get(url)
            resp.encoding = 'ansi'
            content = resp.text
        except Exception:
            print_message(f"Failed to load page", bcolors.FAIL)
            continue  # skip on any error

        # Check validity
        lines = content.strip().splitlines()
        lines = [line.lstrip('\ufeff') for line in lines]

        # Validate that expected declarations are present anywhere in the first 10 lines
        head = lines[:10]
        has_title = any(re.match(r'^var TITLE\d+ *=', line) for line in head)
        has_artist = any(re.match(r'^var ARTIST\d+ *=', line) for line in head)
        has_bpm = any(re.match(r'^var BPM\d+ *=', line) for line in head)
        has_cr = any(re.match(rf'^var CR{song_id}', line) for line in head)

        # ipdb.set_trace()

        if not (has_title and has_artist and has_bpm and has_cr):
            continue

        # Parse designer info
        suffix = chart_map[chart]
        cr_key = f"var CR{song_id}{suffix}"
        for line in lines:
            if line.startswith(cr_key):
                # Extract designer name
                m = re.search(r'NOTES DESIGNER / ([^<]+)</table>', line)
                if m:
                    song[designer_key] = m.group(1).strip()
                    print_message(f"Added chart designer for {chart.upper()}: {song[designer_key]}", bcolors.OKGREEN)
                    total_diffs[0] += 1
                break  # stop after finding the correct one

