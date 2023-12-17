import const
import requests
import json
import ipdb
import re
import copy
from terminal import bcolors
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup, NavigableString, Tag

wiki_base_url = 'https://wikiwiki.jp/chunithmwiki/'

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


# Update on top of existing music-ex
def update_songs_extra_data(date_from, date_until, song_id, nocolors, escape):
    # ipdb.set_trace()
    with open(const.LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # prioritize id search if provided
    if not song_id == 0:
        target_song_list = _filter_songs_by_id(local_music_ex_data, song_id)
    else:
        latest_date = int(get_last_date(const.LOCAL_MUSIC_EX_JSON_PATH))

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
        _update_song_wiki_data(song, nocolors, escape)

    with open(const.LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _filter_songs_by_date(song_list, date_from, date_until):
    target_song_list = []

    for song in song_list:
        song_date_int = int(song.get("date"))

        if date_from <= song_date_int <= date_until:
            target_song_list.append(song)

    return target_song_list


def _filter_songs_by_id(song_list, song_id):
    target_song_list = []

    for song in song_list:
        if song_id == int(song.get("id")):
            target_song_list.append(song)

    return target_song_list


def _update_song_wiki_data(song, nocolors, escape):
    _print_message(f"{song['id']} {song['title']}", nocolors, bcolors.ENDC, escape)

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
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        url = song['wikiwiki_url']
        wiki = requests.get(url)

        return _parse_wikiwiki(song, wiki, url, nocolors, escape)

    # If not, guess URL from title
    else:
        guess_url = wiki_base_url + title
        wiki = requests.get(guess_url)

        if not wiki.ok:
            # try replacing special character as fallback
            title = title.replace('\'', '’')
            guess_url = wiki_base_url + title
            wiki = requests.get(guess_url)

            if not wiki.ok:
                # give up
                _print_message("failed to guess wiki page", nocolors, bcolors.FAIL, escape)
                return song

            else:
                url = guess_url
                _print_message("Found URL by guess!", nocolors, bcolors.OKBLUE, escape)
                return _parse_wikiwiki(song, wiki, url, nocolors, escape)
                
        else:
            url = guess_url
            _print_message("Found URL by guess!", nocolors, bcolors.OKBLUE, escape)
            return _parse_wikiwiki(song, wiki, url, nocolors, escape)


def _parse_wikiwiki(song, wiki, url, nocolors, escape):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = copy.copy(song)

    # Sanitize any unwanted footnote tooltips
    for footnotes in soup.find_all('a', class_='tooltip'):
        footnotes.decompose()

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        _print_message("Parse failed! Skipping song", nocolors, bcolors.FAIL, escape)
        return song

    # find the overview table
    overview_table = None

    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            first_row = rows[0].find('td',{'colspan': True})
            if first_row and first_row.get_text(strip=True) == '楽曲情報':
                second_row = rows[1].find('th')
                if second_row and second_row.get_text(strip=True) == 'ジャンル':
                    overview_table = table
                    break

    if overview_table:
        overview_heads = overview_table.select('th')
        overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text for data in overview_data]
        overview_dict = dict(zip(overview_heads, overview_data))

        # Find release date
        formatted_date = ''
        if '配信' in overview_dict["解禁方法"]:
            release_dates = overview_dict["解禁方法"]    
            earliest_release_date = re.search(r'\b\d{4}/\d{1,2}/\d{1,2}', release_dates).group()
            date_num_parts = earliest_release_date.split('/')
            formatted_date = '{:04d}{:02d}{:02d}'.format(int(date_num_parts[0]), int(date_num_parts[1]), int(date_num_parts[2]))
        elif '初期' in overview_dict["解禁方法"]:
            formatted_date = '20150716' # CHUNITHM launch date
        
        # Write date and guess version
        if not formatted_date == '' and song['we_kanji']:
            ipdb.set_trace()
            diff_count = [0]
            _update_song_key(song, 'date', formatted_date, diff_count=diff_count)
            _update_song_key(song, 'version', _guess_version(formatted_date), diff_count=diff_count)
            
            if diff_count[0] > 0:
                _print_message("Added release date", nocolors, bcolors.OKGREEN, escape)

        else:
            # fail
            _print_message("Warning - date not found", nocolors, bcolors.WARNING, escape)
            
    else:
        # fail
        _print_message("Warning - overview table not found", nocolors, bcolors.WARNING, escape)


    # Find constant and chart designer
    # ipdb.set_trace()
    chart_constant_designer_text = None
    chart_constant_designer_spans = soup.find_all('span', style='font-size:11px')
    
    # Check if the matched span is the correct one
    for chart_constant_designer_span in chart_constant_designer_spans:
        if '譜面作者' in chart_constant_designer_span.get_text(strip=True):

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
                chart_constants_text = chart_constant_designer[1]

                chart_designers_dict = _construct_constant_designer_dict(chart_designers_text, 'designer')
                chart_constants_dict = _construct_constant_designer_dict(chart_constants_text, 'i')
                chart_constant_designer_dict = {**chart_designers_dict, **chart_constants_dict}
                # It's a match!
                break


    # find the charts table
    charts_table = None
    for table in tables:
        th_elements = table.select('tr:nth-of-type(1) td[rowspan], tr:nth-of-type(1) th[rowspan]')
        if len(th_elements) == 2 and th_elements[0].get_text(strip=True) == 'Lv' and th_elements[1].get_text(strip=True) == '総数':
            charts_table = table
            break
    
    # Update chart details
    if charts_table:
        # ipdb.set_trace()
        charts_table_head = [th.text for th in charts_table.select("thead th:not([colspan='5']), thead td:not([colspan='5'])")]
        charts_data = [[cell.text for cell in chart.select("th,td")] for chart in charts_table.select("tbody tr")]

        if any(charts_table_head) and 'Lv' in charts_table_head[0]:
            for chart_details in charts_data:
                chart_dict = dict(zip(charts_table_head, chart_details))

                if song['we_kanji'] == '' and chart_dict['Lv'] == song["lev_bas"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'bas', nocolors, escape)
                    continue
                elif song['we_kanji'] == '' and chart_dict['Lv'] == song["lev_adv"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'adv', nocolors, escape)
                    continue
                elif song['we_kanji'] == '' and chart_dict['Lv'] == song["lev_exp"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'exp', nocolors, escape)
                    continue
                elif song['we_kanji'] == '' and chart_dict['Lv'] == song["lev_mas"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'mas', nocolors, escape)
                    continue
                elif song['we_kanji'] == '' and chart_dict['Lv'] == song["lev_ult"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'ult', nocolors, escape)
                    continue
                # WORLDS END
                elif song['we_kanji'] != '' and chart_dict['Lv'][0] == song["we_kanji"]:
                    _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, 'we', nocolors, escape)
                    continue
        else:
            _print_message("Warning - No chart table found", nocolors, bcolors.WARNING, escape)
    else:
        _print_message("Warning - No chart table found", nocolors, bcolors.WARNING, escape)

    # Update BPM
    if overview_dict['BPM']:
        diff_count = [0]
        _update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

        if diff_count[0] > 0:
            _print_message("Added BPM", nocolors, bcolors.OKGREEN, escape)

    song['wikiwiki_url'] = url

    if old_song == song:
        _print_message("Done (Nothing updated)", nocolors, bcolors.ENDC, escape)
    # else:
    #     _print_message("Updated song extra data from wiki", nocolors, bcolors.OKGREEN, escape)

    return song



