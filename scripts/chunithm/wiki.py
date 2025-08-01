import ipdb
import requests
import json
import re
import copy
import random
import time
from shared.common_func import *
from chunithm.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

wiki_base_url = 'https://wikiwiki.jp/chunithmwiki/'
SDVXIN_BASE_URL = 'https://sdvx.in/'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

TARGET_KEYS = [
    "bpm",
    "lev_bas_notes_tap",
    "lev_bas_notes_hold",
    "lev_bas_notes_slide",
    "lev_bas_notes_air",
    "lev_adv_notes_tap",
    "lev_adv_notes_hold",
    "lev_adv_notes_slide",
    "lev_adv_notes_air",
    "lev_exp_notes_tap",
    "lev_exp_notes_hold",
    "lev_exp_notes_slide",
    "lev_exp_notes_air",
    "lev_mas_notes_tap",
    "lev_mas_notes_hold",
    "lev_mas_notes_slide",
    "lev_mas_notes_air",
    "lev_mas_notes_flick",
    "_exp_designer",
    "_mas_designer"
]

TARGET_KEYS_ULT = [
    "bpm",
    "lev_bas_notes_tap",
    "lev_bas_notes_hold",
    "lev_bas_notes_slide",
    "lev_bas_notes_air",
    "lev_adv_notes_tap",
    "lev_adv_notes_hold",
    "lev_adv_notes_slide",
    "lev_adv_notes_air",
    "lev_exp_notes_tap",
    "lev_exp_notes_hold",
    "lev_exp_notes_slide",
    "lev_exp_notes_air",
    "lev_mas_notes_tap",
    "lev_mas_notes_hold",
    "lev_mas_notes_slide",
    "lev_mas_notes_air",
    "lev_mas_notes_flick",
    "lev_ult_notes_tap",
    "lev_ult_notes_hold",
    "lev_ult_notes_slide",
    "lev_ult_notes_air",
    "lev_ult_notes_flick",
    "_exp_designer",
    "_mas_designer",
    "_ult_designer"
]

TARGET_KEYS_WE = [
    "bpm",
    "_we_notes",
    "_we_designer"
]

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
    "LUMINOUS": "20231214",
    "LUMINOUS+": "20240620",
    "VERSE": "20241212",
    "X-VERSE": "20250716"
}

