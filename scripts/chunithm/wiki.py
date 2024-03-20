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
errors_log = LOCAL_ERROR_LOG_PATH
request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}
HASH_KEYS = ['title', 'artist', 'we_kanji']

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

CHART_COLORS = {
   "bas": "c0ff20",
   "adv": "ffe080",
   "exp": "ffa0c0",
   "mas": "c0a0ff",
   "ult": "ff1c33",
   "we": "white"
}

# Update on top of existing music-ex
def update_songs_extra_data(args):
    print_message(f"Fetching latest wiki data.", bcolors.ENDC, args, errors_log, args.no_verbose)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added', HASH_KEYS, args)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    for song in target_song_list:
        update_song_wiki_data(song, args)

        # time.sleep(random.randint(1,2))

        with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def update_song_wiki_data(song, args):
    print_message(f"{song['id']} {song['title']}", 'HEADER', args, errors_log, args.no_verbose)

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
        if args.noskip:
            url = song['wikiwiki_url']
            try:
                wiki = requests.get(url, timeout=5, headers=request_headers, allow_redirects=True)
                return _parse_wikiwiki(song, wiki, url, args)
            except requests.RequestException as e:
                print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, args, errors_log)
                return song

        else:
            # Skip if URL present
            print_message("(Skipping)", bcolors.ENDC, args)

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
                # give up
                print_message("failed to guess wiki page", bcolors.FAIL, args)
                return song

            else:
                url = guess_url
                print_message("Found URL by guess!", bcolors.OKBLUE, args)
                return _parse_wikiwiki(song, wiki, url, args)
                
        else:
            url = guess_url
            print_message("Found URL by guess!", bcolors.OKBLUE, args)
            return _parse_wikiwiki(song, wiki, url, args)