def get_last_date(LOCAL_MUSIC_JSON_PATH):
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def _update_song_chart_details(song, chart_dict, chart_constant_designer_dict, chart, nocolors, escape):
    
    diff_count = [0]
    _update_song_key(song, f"lev_{chart}_notes", chart_dict["総数"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_notes_tap", chart_dict["Tap"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_notes_hold", chart_dict["Hold"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_notes_slide", chart_dict["Slide"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_notes_air", chart_dict["Air"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_notes_flick", chart_dict["Flick"], remove_comma=True, diff_count=diff_count)

    if chart_constant_designer_dict:
        # ipdb.set_trace()
        # in some cases WE may be labled as WE戻 or 狂☆4...
        if chart == 'we':
            try:
                designer_key = chart_constant_designer_dict[f"lev_{chart}_designer"]
                _update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[f"lev_{chart}_designer"], diff_count=diff_count)
            except KeyError:
                # try alternative syntax
                designer_key = [key for key in chart_constant_designer_dict if song['we_kanji'] in key][0]
                _update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[designer_key], diff_count=diff_count)
        else:
            _update_song_key(song, f"lev_{chart}_designer", chart_constant_designer_dict[f"lev_{chart}_designer"], diff_count=diff_count)
    
    if not chart == 'we' and chart_constant_designer_dict:
        _update_song_key(song, f"lev_{chart}_i", chart_constant_designer_dict[f"lev_{chart}_i"], diff_count=diff_count)

    if diff_count[0] > 0:
        _print_message(f"Added chart details for {chart.upper()}", nocolors, bcolors.OKGREEN, escape)


def _update_song_key(song, key, new_data, remove_comma=False, diff_count=None):
    # if source is not empty, don't overwrite
    if not (song[key] == ''):
        return
    # Only overwrite if new data is not empty and is not same
    if not (new_data == '') and not (song[key] == new_data):
        diff_count[0] += 1
        song[key] = new_data

        if remove_comma:
            song[key] = song[key].replace(',', '')
        
        return

def _construct_constant_designer_dict(text, key_name):
    # Use regular expression to find content within brackets
    match = re.search(r'【(.*?)】', text)

    if match:
        content_within_brackets = match.group(1)
        
        # Split key-value pairs using '、' as the delimiter
        pairs = content_within_brackets.split('、')

        # Separate key and value using '…' and construct a dictionary
        dictionary = {}
        for pair in pairs:
            key, value = pair.split('…', 1)
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

def _print_message(message, nocolors, color_name, escape):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    if escape:
        message = message.replace("'", r"\'")

    # if --nocolors is set
    if nocolors:
        color_name = ''
        reset_color = ''

    print(timestamp + ' ' + color_name + message + reset_color)
