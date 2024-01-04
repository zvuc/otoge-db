# import ipdb
import requests
import json
from shared.common_func import *
from ongeki.paths import *
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'

# Update on top of existing music-ex
def update_songs_extra_data(args):
    print_message(f"Fetching latest wiki data.", bcolors.ENDC, args)

    date_from = args.date_from
    date_until = args.date_until
    song_id = args.id

    # ipdb.set_trace()
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # prioritize id search if provided
    if not song_id == 0:
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

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
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


def _update_song_wiki_data(song, args):
    print_message(f"{song['id']} {song['title']}", bcolors.ENDC, args)

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
        return _parse_wikiwiki(song, wiki, url, args)

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
                print_message("Failed to guess wiki page", bcolors.FAIL, args)
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
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = song

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        print_message("Parse failed! Skipping song", bcolors.FAIL, args)
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

            if enemy_lv and not enemy_lv == '○':
                diff_count = [0]
                _update_song_key(song, 'enemy_lv', enemy_lv, diff_count=diff_count)

                if diff_count[0] > 0:
                    print_message("Added Enemy Lv", bcolors.OKGREEN, args)


            # If character name includes type info, use it
            if 'FIRE' in enemy_name:
                song['enemy_type'] = 'FIRE'
                print_message("Updated enemy type", bcolors.OKGREEN, args)
            elif 'AQUA' in enemy_name:
                song['enemy_type'] = 'AQUA'
                print_message("Updated enemy type", bcolors.OKGREEN, args)
            elif 'LEAF' in enemy_name:
                song['enemy_type'] = 'LEAF'
                print_message("Updated enemy type", bcolors.OKGREEN, args)

        else:
            # fail
            print_message("Warning - enemy lv not found", bcolors.WARNING, args)
            
    else:
        # fail
        print_message("Warning - overview table not found", bcolors.WARNING, args)


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
                    _update_song_chart_details(song, chart_dict, 'bas', args)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'ADVANCED':
                    _update_song_chart_details(song, chart_dict, 'adv', args)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'EXPERT':
                    _update_song_chart_details(song, chart_dict, 'exc', args)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'MASTER':
                    _update_song_chart_details(song, chart_dict, 'mas', args)
                elif song['lunatic'] == '1' and chart_dict['難易度'] == 'LUNATIC':
                    _update_song_chart_details(song, chart_dict, 'lnt', args)
        else:
            print_message("Warning - No chart table found", bcolors.WARNING, args)
    else:
        print_message("Warning - No chart table found", bcolors.WARNING, args)
    
    # Update BPM
    if overview_dict['BPM']:
        diff_count = [0]
        _update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

        if diff_count[0] > 0:
            print_message("Added BPM", bcolors.OKGREEN, args)

    song['wikiwiki_url'] = url

    if old_song == song:
        print_message("Done (Nothing updated)", bcolors.ENDC, args)
    # else:
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN, args)

    return song


def _update_song_chart_details(song, chart_dict, chart, args):
    diff_count = [0]
    _update_song_key(song, f"lev_{chart}_notes", chart_dict["総ノート数"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_bells", chart_dict["BELL"], remove_comma=True, diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_i", chart_dict["譜面定数"], diff_count=diff_count)
    _update_song_key(song, f"lev_{chart}_designer", chart_dict["譜面製作者"], diff_count=diff_count)

    if diff_count[0] > 0:
        print_message(f"Updated chart details for {chart.upper()}", bcolors.OKGREEN, args)

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
