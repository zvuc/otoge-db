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

TARGET_KEYS = [
    "bpm",
    "_notes",
    "_designer"
]

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
def update_songs_extra_data():
    print_message(f"Fetch latest wiki data", 'H2', log=True)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'sort', 'date_added', generate_hash_from_keys)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    total_diffs = [0]

    for song in target_song_list:
        update_song_wiki_data(song, total_diffs)

        # Sort the song dictionary before saving
        sorted_song = sort_dict_keys(song)
        song.clear()  # Clear the original song dictionary
        song.update(sorted_song)

        # time.sleep(random.randint(1,2))

        with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

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
    if 'wiki_url' in song and song['wiki_url']:
        if game.ARGS.noskip:
            # Check if any values are empty from target keys
            # but excluding lev_utage_notes_touch
            if (
                any(
                    value == ""
                    for key, value in song.items()
                    if any(target in key for target in TARGET_KEYS) and key != "lev_utage_notes_touch"
                )
                or game.ARGS.overwrite
            ):
                url = song['wiki_url']
                try:
                    wiki = requests.get(url, timeout=5, headers=request_headers, allow_redirects=True)
                    return _parse_wikiwiki(song, wiki, url, total_diffs, header_printed)
                except requests.RequestException as e:
                    lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
                    print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True)
                    return song
            else:
                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("(Skipping - all data already present)", bcolors.ENDC, log=True, is_verbose=True)

        else:
            # Skip if URL present
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("(Skipping - URL already exists)", bcolors.ENDC, log=True, is_verbose=True)

    # If not, guess URL from title
    else:
        # guess_url = wiki_base_url + title
        if 'lev_utage' in song and song["title"].startswith(f"[{song['kanji']}]"):
            stripped_utage_title = song["title"][len(song['kanji']) + 2:].strip()
            normalized_utage_title = (
                stripped_utage_title
                .replace('&', '＆')
                .replace(':', '：')
                .replace('[', '［')
                .replace(']', '］')
                .replace('#', '＃')
                .replace('"', '”')
                .replace('?', '？')
            )
            search_title = normalized_utage_title.replace('-',' ')
        else:
            search_title = title.replace('-',' ')
        guess_url = f'https://www.google.com/search?hl=en&q="{search_title}"+site%3Agamerch.com%2Fmaimai&btnI=I'
        try:
            search_results = requests.get(guess_url, timeout=5)
        except requests.RequestException as e:
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
            print_message(f"Error while loading Google Search results: {e}", bcolors.FAIL, log=True)
            return song

        if not search_results.ok:
            # give up
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
            print_message("Failed to guess wiki page", bcolors.FAIL, log=True)
            return song

        else:
            # don't save just yet...
            # url = guess_url
            search_results_soup = BeautifulSoup(search_results.text, 'html.parser')
            href_values = [a['href'] for a in search_results_soup.find_all('a') if 'href' in a.attrs]

            # Extract the URLs starting with the specified prefix
            if 'gamerch.com/maimai' in href_values[0]:
                first_matched_url = href_values[0]
            else:
                extracted_urls = [re.search(r'(?<=url\?q=)([^&]+)', href).group(1) for href in href_values if re.search(r'(?<=url\?q=)([^&]+)', href)]

                # Filter URLs that start with the specified prefix
                filtered_urls = [url for url in extracted_urls if url.startswith('https://gamerch.com/maimai/entry/')]
                first_matched_url = filtered_urls[0] if filtered_urls else None

            if first_matched_url:
                time.sleep(random.randint(1,2))

                try:
                    wiki = requests.get(first_matched_url, timeout=5, headers=request_headers, allow_redirects=True)
                except requests.RequestException as e:
                    lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True, is_verbose=True)
                    return song

                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Found potential wiki URL from search - checking page contents", bcolors.OKBLUE, log=True, is_verbose=True)
                return _parse_wikiwiki(song, wiki, first_matched_url, total_diffs, header_printed)
            else:
                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Failed to guess wiki page", bcolors.FAIL, log=True, is_verbose=True)
                return song


