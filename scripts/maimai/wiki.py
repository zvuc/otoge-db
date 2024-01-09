import ipdb
import requests
import json
import re
import copy
import random
import time
# from selenium import webdriver
from shared.common_func import *
from maimai.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

wiki_base_url = 'https://gamerch.com/maimai/'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

VERSION_DATES = {
    "無印": "20150716",
    "PLUS": "20160204",
    "AIR": "20160825",
    "AIR+": "20170209",
    "STAR": "20170824",
    "STAR+": "20180308",
    "AMAZON": "20181025",
    "AMAZON+": "20190411",
    "CRYSTAL": "20191024",
    "CRYSTAL+": "20200716",
    "PARADISE": "20210121",
    "PARADISE×": "20210513",
    "NEW": "20211104",
    "NEW+": "20220414",
    "SUN": "20221013",
    "SUN+": "20230511",
    "LUMINOUS": "20231214"
}

CHART_LIST = {
   "lev_bas",
   "lev_adv",
   "lev_exp",
   "lev_mas",
   "lev_remas"
}

CHART_LIST_DX = {
   "dx_lev_bas",
   "dx_lev_adv",
   "dx_lev_exp",
   "dx_lev_mas",
   "dx_lev_remas"
}

CHART_COLORS = {
   "lev_bas": "98fb98",
   "dx_lev_bas": "98fb98",
   "lev_adv": "ffa500",
   "dx_lev_adv": "ffa500",
   "lev_exp": "fa8080",
   "dx_lev_exp": "fa8080",
   "lev_mas": "ee82ee",
   "dx_lev_mas": "ee82ee",
   "lev_remas": "ffceff",
   "dx_lev_remas": "ffceff",
   "lev_utage": "ff5296"
}

# Update on top of existing music-ex
def update_songs_extra_data(args):
    print_message(f"Fetching latest wiki data.", bcolors.ENDC, args)
    
    date_from = args.date_from
    date_until = args.date_until
    song_id = args.id

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # prioritize id search if provided
    if not song_id == 0:
        if '-' in song_id:
            id_from = song_id.split('-')[0]
            id_to = song_id.split('-')[-1]
            target_song_list = _filter_songs_by_id_range(local_music_ex_data, id_from, id_to)
        else:
            target_song_list = _filter_songs_by_id(local_music_ex_data, song_id)
    else:
        latest_date = int(get_last_date(LOCAL_MUSIC_EX_JSON_PATH))

        if date_from == 0:
            date_from = latest_date

        if date_until == 0:
            date_until = latest_date

        target_song_list = _filter_songs_by_date(local_music_ex_data, date_from, date_until)


    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    f = open("diffs.txt", 'w')

    for song in target_song_list:
        _update_song_wiki_data(song, args)

        # time.sleep(random.randint(1,2))

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


def _filter_songs_by_id(song_list, song_id):
    target_song_list = []

    for song in song_list:
        if int(song_id) == int(song.get("sort")):
            target_song_list.append(song)

    return target_song_list


def _update_song_wiki_data(song, args):
    print_message(f"{song['sort']} {song['title']}", bcolors.ENDC, args)

    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
        .replace('"', '”')
    )
    
    # use existing URL if already present
    if 'wiki_url' in song and song['wiki_url']:
        url = song['wiki_url']
        wiki = requests.get(url, timeout=1, headers=request_headers, allow_redirects=True)

        return _parse_wikiwiki(song, wiki, url, args)

        # Skip if URL present
        # print_message("(Skipping)", bcolors.ENDC, args)

    # If not, guess URL from title
    else:
        # guess_url = wiki_base_url + title

        guess_url = f'https://www.google.com/search?hl=en&q={title}%20maimai%E3%80%80%E6%94%BB%E7%95%A5wiki&btnI=I'
        search_results = requests.get(guess_url, timeout=1)

        if not search_results.ok:
            # give up
            print_message("failed to guess wiki page", bcolors.FAIL, args)
            return song

        else:
            # don't save just yet...
            # url = guess_url
            search_results_soup = BeautifulSoup(search_results.text, 'html.parser')
            href_values = [a['href'] for a in search_results_soup.find_all('a') if 'href' in a.attrs]

            # Extract the URLs starting with the specified prefix
            extracted_urls = [re.search(r'(?<=url\?q=)([^&]+)', href).group(1) for href in href_values if re.search(r'(?<=url\?q=)([^&]+)', href)]

            # Filter URLs that start with the specified prefix
            filtered_urls = [url for url in extracted_urls if url.startswith('https://gamerch.com/maimai/entry/')]
            first_matched_url = filtered_urls[0] if filtered_urls else None

            if first_matched_url:
                wiki = requests.get(first_matched_url, timeout=1, headers=request_headers, allow_redirects=True)
                print_message("Found URL by guess!", bcolors.OKBLUE, args)
                return _parse_wikiwiki(song, wiki, first_matched_url, args)
            else:
                print_message("failed to guess wiki page", bcolors.FAIL, args)
                return song