CHART_COLORS = {
   "bas": "c0ff20",
   "adv": "ffe080",
   "exp": "ffa0c0",
   "mas": "c0a0ff",
   "ult": "ff1c33",
   "we": "white"
}

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
                            TARGET_KEYS_WE if song.get("we_kanji", "") != ""
                            else TARGET_KEYS if song.get("lev_ult", "") == ""
                            else TARGET_KEYS_ULT
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
            first_row = rows[0].find(lambda tag: tag.name in ['th', 'td'],{'colspan': True})
            if first_row and first_row.get_text(strip=True) == '楽曲情報':
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
        if not song['we_kanji']:
            # Find release date
            formatted_date = ''
            if '初期' in overview_dict["解禁方法"]:
                formatted_date = '20150716' # CHUNITHM launch date
            else:
                release_dates = overview_dict["解禁方法"]
                earliest_release_date = re.search(r'\b\d{4}/\d{1,2}/\d{1,2}', release_dates)
                if earliest_release_date:
                    earliest_release_date = earliest_release_date.group()
                    date_num_parts = earliest_release_date.split('/')
                    formatted_date = '{:04d}{:02d}{:02d}'.format(int(date_num_parts[0]), int(date_num_parts[1]), int(date_num_parts[2]))

            if not formatted_date == '':
                diff_count = [0]
                update_song_key(song, 'date_added', formatted_date, diff_count=diff_count)
                update_song_key(song, 'version', _guess_version(formatted_date), diff_count=diff_count)

                if diff_count[0] > 0:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                    print_message("Added date and version", bcolors.OKGREEN, log=True)
            else:
                # fail
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message("Warning - date not found", bcolors.WARNING, log=True, is_verbose=True)
        else:
            # Skip for WE
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message("Skipped date (WE)", bcolors.WARNING, log=True, is_verbose=True)

        # Update BPM
        if overview_dict['BPM']:
            diff_count = [0]
            update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

            if diff_count[0] > 0:
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                print_message("Added BPM", bcolors.OKGREEN, log=True)
    else:
        # fail
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Invalid wiki page - no overview table", bcolors.FAIL, log=True)
        critical_errors[0] += 1


    # Find constant and chart designer
    chart_constant_designer_text = None
    chart_constant_designer_spans = soup.find_all('span', style='font-size:11px')
    chart_designers_dict = {}
    chart_constants_dict = {}

    for chart_constant_designer_span in chart_constant_designer_spans:

        chart_constant_designer_span_text = chart_constant_designer_span.get_text(strip=True)

        # Count number of text in brackets
        brackets_count = len(re.compile(r'【(.*?)】').findall(chart_constant_designer_span_text))

        if brackets_count == 0:
            continue

        # 2 brackets within same <span>
        elif brackets_count == 2:
            if '譜面作者【' in chart_constant_designer_span_text and '譜面定数【' in chart_constant_designer_span_text:
                # separate text lines
                text = ''
                for child_node in chart_constant_designer_span:
                    if isinstance(child_node, NavigableString):
                        text += str(child_node).strip()
                    elif isinstance(child_node, Tag):
                        if child_node.name != 'br':
                            text += child_node.text.strip()
                        else:
                            text += '\n'

                chart_constant_designer = text.strip().split('\n')
                # check if separated text includes 譜面定数 in second row
                if '譜面定数' in chart_constant_designer[1]:
                    chart_designers_text = chart_constant_designer[0]
                    chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer', header_printed)
                    chart_constants_text = chart_constant_designer[1]
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i', header_printed)
                    break
            else:
                # Sometimes the brackets are missing the header text
                # Try finding the 00.0 constant format
                match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(\d{2}\.\d)(.*)】',chart_constant_designer_span_text)
                match_other = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(.*?)】',chart_constant_designer_span_text)

                if match is None:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Warning - No designer/constant info found", bcolors.WARNING, log=True, is_verbose=True)
                    break

                if re.match(r'\d{2}\.\d', match.group(3)) is not None:
                    chart_constants_text = match.group()
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i', header_printed)

                    # try looking for designer bracket nearby
                    # even if it doesnt have a title
                    if re.match(r'\d{2}\.\d', match_other.group(3)) is None:
                        chart_designers_text = match_other.group()
                        chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer', header_printed)
                        break
                    else:
                        break

        # Just one bracket in span
        elif brackets_count == 1:
            # Find if it's either designer or constants
            # Designer
            if '譜面作者【' in chart_constant_designer_span_text:
                match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(.*?)】',chart_constant_designer_span_text)

                if match is None:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Warning - No designer/constant info found", bcolors.WARNING, log=True, is_verbose=True)
                    break

                if re.match(r'\d{2}\.\d', match.group(3)) is None:
                    chart_designers_text = chart_constant_designer_span_text
                    chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer', header_printed)
                elif match is None and song['we_kanji']:
                    # Song is WE only
                    chart_designers_text = chart_constant_designer_span_text
                    match = re.search(r'【(.*?)】', chart_designers_text)
                    if match:
                        match = match.group(1)
                        chart_designers_dict = {f"lev_{song['we_kanji']}_designer": match}

            # Constants
            if '譜面定数【' in chart_constant_designer_span_text:
                # match = re.search(r'【(.*?)】', chart_constant_designer_span_text).group(1)
                match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(\d{2}\.\d)(.*)】',chart_constant_designer_span_text)

                if match is None:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Warning - No designer/constant info found", bcolors.WARNING, log=True, is_verbose=True)
                    break

                if re.match(r'\d{2}\.\d', match.group(3)) is not None:
                    chart_constants_text = chart_constant_designer_span_text
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i', header_printed)
                    break
        else:
            lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
            print_message(f"Warning - No designer/constant info found", bcolors.WARNING, log=True, is_verbose=True)


    chart_constant_designer_dict = {**chart_designers_dict, **chart_constants_dict}

    # find the charts table
    charts_table = None
    charts_data = []
    for table in tables:
        th_elements = table.select('tr:nth-of-type(1) td[rowspan], tr:nth-of-type(1) th[rowspan]')
        if len(th_elements) == 2 and th_elements[0].get_text(strip=True) == 'Lv' and th_elements[1].get_text(strip=True) == '総数':
            charts_table_head = [th.text for th in table.select("thead th:not([colspan='5']), thead td:not([colspan='5'])")]

            if any(charts_table_head) and 'Lv' in charts_table_head[0]:
                charts_table = table
                # Found the charts table
                break
            else:
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
                print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True)
                critical_errors[0] += 1

    # Update chart details
    if charts_table:
        if song['lev_bas']:
            bas_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["bas"]}' in tag.get('style', ''))
            # bas_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["bas"]}.*')})
            if bas_row:
                bas_row = bas_row.find_parent()
                bas_data = [cell.text for cell in bas_row]
                bas_data_dict = dict(zip(charts_table_head, bas_data))
                _update_song_chart_details(song, bas_data_dict, chart_constant_designer_dict, 'bas', header_printed)
        if song['lev_adv']:
            adv_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["adv"]}' in tag.get('style', ''))
            # adv_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["adv"]}.*')})
            if adv_row:
                adv_row = adv_row.find_parent()
                adv_data = [cell.text for cell in adv_row]
                adv_data_dict = dict(zip(charts_table_head, adv_data))
                _update_song_chart_details(song, adv_data_dict, chart_constant_designer_dict, 'adv', header_printed)
        if song['lev_exp']:
            exp_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["exp"]}' in tag.get('style', ''))
            # exp_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["exp"]}.*')})
            if exp_row:
                exp_row = exp_row.find_parent()
                exp_data = [cell.text for cell in exp_row]
                exp_data_dict = dict(zip(charts_table_head, exp_data))
                _update_song_chart_details(song, exp_data_dict, chart_constant_designer_dict, 'exp', header_printed)
        if song['lev_mas']:
            mas_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["mas"]}' in tag.get('style', ''))
            # mas_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["mas"]}.*')})
            if mas_row:
                mas_row = mas_row.find_parent()
                mas_data = [cell.text for cell in mas_row]
                mas_data_dict = dict(zip(charts_table_head, mas_data))
                _update_song_chart_details(song, mas_data_dict, chart_constant_designer_dict, 'mas', header_printed)
        if song['lev_ult']:
            ult_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["ult"]}' in tag.get('style', ''))
            # ult_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["ult"]}.*')})
            if ult_row:
                ult_row = ult_row.find_parent()
                ult_data = [cell.text for cell in ult_row]
                ult_data_dict = dict(zip(charts_table_head, ult_data))
                _update_song_chart_details(song, ult_data_dict, chart_constant_designer_dict, 'ult', header_printed)
        if song['we_kanji']:
            # Find with color
            # we_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and 'white' in tag.get('style', ''))
            # Find with text
            we_kanji = song['we_kanji']
            we_kanji_alt = song['we_kanji']

            if '？' in we_kanji:
                we_kanji_alt = '?'
            elif '！' in we_kanji:
                we_kanji_alt = '!'

            we_row = charts_table.find(text = lambda tag: (tag.string in [we_kanji, we_kanji_alt]))

            if we_row:
                we_row = we_row.find_parent(lambda tag: tag.name in ['th', 'td'])

            if we_row and song['we_kanji'] in we_row.get_text(strip=True).replace('?', '？').replace('!', '！'):
                we_row_parent = we_row.find_parent()
                for br_tag in we_row_parent.find_all('br'):
                    br_tag.decompose()
                we_data = [cell.text for cell in we_row_parent]
                we_data_dict = dict(zip(charts_table_head, we_data))
                _update_song_chart_details(song, we_data_dict, chart_constant_designer_dict, 'we', header_printed)

    else:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Invalid wiki page - No chart table found", bcolors.FAIL, log=True, is_verbose=True)
        critical_errors[0] += 1

    if ('wikiwiki_url' not in song or song['wikiwiki_url'] != url) and critical_errors[0] == 0:
        song['wikiwiki_url'] = url
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message("Saved wiki URL", bcolors.OKBLUE)

    if old_song == song:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
        print_message("Done (Nothing updated)", bcolors.ENDC, log=True, is_verbose=True)
    else:
        total_diffs[0] += 1


    return song