def _parse_wikiwiki(song, wiki, url, total_diffs, header_printed):
    critical_errors = [0]

    if 'lev_utage' in song and song["title"].startswith(f"[{song['kanji']}]"):
        stripped_utage_title = song["title"][len(song['kanji']) + 2:].strip()
        song_title = normalize_title(stripped_utage_title)
    else:
        song_title = normalize_title(song['title'])

    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("body .main table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', id=re.compile('^notes_')):
        if '*' in footnotes.get_text(strip=True):
            footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
        print_message("Wiki page not found - invalid page", bcolors.FAIL, log=True)
        return song

    # If title doesn't match
    if normalize_title(soup.find('h1', 'content-head').text) != song_title:
        # if song has a confirmed wiki url
        if song['wiki_url'] == url:
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
            print_message("Invalid wiki page - Page title mismatch", bcolors.WARNING, log=True)
        # If it doesn't abort
        else:
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
            print_message("Invalid wiki page - Page title mismatch", bcolors.FAIL, log=True)
            return song

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
            try:
                date_row = overview_dict["配信日"]
            except KeyError:
                try:
                    date_row = overview_dict["本配信日"]
                except KeyError:
                    lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message("Warning - date not found", bcolors.WARNING, log=True, is_verbose=True)

            formatted_date = ''
            if date_row:
                if '初期' in date_row:
                    formatted_date = '20121107' # maimai launch date
                else:
                    release_dates = date_row
                    earliest_release_date = re.search(r'\b\d{4}/\d{1,2}/\d{1,2}', release_dates)
                    if earliest_release_date:
                        earliest_release_date = earliest_release_date.group()
                        date_num_parts = earliest_release_date.split('/')
                        formatted_date = '{:04d}{:02d}{:02d}'.format(int(date_num_parts[0]), int(date_num_parts[1]), int(date_num_parts[2]))

            if not formatted_date == '':
                diff_count = [0]
                update_song_key(song, 'date_added', formatted_date, diff_count=diff_count)
                # update_song_key(song, 'version', _guess_version(formatted_date), diff_count=diff_count)
                
                if diff_count[0] > 0:
                    lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
                    print_message("Added date and version", bcolors.OKGREEN)
            else:
                # fail
                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Warning - date not found", bcolors.WARNING, log=True, is_verbose=True)
        else:
            # Skip for Utage
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Skipped date (Utage)", bcolors.WARNING, log=True, is_verbose=True)

        # Update BPM
        if overview_dict['BPM']:
            diff_count = [0]
            update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

            if diff_count[0] > 0:
                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
                print_message("Added BPM", bcolors.OKGREEN)
    else:
        # fail
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
        print_message("Invalid wiki page - no overview table", bcolors.FAIL, log=True)
        critical_errors[0] += 1

    # find the charts table
    charts_table = None
    charts_table_dx = None
    charts_data = []
    for table in tables:
        th_elements = table.select('tr:nth-of-type(1) td[rowspan], tr:nth-of-type(1) th[rowspan]')


        # Handle buddy chart in song
        if 'buddy' in song and len(th_elements) > 3 and 'バディ' in th_elements[3]:
            th_elements = th_elements[:-2]

        if len(th_elements) in (2, 3) and th_elements[0].get_text(strip=True) == 'Lv' and th_elements[-1].get_text(strip=True) == '総数':
            charts_table_head = [th.text for th in table.select("thead th:not([colspan]), thead td:not([colspan])") if th.text != "スコア"]
            
            if any(charts_table_head) and 'Lv' in charts_table_head[0]:
                # DX chart table
                if 'Touch' in charts_table_head[5:7]:
                    charts_table_dx = table
                    charts_table_head_dx = charts_table_head
                # Standard chart table
                else:
                    charts_table = table


    
    if has_std_chart and charts_table is None:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - No Std chart table found", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1
    if has_dx_chart and charts_table_dx is None:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - No DX chart table found", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1
    if (has_dual_chart or has_utage_chart) and charts_table is None and charts_table_dx is None:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1


    # Find constant and chart designer
    chart_designers_text = None
    chart_designers_spans = soup.find_all('span', style='font-size:11px')
    chart_designers_dict = {}
    chart_designers_dict_dx = {}


    # count total numbers of designer dicts needed
    if has_std_chart and has_dx_chart:
        req_dict_count = 2
    elif has_single_chart or has_utage_chart:
        req_dict_count = 1


    for chart_designers_span in chart_designers_spans:
        chart_designers_span_text = chart_designers_span.get_text(strip=True)

        # Count number of text in brackets
        brackets_count = len(re.compile(r'【(.*?)】').findall(chart_designers_span_text))

        # Ensure there are only one pair of brackets in matched text
        # if brackets_count == 0:
        #     continue

        # # Just one bracket in span
        # elif brackets_count == 1:

        # Warn if multiple brackets
        if brackets_count != 1:
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message(f"Caution - Designer info text has markup issues", bcolors.WARNING, log=True, is_verbose=True)



        # Match Designer text
        if '譜面作者【' in chart_designers_span_text:
            match = re.search(r'【(BAS|ADV|EXP|MST|Re:M)(…|[.]{3})(.*?)】', chart_designers_span_text)

            # Matched on first try!
            if match is not None:
                chart_designers_text = chart_designers_span_text

            else:
                # Song is WE only
                if 'kanji' in song:
                    chart_designers_text = chart_designers_span_text
                    match = re.search(r'【(.*?)】', chart_designers_text)
                    if match:
                        match = match.group(1)
                        chart_designers_dict = {f"lev_{song['kanji']}_designer": match}
                        req_dict_count-=1
                        break
                else:
                    # ipdb.set_trace()

                    # Try searching without closing brackets
                    # And get its parent to see if brackets weren't matched
                    # due to formatting errors (e.g.: https://gamerch.com/maimai/entry/533826)
                    chart_designers_span_parent_text = chart_designers_span.find_parent().get_text(strip=True)

                    if '譜面作者【' in chart_designers_span_parent_text:
                        match = re.search(r'【(BAS|ADV|EXP|MST|Re:M)(…|[.]{3})(.*?)】', chart_designers_span_parent_text)

                        if match is not None:
                            chart_designers_text = chart_designers_span_parent_text


            if match is not None:
                # Check if the DX chart table is directly in front
                if charts_table_dx is not None and charts_table_dx == chart_designers_span.find_previous().find_previous('div', {'class':"mu__table"}).find('table'):
                    chart_designers_dict_dx = _construct_designers_dict(song, chart_designers_text, 'designer', 'dx_')
                    req_dict_count-=1
                    break

                # Check if the Std chart table is directly in front
                if charts_table is not None and charts_table == chart_designers_span.find_previous().find_previous('div', {'class':"mu__table"}).find('table'):
                    chart_designers_dict = _construct_designers_dict(song, chart_designers_text, 'designer', '')
                    req_dict_count-=1
                    break




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
            lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message(f"Warning - No designer info found", bcolors.WARNING, log=True, is_verbose=True)

    if ((has_dual_chart and req_dict_count == 2)
        or ((has_single_chart or has_utage_chart) and req_dict_count == 1)):
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message(f"Warning - No designer info found", bcolors.WARNING, log=True, is_verbose=True)

    # Update chart details
    if charts_table:
        if 'kanji' in song:
            _process_utage_chart(song, charts_table, charts_table_head, chart_designers_dict, header_printed)
        else:
            for chart_type in game.CHART_LIST:
                if chart_type in song:
                    _process_chart(song, chart_type, CHART_COLORS[chart_type], charts_table, charts_table_head, chart_designers_dict, header_printed)


    if charts_table_dx:
        if 'kanji' in song:
            _process_utage_chart(song, charts_table_dx, charts_table_head_dx, chart_designers_dict_dx, header_printed)

        else:
            for chart_type in game.CHART_LIST_DX:
                if chart_type in song:
                    _process_chart(song, chart_type, CHART_COLORS[chart_type], charts_table_dx, charts_table_head_dx, chart_designers_dict_dx, header_printed)


    if song['wiki_url'] != url and critical_errors[0] == 0:
        song['wiki_url'] = url
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
        print_message("Saved wiki URL", bcolors.OKBLUE)

    if old_song == song:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
    else:
        total_diffs[0] += 1
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN)

    return song


