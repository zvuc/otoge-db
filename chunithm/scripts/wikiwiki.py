import const
import requests
import json
import ipdb
import re
from terminal import bcolors
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/chunithmwiki/'

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

        _print_message("(URL already present!)", song, nocolors, bcolors.OKBLUE, escape)
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
                _print_message("failed to guess wiki page", song, nocolors, bcolors.FAIL, escape)
                return song

            else:
                url = guess_url
                return _parse_wikiwiki(song, wiki, url, nocolors, escape)
                
        else:
            url = guess_url
            
            return _parse_wikiwiki(song, wiki, url, nocolors, escape)


def _parse_wikiwiki(song, wiki, url, nocolors, escape):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        _print_message("Parse failed! Skipping song", song, nocolors, bcolors.FAIL, escape)
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

        # no need to take care of worldsend
        # if song['we_kanji'] != '':
        #     overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]
        # else:
        #     overview_data = [head.find_parent('tr').select('td:not([rowspan])') for head in overview_heads]

        overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]

        overview_heads = [head.text for head in overview_heads]
        overview_data = [data[0].text for data in overview_data]
        overview_hash = dict(zip(overview_heads, overview_data))

        # Find release data
        if '配信' in overview_hash["解禁方法"].upper():
            release_dates = overview_hash["解禁方法"].upper()    
            earliest_release_date = re.search(r'\b\d{4}/\d{1,2}/\d{1,2}', release_dates).group()
            date_num_parts = earliest_release_date.split('/')
            formatted_date = '{:04d}{:02d}{:02d}'.format(int(date_num_parts[0]), int(date_num_parts[1]), int(date_num_parts[2]))
            
            if earliest_release_date:
                song['date'] = formatted_date

        else:
            # fail
            _print_message("Warning - date not found", song, nocolors, bcolors.WARNING, escape)
            
    else:
        # fail
        _print_message("Warning - overview table not found", song, nocolors, bcolors.WARNING, escape)


    # find the charts table
    charts_table = None
    for table in tables:
        th_elements = table.select('th:nth-of-type(1), th:nth-of-type(2)')
        if len(th_elements) > 2 and th_elements[0].get_text(strip=True) == 'Lv' and th_elements[1].get_text(strip=True) == '総数':
            charts_table = table
            break
    
    if charts_table:
        charts_table_head = [th.text for th in charts_table.select("thead th:not([colspan='5'])")]
        charts_data = [[cell.text for cell in level.select("th,td")] for level in charts_table.select("tbody tr")]

        if any(charts_table_head) and 'Lv' in charts_table_head[0]:
            for chart_details in charts_data:
                level_hash = dict(zip(charts_table_head, chart_details))

                if song['we_kanji'] == '' and level_hash['Lv'] == song["lev_bas"]:
                    song["lev_bas_notes"] = _update_song_key(song["lev_bas_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_bas_notes_tap"] = _update_song_key(song["lev_bas_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_bas_notes_hold"] = _update_song_key(song["lev_bas_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_bas_notes_slide"] = _update_song_key(song["lev_bas_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_bas_notes_air"] = _update_song_key(song["lev_bas_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_bas_notes_flick"] = _update_song_key(song["lev_bas_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_bas_i"] = _update_song_key(song["lev_bas_i"], level_hash["譜面定数"])
                    # song["lev_bas_designer"] = _update_song_key(song["lev_bas_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for BAS", song, nocolors, bcolors.OKGREEN, escape)
                    continue
                elif song['we_kanji'] == '' and level_hash['Lv'] == song["lev_adv"]:
                    song["lev_adv_notes"] = _update_song_key(song["lev_adv_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_adv_notes_tap"] = _update_song_key(song["lev_adv_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_adv_notes_hold"] = _update_song_key(song["lev_adv_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_adv_notes_slide"] = _update_song_key(song["lev_adv_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_adv_notes_air"] = _update_song_key(song["lev_adv_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_adv_notes_flick"] = _update_song_key(song["lev_adv_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_adv_i"] = _update_song_key(song["lev_adv_i"], level_hash["譜面定数"])
                    # song["lev_adv_designer"] = _update_song_key(song["lev_adv_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for ADV", song, nocolors, bcolors.OKGREEN, escape)
                    continue
                elif song['we_kanji'] == '' and level_hash['Lv'] == song["lev_exp"]:
                    song["lev_exp_notes"] = _update_song_key(song["lev_exp_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_exp_notes_tap"] = _update_song_key(song["lev_exp_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_exp_notes_hold"] = _update_song_key(song["lev_exp_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_exp_notes_slide"] = _update_song_key(song["lev_exp_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_exp_notes_air"] = _update_song_key(song["lev_exp_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_exp_notes_flick"] = _update_song_key(song["lev_exp_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_exc_i"] = _update_song_key(song["lev_exc_i"], level_hash["譜面定数"])
                    # song["lev_exc_designer"] = _update_song_key(song["lev_exc_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for EXP", song, nocolors, bcolors.OKGREEN, escape)
                    continue
                elif song['we_kanji'] == '' and level_hash['Lv'] == song["lev_mas"]:
                    song["lev_mas_notes"] = _update_song_key(song["lev_mas_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_mas_notes_tap"] = _update_song_key(song["lev_mas_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_mas_notes_hold"] = _update_song_key(song["lev_mas_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_mas_notes_slide"] = _update_song_key(song["lev_mas_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_mas_notes_air"] = _update_song_key(song["lev_mas_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_mas_notes_flick"] = _update_song_key(song["lev_mas_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_mas_i"] = _update_song_key(song["lev_mas_i"], level_hash["譜面定数"])
                    # song["lev_mas_designer"] = _update_song_key(song["lev_mas_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for MAS", song, nocolors, bcolors.OKGREEN, escape)
                    continue
                elif song['we_kanji'] == '' and level_hash['Lv'] == song["lev_ult"]:
                    song["lev_ult_notes"] = _update_song_key(song["lev_ult_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_ult_notes_tap"] = _update_song_key(song["lev_ult_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_ult_notes_hold"] = _update_song_key(song["lev_ult_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_ult_notes_slide"] = _update_song_key(song["lev_ult_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_ult_notes_air"] = _update_song_key(song["lev_ult_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_ult_notes_flick"] = _update_song_key(song["lev_ult_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_ult_i"] = _update_song_key(song["lev_ult_i"], level_hash["譜面定数"])
                    # song["lev_ult_designer"] = _update_song_key(song["lev_ult_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for ULT", song, nocolors, bcolors.OKGREEN, escape)
                    continue
                # WORLDS END
                elif song['we_kanji'] != '' and level_hash['Lv'] == song["lev_adv"]:
                    song["lev_we_notes"] = _update_song_key(song["lev_we_notes"], level_hash["総数"], remove_comma=True)
                    song["lev_we_notes_tap"] = _update_song_key(song["lev_we_notes_tap"], level_hash["Tap"], remove_comma=True)
                    song["lev_we_notes_hold"] = _update_song_key(song["lev_we_notes_hold"], level_hash["Hold"], remove_comma=True)
                    song["lev_we_notes_slide"] = _update_song_key(song["lev_we_notes_slide"], level_hash["Slide"], remove_comma=True)
                    song["lev_we_notes_air"] = _update_song_key(song["lev_we_notes_air"], level_hash["Air"], remove_comma=True)
                    song["lev_we_notes_flick"] = _update_song_key(song["lev_we_notes_flick"], level_hash["Flick"], remove_comma=True)
                    # song["lev_we_i"] = _update_song_key(song["lev_we_i"], level_hash["譜面定数"])
                    # song["lev_we_designer"] = _update_song_key(song["lev_we_designer"], level_hash["譜面製作者"])
                    _print_message(f"Wrote info {level_hash} for WE", song, nocolors, bcolors.OKGREEN, escape)
                    continue
        else:
            _print_message("Warning - No chart table found", song, nocolors, bcolors.WARNING, escape)
    else:
        _print_message("Warning - No chart table found", song, nocolors, bcolors.WARNING, escape)
    

    # TODO: Parse constant and chart designer

    song['bpm'] = overview_hash['BPM']

    song['wikiwiki_url'] = url

    _print_message("Updated song extra data from wiki", song, nocolors, bcolors.OKGREEN, escape)

    return song



def get_last_date(LOCAL_MUSIC_JSON_PATH):
    with open(LOCAL_MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def _update_song_key(key, new_data, remove_comma=False):
    # if source is not empty, don't overwrite
    if not (key == ''):
        return key
    # Only overwrite if new data is not empty
    if not (new_data == ''):
        key = new_data

        if remove_comma:
            key.replace(',', '')
            return key
        else:
            return key

def _print_message(message, song, nocolors, color_name, escape):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    if song:
        song_id = song['id']

        # if --escape is set
        if escape:
            song_title = ' : ' + song['title'].replace("'", r"\'")
        else:
            song_title = ' : ' + song['title']
    else:
        song_id = ''
        song_title = ''

    # if --nocolors is set
    if nocolors:
        color_name = ''
        reset_color = ''

    print(timestamp + color_name + ' ' + song_id + ' ' + message + song_title + reset_color)