def _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, chart, header_printed):
    details_diff_count = [0]
    designer_diff_count = [0]

    update_song_key(song, f"lev_{chart}_notes", chart_dict["総数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_tap", chart_dict["Tap"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_hold", chart_dict["Hold"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_slide", chart_dict["Slide"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_air", chart_dict["Air"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_flick", chart_dict["Flick"], remove_comma=True, diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN)

    if chart_constant_designer_dict:
        # in some cases WE may be labled as WE戻 or 狂☆4...
        # WE戻 : https://wikiwiki.jp/chunithmwiki/B.B.K.K.B.K.K.
        # 狂☆4  : https://wikiwiki.jp/chunithmwiki/Trackless%20wilderness
        if chart == 'we':
            try:
                designer_key = chart_constant_designer_dict[f"lev_{chart}_designer"]
                update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[f"lev_{chart}_designer"], diff_count=designer_diff_count)
            except KeyError:
                try:
                    # try alternative syntax
                    designer_key = [key for key in chart_constant_designer_dict if song['we_kanji'] in key][0]
                    update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[designer_key], diff_count=designer_diff_count)
                except:
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)
        else:
            try:
                update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[f"lev_{chart}_designer"], diff_count=designer_diff_count)
            except:
                if chart not in ('bas', 'adv'):
                    lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, log=True, is_verbose=True)

    if designer_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN)