def _process_chart(song, chart_type, chart_color, charts_table, charts_table_head, chart_designers_dict, header_printed):
    row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{chart_color}' in tag.get('style', ''))
    if row:
        row = row.find_parent()
        data = [cell.text for cell in row]
        data_dict = dict(zip(charts_table_head, data))
        _update_song_chart_details(song, data_dict, chart_designers_dict, chart_type, header_printed)

def _process_utage_chart(song, charts_table, charts_table_head, chart_designers_dict, header_printed):
    utage_rows = charts_table.find_all(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["lev_utage"]}' in tag.get('style', ''))

    if 'buddy' not in song:
        for utage_row in utage_rows:
            # Case 1 : Multiple Utage charts, label is 宴2<br/>14?
            if len(utage_rows) > 1:
                if song['kanji'] in utage_row.get_text(strip=True) and song['lev_utage'] in utage_row.get_text(strip=True):
                    utage_row_parent = utage_row.find_parent()
                    if utage_row_parent:
                        # Case 1 : 宴2<br/>14?
                        this_utage_chart_number = ''
                        pattern = re.compile(fr'{re.escape(song["kanji"])}(\d)(?=<br/>{re.escape(song["lev_utage"])})')
                        if pattern:
                            match = re.search(pattern, utage_row_parent.find('th').decode_contents())
                            if match:
                                this_utage_chart_number = match.group(0)

                        for br_tag in utage_row_parent.find_all('br'):
                            br_tag.decompose()

                        utage_data = [cell.text for cell in utage_row_parent]
                        utage_data_dict = dict(zip(charts_table_head, utage_data))
                        _update_song_chart_details(song, utage_data_dict, chart_designers_dict, 'lev_utage', header_printed, this_utage_chart_number)
                        return

            # Case 2 : Only one utage chart, label is 宴
            elif len(utage_rows) == 1:
                if song['kanji'] in utage_row.get_text(strip=True):
                    utage_row_parent = utage_row.find_parent()
                    if utage_row_parent:
                        utage_data = [cell.text for cell in utage_row_parent]
                        utage_data_dict = dict(zip(charts_table_head, utage_data))
                        _update_song_chart_details(song, utage_data_dict, chart_designers_dict, 'lev_utage', header_printed)
                        return
    else:
        # Case 3 : Utage (Buddy)
        for utage_row in utage_rows:
            if song['kanji'] in utage_row.get_text(strip=True):
                utage_row_parent = utage_row.find_parent()
                if utage_row_parent:
                    utage_left_data = [cell.text for cell in utage_row_parent]
                    utage_left_data_dict = dict(zip(charts_table_head, utage_left_data))

                    # Get right side data
                    utage_row_parent_right = utage_row_parent.find_next_sibling()
                    utage_right_data = [cell.text for cell in utage_row_parent_right]

                    # Copy and insert first item from utage_left_data into utage_right_data
                    utage_right_data.insert(0, utage_left_data[0])  # Copy utage_left_data[0] to the start of utage_right_data


                    # Process right side data referencing left side data
                    if [cell for cell in utage_row_parent][2].has_attr('rowspan'):
                        utage_right_data.insert(2, utage_left_data[2])

                    utage_right_data_dict = dict(zip(charts_table_head, utage_right_data))

                    _update_song_chart_details(song, utage_left_data_dict, chart_designers_dict, 'lev_utage_left', header_printed)
                    _update_song_chart_details(song, utage_right_data_dict, chart_designers_dict, 'lev_utage_right', header_printed)
                    return