def _parse_wikiwiki(song, wiki, url, args):
    song_diffs = [0]
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', class_='tooltip'):
        footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        print_message("Parse failed! Skipping song", bcolors.FAIL, args, errors_log, args.no_verbose)
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
                    lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
                    print_message("Added date and version", bcolors.OKGREEN, args, errors_log)
            else:
                # fail
                print_message("Warning - date not found", bcolors.WARNING, args, errors_log, args.no_verbose)
        else:
            # Skip for WE
            print_message("Skipped date (WE)", bcolors.WARNING, args, errors_log, args.no_verbose)

        # Update BPM
        if overview_dict['BPM']:
            diff_count = [0]
            update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

            if diff_count[0] > 0:
                lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
                print_message("Added BPM", bcolors.OKGREEN, args, errors_log)
    else:
        # fail
        print_message("Warning - overview table not found", bcolors.FAIL, args, errors_log, args.no_verbose)


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
                    chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer')
                    chart_constants_text = chart_constant_designer[1]
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i')
                    break
            else:
                # Sometimes the brackets are missing the header text
                # Try finding the 00.0 constant format
                match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(\d{2}\.\d)(.*)】',chart_constant_designer_span_text)
                match_other = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(.*?)】',chart_constant_designer_span_text)

                if re.match(r'\d{2}\.\d', match.group(3)) is not None:
                    chart_constants_text = match.group()
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i')
                    
                    # try looking for designer bracket nearby
                    # even if it doesnt have a title
                    if re.match(r'\d{2}\.\d', match_other.group(3)) is None:
                        chart_designers_text = match_other.group()
                        chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer')
                        break
                    else:
                        break
        
        # Just one bracket in span
        elif brackets_count == 1:
            # Find if it's either designer or constants
            # Designer
            if '譜面作者【' in chart_constant_designer_span_text:
                match = re.search(r'【(ULT|BAS|ADV|EXP|MAS)(…|[.]{3})(.*?)】',chart_constant_designer_span_text)

                if match is not None and re.match(r'\d{2}\.\d', match.group(3)) is None:
                    chart_designers_text = chart_constant_designer_span_text
                    chart_designers_dict = _construct_constant_designer_dict(song, chart_designers_text, 'designer')
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

                if re.match(r'\d{2}\.\d', match.group(3)) is not None:
                    chart_constants_text = chart_constant_designer_span_text
                    chart_constants_dict = _construct_constant_designer_dict(song, chart_constants_text, 'i')
                    break
        else:
            print_message(f"Warning - No designer/constant info found ({chart.upper()})", bcolors.WARNING, args, errors_log, args.no_verbose)
            
    
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
                print_message("Warning - No chart table found", bcolors.FAIL, args, errors_log, args.no_verbose)
    
    # Update chart details
    if charts_table:
        if song['lev_bas']:
            bas_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["bas"]}' in tag.get('style', ''))
            # bas_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["bas"]}.*')})
            if bas_row:
                bas_row = bas_row.find_parent()
                bas_data = [cell.text for cell in bas_row]
                bas_data_dict = dict(zip(charts_table_head, bas_data))
                _update_song_chart_details(song, bas_data_dict, chart_constant_designer_dict, 'bas', args, song_diffs)
        if song['lev_adv']:
            adv_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["adv"]}' in tag.get('style', ''))
            # adv_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["adv"]}.*')})
            if adv_row:
                adv_row = adv_row.find_parent()
                adv_data = [cell.text for cell in adv_row]
                adv_data_dict = dict(zip(charts_table_head, adv_data))
                _update_song_chart_details(song, adv_data_dict, chart_constant_designer_dict, 'adv', args, song_diffs)
        if song['lev_exp']:
            exp_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["exp"]}' in tag.get('style', ''))
            # exp_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["exp"]}.*')})
            if exp_row:
                exp_row = exp_row.find_parent()
                exp_data = [cell.text for cell in exp_row]
                exp_data_dict = dict(zip(charts_table_head, exp_data))
                _update_song_chart_details(song, exp_data_dict, chart_constant_designer_dict, 'exp', args, song_diffs)
        if song['lev_mas']:
            mas_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["mas"]}' in tag.get('style', ''))
            # mas_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["mas"]}.*')})
            if mas_row:
                mas_row = mas_row.find_parent()
                mas_data = [cell.text for cell in mas_row]
                mas_data_dict = dict(zip(charts_table_head, mas_data))
                _update_song_chart_details(song, mas_data_dict, chart_constant_designer_dict, 'mas', args, song_diffs)
        if song['lev_ult']:
            ult_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and f'{CHART_COLORS["ult"]}' in tag.get('style', ''))
            # ult_row = charts_table.find_all(['td','th'], attrs={'style':re.compile(f'{CHART_COLORS["ult"]}.*')})
            if ult_row:
                ult_row = ult_row.find_parent()
                ult_data = [cell.text for cell in ult_row]
                ult_data_dict = dict(zip(charts_table_head, ult_data))
                _update_song_chart_details(song, ult_data_dict, chart_constant_designer_dict, 'ult', args, song_diffs)
        if song['we_kanji']:
            # ipdb.set_trace()
            # Find with color
            # we_row = charts_table.find(lambda tag: tag.name in ['th', 'td'] and 'white' in tag.get('style', ''))
            # Find with text
            we_row = charts_table.find(text=song['we_kanji']).find_parent(lambda tag: tag.name in ['th','td'])
            
            if we_row and song['we_kanji'] in we_row.get_text(strip=True).replace('?', '？').replace('!', '！'):
                we_row_parent = we_row.find_parent()
                for br_tag in we_row_parent.find_all('br'):
                    br_tag.decompose()
                we_data = [cell.text for cell in we_row_parent]
                we_data_dict = dict(zip(charts_table_head, we_data))
                _update_song_chart_details(song, we_data_dict, chart_constant_designer_dict, 'we', args, song_diffs)

    else:
        print_message("Warning - No chart table found", bcolors.FAIL, args, errors_log, args.no_verbose)


    song['wikiwiki_url'] = url

    if old_song == song:
        print_message("Done (Nothing updated)", bcolors.ENDC, args, errors_log, args.no_verbose)
    # else:
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN, args, errors_log, args.no_verbose)

    return song



def _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, chart, args, song_diffs):
    details_diff_count = [0]
    designer_diff_count = [0]

    update_song_key(song, f"lev_{chart}_notes", chart_dict["総数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_tap", chart_dict["Tap"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_hold", chart_dict["Hold"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_slide", chart_dict["Slide"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_air", chart_dict["Air"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_notes_flick", chart_dict["Flick"], remove_comma=True, diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN, args)

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
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, args, errors_log, args.no_verbose)
        else:
            try:
                update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[f"lev_{chart}_designer"], diff_count=designer_diff_count)
            except:
                if chart not in ('bas', 'adv'):
                    print_message(f"Warning - No designer found ({chart.upper()})", bcolors.WARNING, args, errors_log, args.no_verbose)
    
    # Now fetching constants from google sheet (const.py) so we don't need this
    # if not chart == 'we' and chart_constant_designer_dict:
    #     try:
    #         if re.search(r'(\d{2}\.\d)',chart_constant_designer_dict[f"lev_{chart}_i"]):
    #             update_song_key(song, f"lev_{chart}_i", chart_constant_designer_dict[f"lev_{chart}_i"], diff_count=diff_count)
    #         else:
    #             raise Exception(f"Constant for {chart.upper()} is invalid")
    #     except:
    #         if chart not in ('bas', 'adv'):
    #             print_message(f"Warning - No constant found ({chart.upper()})", bcolors.WARNING, args, errors_log, args.no_verbose)

    if designer_diff_count[0] > 0:
        if details_diff_count[0] == 0:
            lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN, args)


def _construct_constant_designer_dict(song, text, key_name):
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