def _parse_wikiwiki(song, wiki, url, args):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("body .main table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', id_='notes'):
        if '*' in footnotes.get_text(strip=True):
            footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        print_message("Parse failed! Skipping song", bcolors.FAIL, args)
        return song

    # ipdb.set_trace()

    has_std_chart = 'lev_bas' in song
    has_dx_chart = 'dx_lev_bas' in song
    has_utage_chart = 'lev_utage' in song
    has_dual_chart = has_std_chart and has_dx_chart
    has_single_chart = (has_std_chart and not has_dx_chart) or (has_dx_chart and not has_std_chart)

    # find the overview table
    overview_table = None

    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            first_row = rows[0].find(lambda tag: tag.name in ['td'],{'rowspan': True})
            if first_row and first_row.find('img'):
                second_row = rows[1].find('th')
                if second_row and second_row.get_text(strip=True) == 'ジャンル':
                    overview_table = table
                    break

    if overview_table:
        overview_heads = overview_table.select('th')
        overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text if data else None for data in overview_data]
        overview_dict = dict(zip(overview_heads, overview_data))

        
        # Write date and guess version
        if 'kanji' not in song:
            # Find release date
            formatted_date = ''
            if '初期' in overview_dict["配信日"]:
                formatted_date = '20121107' # maimai launch date
            else:
                release_dates = overview_dict["配信日"]
                earliest_release_date = re.search(r'\b\d{4}/\d{1,2}/\d{1,2}', release_dates)
                if earliest_release_date:
                    earliest_release_date = earliest_release_date.group()
                    date_num_parts = earliest_release_date.split('/')
                    formatted_date = '{:04d}{:02d}{:02d}'.format(int(date_num_parts[0]), int(date_num_parts[1]), int(date_num_parts[2]))

            if not formatted_date == '':
                diff_count = [0]
                _update_song_key(song, 'date', formatted_date, diff_count=diff_count)
                _update_song_key(song, 'version', _guess_version(formatted_date), diff_count=diff_count)
                
                if diff_count[0] > 0:
                    print_message("Added date and version", bcolors.OKGREEN, args)
            else:
                # fail
                print_message("Warning - date not found", bcolors.WARNING, args)
        else:
            # Skip for Utage
            print_message("Skipped date (Utage)", bcolors.WARNING, args)

        # Update BPM
        if overview_dict['BPM']:
            diff_count = [0]
            _update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

            if diff_count[0] > 0:
                print_message("Added BPM", bcolors.OKGREEN, args)
    else:
        # fail
        print_message("Warning - overview table not found", bcolors.FAIL, args)

    # find the charts table
    charts_table = None
    charts_table_dx = None
    charts_data = []
    for table in tables:
        th_elements = table.select('tr:nth-of-type(1) td[rowspan], tr:nth-of-type(1) th[rowspan]')

        if len(th_elements) in (2, 3) and th_elements[0].get_text(strip=True) == 'Lv' and th_elements[-1].get_text(strip=True) == '総数':
            charts_table_head = [th.text for th in table.select("thead th:not([colspan]), thead td:not([colspan])")]
            
            if any(charts_table_head) and 'Lv' in charts_table_head[0]:
                # DX chart table
                if 'Touch' in charts_table_head[5:7]:
                    charts_table_dx = table
                    charts_table_head_dx = charts_table_head
                # Standard chart table
                else:
                    charts_table = table
    
    if has_std_chart and charts_table is None:
        print_message("Warning - No Std chart table found", bcolors.FAIL, args)
    if has_dx_chart and charts_table_dx is None:
        print_message("Warning - No DX chart table found", bcolors.FAIL, args)
    if (has_dual_chart or has_utage_chart) and charts_table is None and charts_table_dx is None:
        print_message("Warning - No chart table found", bcolors.FAIL, args)


    # Find constant and chart designer
    chart_designers_text = None
    chart_designers_spans = soup.find_all('span', style='font-size:11px')
    chart_designers_dict = {}

    # count total numbers of designer dicts needed
    if has_std_chart and has_dx_chart:
        req_dict_count = 2
    elif has_single_chart or has_utage_chart:
        req_dict_count = 1

    
    for chart_designers_span in chart_designers_spans:
        chart_designers_span_text = chart_designers_span.get_text(strip=True)

        # Count number of text in brackets
        brackets_count = len(re.compile(r'【(.*?)】').findall(chart_designers_span_text))

        if brackets_count == 0:
            continue

        # Just one bracket in span
        elif brackets_count == 1:
            # Find if it's either designer or constants
            # Designer
            if '譜面作者【' in chart_designers_span_text:
                match = re.search(r'【(BAS|ADV|EXP|MST|Re:M)(…|[.]{3})(.*?)】',chart_designers_span_text)

                if match is not None:
                    chart_designers_text = chart_designers_span_text
                    # chart_designers_dict = _construct_designers_dict(song, chart_designers_text, 'designer')

                    # Check if the DX chart table is directly in front
                    if charts_table_dx is not None and charts_table_dx == chart_designers_span.find_previous().find_previous('div', {'class':"mu__table"}).find('table'):
                        chart_designers_dict_dx = _construct_designers_dict(song, chart_designers_text, 'designer', 'dx_')
                        req_dict_count-=1

                    # Check if the Std chart table is directly in front
                    if charts_table is not None and charts_table == chart_designers_span.find_previous().find_previous('div', {'class':"mu__table"}).find('table'):
                        chart_designers_dict = _construct_designers_dict(song, chart_designers_text, 'designer', '')
                        req_dict_count-=1

                elif match is None and 'kanji' in song:
                    # Song is WE only
                    chart_designers_text = chart_designers_span_text
                    match = re.search(r'【(.*?)】', chart_designers_text)
                    if match:
                        match = match.group(1)
                        chart_designers_dict = {f"lev_{song['kanji']}_designer": match}
                        req_dict_count-=1

            if req_dict_count == 0:
                break
                

            # Constants
            # if '譜面定数【' in chart_designers_span_text:
            #     # match = re.search(r'【(.*?)】', chart_designers_span_text).group(1)
            #     match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(\d{2}\.\d)(.*)】',chart_designers_span_text)

            #     if re.match(r'\d{2}\.\d', match.group(3)) is not None:
            #         chart_constants_text = chart_designers_span_text
            #         chart_constants_dict = _construct_designers_dict(song, chart_constants_text, 'i')
            #         break
        else:
            print_message(f"Warning - No designer/constant info found ({chart.upper()})", bcolors.WARNING, args)
            



    # Update chart details
    if charts_table:
        for chart_type in CHART_LIST:
            if chart_type in song:
                _process_chart(song, chart_type, CHART_COLORS[chart_type], charts_table, charts_table_head, chart_designers_dict, args)
        
        if 'kanji' in song:
            # Find with color
            # utage_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and 'white' in tag.get('style', ''))
            # Find with text
            utage_rows = charts_table.find_all(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["lev_utage"]}' in tag.get('style', ''))
            for utage_row in utage_rows:
                if song['kanji'] in utage_row.get_text(strip=True) and song['lev_utage'] in utage_row.get_text(strip=True):
                    utage_row_parent = utage_row.find_parent()
                    for br_tag in utage_row_parent.find_all('br'):
                        br_tag.decompose()
                    utage_data = [cell.text for cell in utage_row_parent]
                    utage_data_dict = dict(zip(charts_table_head, utage_data))
                    _update_song_chart_details(song, utage_data_dict, chart_designers_dict, 'utage', args)

    if charts_table_dx:
        for chart_type in CHART_LIST_DX:
            if chart_type in song:
                _process_chart(song, chart_type, CHART_COLORS[chart_type], charts_table_dx, charts_table_head_dx, chart_designers_dict_dx, args)
        
        if 'kanji' in song:
            # Find with color
            # utage_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and 'white' in tag.get('style', ''))
            # Find with text
            utage_row = charts_table.find(text=song['kanji']).find_parent(lambda tag: tag.name in ['th','td'] and f'{CHART_COLORS["lev_utage"]}' in tag.get('style', ''))
            
            if utage_row and song['kanji'] in utage_row.get_text(strip=True) and song['lev_utage'] in utage_row.get_text(strip=True):
                utage_row_parent = utage_row.find_parent()
                for br_tag in utage_row_parent.find_all('br'):
                    br_tag.decompose()
                utage_data = [cell.text for cell in utage_row_parent]
                utage_data_dict = dict(zip(charts_table_head, utage_data))
                _update_song_chart_details(song, utage_data_dict, chart_designers_dict_dx, 'utage', args)


    if song['wiki_url'] != url:
        song['wiki_url'] = url
        print_message("Saved wiki URL", bcolors.OKBLUE, args)

    if old_song == song:
        print_message("Done (Nothing updated)", bcolors.ENDC, args)
    # else:
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN, args)

    return song