def _construct_constant_designer_dict(song, text, key_name, header_printed):
    # Use regular expression to find content within brackets
    match = re.search(r'【(.*?)】', text)

    if match:
        content_within_brackets = '【' + match.group(1)

        # Split key-value pairs using '、' as the delimiter
        pairs = {}
        if song['we_kanji']:
            pattern = re.compile(fr'[、【](?=EXP|MAS|ULT|WE|{re.escape(song["we_kanji"])})')
        else:
            pattern = re.compile(r'[、【](?=EXP|MAS|ULT|WE)')
        pairs = re.split(pattern, content_within_brackets)
        pairs = [item for item in pairs if item]

        # Separate key and value using '…' and construct a dictionary
        dictionary = {}
        for pair in pairs:
            if '…' in pair:
                key, value = pair.split('…', 1)
            elif '...' in pair:
                key, value = pair.split('...', 1)
            else:
                lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True, is_verbose=True)
                print_message(f"Warning - Found designer but was discarded due to unparsable formatting ({pair})", bcolors.WARNING, log=True, is_verbose=True)
                continue
            dictionary[key] = value

        # transform key names into lev_{chart} format
        formatted_dict = {}
        for key, value in dictionary.items():
            formatted_key = f"lev_{key.lower()}_{key_name}"
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


def _fetch_designer_info_from_sdvxin(song, total_diffs):
    """
    Update song dict with missing designer info by scraping sdvx.in chart pages.
    Only works for lev_exp, lev_mas, lev_ult based on song type and current designer info.
    """
    chart_map = {
        'lev_exp': 'E',
        'lev_mas': 'M',
        'lev_ult': 'U',
        'lev_we': 'W',
    }

    # Determine target charts
    is_we = song.get('we_kanji') != ''
    has_ult = song.get('lev_ult') != ''
    if is_we:
        target_charts = ['lev_we',]
    elif has_ult:
        target_charts = ['lev_exp', 'lev_mas', 'lev_ult']
    else:
        target_charts = ['lev_exp', 'lev_mas']

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

        # Define version and URL suffix patterns per chart
        chart_info = {
            'lev_we':  ('end', 'end'),
            'lev_ult': ('ult', 'ult'),
        }

        # Determine the version prefix and expected file suffix
        version_prefix, file_suffix = chart_info.get(chart, (r'\d{2}', 'sort'))

        # Build regex pattern dynamically
        pattern = rf'({version_prefix})/(\d{{5}})[a-z]{{3}}\d*'
        match = re.match(pattern, chart_link)

        if not match:
            print_message(f"Parsing ID from chart link failed", bcolors.FAIL, is_verbose=True)
            continue

        version_num, song_id = match.groups()

        # Construct URL
        url = f"{SDVXIN_BASE_URL}{game.GAME_NAME}/{version_num}/js/{song_id}{file_suffix}.js"


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