def _update_song_chart_details(song, chart_dict, chart_designers_dict, chart, header_printed, this_utage_chart_number=''):
    details_diff_count = [0]
    designer_diff_count = [0]

    update_song_key(song, f"{chart}_notes", chart_dict["総数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"{chart}_notes_tap", chart_dict["Tap"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"{chart}_notes_hold", chart_dict["Hold"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"{chart}_notes_slide", chart_dict["Slide"], remove_comma=True, diff_count=details_diff_count)

    if 'Touch' in chart_dict:
        update_song_key(song, f"{chart}_notes_touch", chart_dict["Touch"], remove_comma=True, diff_count=details_diff_count)

    update_song_key(song, f"{chart}_notes_break", chart_dict["Break"], remove_comma=True, diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN)

    if chart_designers_dict and 'buddy' not in song:
        # Skip designer search for UTAGE because it's copied from comment

        # in some cases 宴 may be labled as 宴2 or 宴[即]..
        # 宴2 : Garakuta Doll Play https://gamerch.com/maimai/entry/533459
        # 宴[即] : ジングルベル https://gamerch.com/maimai/entry/533569
        # if chart == 'lev_utage':
        #     _try_match_utage_designer(song, chart_designers_dict, chart, this_utage_chart_number, diff_count=designer_diff_count)

        # Convert REMAS to RE:M
        # elif chart == 'lev_remas':
        #     try:
        #         update_song_key(song, f"{chart}_designer", chart_designers_dict["lev_remas_designer"], diff_count=designer_diff_count)
        #     except KeyError:
        #         print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)

        try:
            update_song_key(song, f"{chart}_designer", chart_designers_dict[f"{chart}_designer"], diff_count=designer_diff_count)
        except:
            # only print not found if chart is EXP/MAS/REMAS
            if chart not in ('lev_bas', 'lev_adv', 'dx_lev_bas', 'dx_lev_adv', 'lev_utage', 'dx_lev_utage'):
                lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)
    
    # if not chart == 'lev_utage' and chart_designers_dict:
    #     try:
    #         if re.search(r'(\d{2}\.\d)',chart_designers_dict[f"{chart}_i"]):
    #             update_song_key(song, f"{chart}_i", chart_designers_dict[f"{chart}_i"], diff_count=designer_diff_count)
    #         else:
    #             raise Exception(f"Constant for {chart.upper()} is invalid")
    #     except:
    #         if chart not in ('bas', 'adv'):
    #             print_message(f"Warning - No constant found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)

    if designer_diff_count[0] > 0:
        lazy_print_song_header(f"{song['sort']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN)


# def _try_match_utage_designer(song, chart_designers_dict, chart, this_utage_chart_number, diff_count):

#     # Case 1 : 宴
#     count_of_宴 = sum('宴' in key for key in chart_designers_dict.keys())
#     if count_of_宴 == 1:
#         try:
#             designer_key = chart_designers_dict[[key for key in chart_designers_dict if '宴' in key][0]]
#             update_song_key(song, "lev_utage_designer", designer_key, diff_count=diff_count)
#             return
#         except KeyError:
#             pass
    
#     # Case 2 : 宴2
#     if this_utage_chart_number != '':
#         try:
#             designer_key = chart_designers_dict[f"lev_{this_utage_chart_number}_designer"]
#             update_song_key(song, "lev_utage_designer", designer_key, diff_count=diff_count)
#             return
#         except KeyError:
#             pass

#     # Case 3 : 宴[協]
#     try:
#         designer_key = chart_designers_dict[f"lev_宴[{song['kanji']}]_designer"]
#         update_song_key(song, "lev_utage_designer", designer_key, diff_count=diff_count)
#         return
#     except KeyError:
#         print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)


def _construct_designers_dict(song, text, key_name, prefix=''):
    # Use regular expression to find content within brackets
    match = re.search(r'【(.*?)】', text)

    if match:
        content_within_brackets = '【' + match.group(1)
        
        # Split key-value pairs using '、' as the delimiter
        pairs = {}
        pattern = re.compile(fr'[、【](?=EXP|MST|Re:M|宴|光|覚|蛸|蔵|狂|星|宴|協)')
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
            if key.lower() == 're:m':
                key = 'remas'
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