def _process_chart(song, chart_type, chart_color, charts_table, charts_table_head, chart_designers_dict, args):
    row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{chart_color}' in tag.get('style', ''))
    if row:
        row = row.find_parent()
        data = [cell.text for cell in row]
        data_dict = dict(zip(charts_table_head, data))
        _update_song_chart_details(song, data_dict, chart_designers_dict, chart_type, args)


def _update_song_chart_details(song, chart_dict, chart_designers_dict, chart, args):
    # ipdb.set_trace()
    diff_count = [0]
    if '定数' in chart_dict:
        _update_song_key(song, f"{chart}_i", chart_dict["定数"], remove_comma=True, diff_count=diff_count)

    _update_song_key(song, f"{chart}_notes", chart_dict["総数"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"{chart}_notes_tap", chart_dict["Tap"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"{chart}_notes_hold", chart_dict["Hold"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"{chart}_notes_slide", chart_dict["Slide"], remove_comma=True, diff_count=diff_count)

    if 'Touch' in chart_dict:
        _update_song_key(song, f"{chart}_notes_touch", chart_dict["Touch"], remove_comma=True, diff_count=diff_count)

    _update_song_key(song, f"{chart}_notes_break", chart_dict["Break"], remove_comma=True, diff_count=diff_count)

    if chart_designers_dict:
        # in some cases 宴 may be labled as 宴2 or 宴[即]..
        # 宴2 : Garakuta Doll Play https://gamerch.com/maimai/entry/533459
        # 宴[即] : ジングルベル https://gamerch.com/maimai/entry/533569
        if chart == 'lev_utage':
            try:
                designer_key = chart_designers_dict[f"{chart}_designer"]
                _update_song_key(song, f"{chart}_designer", chart_designers_dict[f"{chart}_designer"], diff_count=diff_count)
            except KeyError:
                try:
                    # try alternative syntax
                    designer_key = [key for key in chart_designers_dict if song['kanji'] in key][0]
                    _update_song_key(song, f"{chart}_designer", chart_designers_dict[designer_key], diff_count=diff_count)
                except:
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, args)
        # Convert REMAS to RE:M
        elif chart == 'lev_remas':
            try:
                _update_song_key(song, f"{chart}_designer", chart_designers_dict["lev_re:m_designer"], diff_count=diff_count)
            except KeyError:
                print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, args)
        else:
            try:
                _update_song_key(song, f"{chart}_designer", chart_designers_dict[f"{chart}_designer"], diff_count=diff_count)
            except:
                if chart not in ('lev_bas', 'lev_adv', 'dx_lev_bas', 'dx_lev_adv'):
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, args)
    
    if not chart == 'lev_utage' and chart_designers_dict:
        try:
            if re.search(r'(\d{2}\.\d)',chart_designers_dict[f"{chart}_i"]):
                _update_song_key(song, f"{chart}_i", chart_designers_dict[f"{chart}_i"], diff_count=diff_count)
            else:
                raise Exception(f"Constant for {chart.upper()} is invalid")
        except:
            if chart not in ('bas', 'adv'):
                print_message(f"Warning - No constant found ({chart.upper()})", bcolors.WARNING, args)

    if diff_count[0] > 0:
        print_message(f"Added chart details for {chart.upper()}", bcolors.OKGREEN, args)


def _update_song_key(song, key, new_data, remove_comma=False, diff_count=None):
    # if source key doesn't exist, exit
    if key not in song:
        return
    # if source is not empty, don't overwrite
    if not (song[key] == ''):
        return
    # Only overwrite if new data is not empty and is not same
    if not (new_data == '') and not (song[key] == new_data) and not (new_data == "??") and not (new_data == "???") and not (new_data == '-'):
        diff_count[0] += 1
        song[key] = new_data

        if remove_comma:
            song[key] = song[key].replace(',', '')
        
        return

def _construct_designers_dict(song, text, key_name, prefix=''):
    # Use regular expression to find content within brackets
    match = re.search(r'【(.*?)】', text)

    if match:
        content_within_brackets = '【' + match.group(1)
        
        # Split key-value pairs using '、' as the delimiter
        pairs = {}
        if 'kanji' in song:
            pattern = re.compile(fr'[、【](?=EXP|MST|Re:M|{re.escape(song["kanji"])})')
        else:
            pattern = re.compile(r'[、【](?=EXP|MST|Re:M)')
        pairs = re.split(pattern, content_within_brackets)
        pairs = [item for item in pairs if item]

        # Separate key and value using '…' and construct a dictionary
        dictionary = {}
        for pair in pairs:
            if '…' in pair:
                key, value = pair.split('…', 1)
            elif '...' in pair:
                key, value = pair.split('...', 1)
            dictionary[key] = value

        # transform key names into lev_{chart} format
        formatted_dict = {}
        for key, value in dictionary.items():
            if key.lower() == 'mst':
                key = 'mas'
            formatted_key = f"{prefix}lev_{key.lower()}_{key_name}"
            formatted_dict[formatted_key] = value
        return formatted_dict
    else:
        return None

def _guess_version(release_date):
    closest_version = None
    closest_difference = float('inf')

    for version, version_date in VERSION_DATES.items():
        difference = int(release_date) - int(version_date)

        if 0 <= difference < closest_difference:
            closest_difference = difference
            closest_version = version

    return closest_version

