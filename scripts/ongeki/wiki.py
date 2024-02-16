# import ipdb
import requests
import json
from shared.common_func import *
from ongeki.paths import *
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'
errors_log = LOCAL_ERROR_LOG_PATH
ENEMY_TYPES = ['FIRE', 'AQUA', 'LEAF']

# Update on top of existing music-ex
def update_songs_extra_data(args):
    print_message(f"Fetching latest wiki data.", bcolors.ENDC, args)

    date_from = args.date_from
    date_until = args.date_until
    song_id = args.id

    # ipdb.set_trace()
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date', 'id', args)


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
    )

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        url = song['wikiwiki_url']
        wiki = requests.get(url)
        return _parse_wikiwiki(song, wiki, url, args)

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        if args.noskip:
            url = song['wikiwiki_url']
            try:
                wiki = requests.get(url, timeout=5)
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
        wiki = requests.get(guess_url)

        if not wiki.ok:
            # try replacing special character as fallback
            title = title.replace('\'', '’')
            guess_url = wiki_base_url + title
            wiki = requests.get(guess_url)

            if not wiki.ok:
                # give up
                print_message("Failed to guess wiki page", bcolors.FAIL, args, errors_log, args.no_verbose)
                return song

            else:
                url = guess_url
                print_message("Found URL by guess!", bcolors.OKBLUE, args, errors_log, args.no_verbose)
                return _parse_wikiwiki(song, wiki, url, args)
                
        else:
            url = guess_url
            print_message("Found URL by guess!", bcolors.OKBLUE, args, errors_log, args.no_verbose)
            return _parse_wikiwiki(song, wiki, url, args)


def _parse_wikiwiki(song, wiki, url, args):
    song_diffs = [0]
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")
    old_song = song

    # If there are no tables in page at all, exit
    if len(tables) == 0:
        print_message("Parse failed! Skipping song", bcolors.FAIL, args, errors_log, args.no_verbose)
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
                update_song_key(song, 'enemy_lv', enemy_lv, diff_count=diff_count)

                if diff_count[0] > 0:
                    lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
                    print_message("Added Enemy Lv", bcolors.OKGREEN, args, errors_log)


            # If character name includes type info, use it
            for enemy_type in ENEMY_TYPES:
                diff_count = [0]

                if enemy_type in enemy_name:
                    update_song_key(song, 'enemy_type', enemy_type, diff_count=diff_count)

                    if diff_count[0] > 0:
                        lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
                        print_message("Updated enemy type", bcolors.OKGREEN, args, errors_log)
                        break

        else:
            # fail
            print_message("Warning - enemy lv not found", bcolors.WARNING, args, errors_log, args.no_verbose)
            
    else:
        # fail
        print_message("Warning - overview table not found", bcolors.WARNING, args, errors_log, args.no_verbose)


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
                    _update_song_chart_details(song, chart_dict, 'bas', args, song_diffs)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'ADVANCED':
                    _update_song_chart_details(song, chart_dict, 'adv', args, song_diffs)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'EXPERT':
                    _update_song_chart_details(song, chart_dict, 'exc', args, song_diffs)
                elif song['lunatic'] == '' and chart_dict['難易度'] == 'MASTER':
                    _update_song_chart_details(song, chart_dict, 'mas', args, song_diffs)
                elif song['lunatic'] == '1' and chart_dict['難易度'] == 'LUNATIC':
                    _update_song_chart_details(song, chart_dict, 'lnt', args, song_diffs)
        else:
            print_message("Warning - No chart table found", bcolors.WARNING, args, errors_log, args.no_verbose)
    else:
        print_message("Warning - No chart table found", bcolors.WARNING, args, errors_log, args.no_verbose)
    
    # Update BPM
    if overview_dict['BPM']:
        diff_count = [0]
        update_song_key(song, 'bpm', overview_dict['BPM'], diff_count=diff_count)

        if diff_count[0] > 0:
            lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
            print_message("Added BPM", bcolors.OKGREEN, args, errors_log)

    song['wikiwiki_url'] = url

    if old_song == song:
        print_message("Done (Nothing updated)", bcolors.ENDC, args, errors_log, args.no_verbose)
    # else:
    #     print_message("Updated song extra data from wiki", bcolors.OKGREEN, args)

    return song


def _update_song_chart_details(song, chart_dict, chart, args, song_diffs):
    details_diff_count = [0]
    designer_diff_count = [0]
    update_song_key(song, f"lev_{chart}_notes", chart_dict["総ノート数"], remove_comma=True, diff_count=details_diff_count)
    update_song_key(song, f"lev_{chart}_bells", chart_dict["BELL"], remove_comma=True, diff_count=details_diff_count)
    # update_song_key(song, f"lev_{chart}_i", chart_dict["譜面定数"], diff_count=details_diff_count)

    if details_diff_count[0] > 0:
        lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
        print_message(f"Added chart details for {chart.upper()} (+{details_diff_count[0]})", bcolors.OKGREEN, args)

    update_song_key(song, f"lev_{chart}_designer", chart_dict["譜面製作者"], diff_count=designer_diff_count)

    if designer_diff_count[0] > 0:
        if details_diff_count[0] == 0:
            lazy_print_song_header(f"{song['id']} {song['title']}", song_diffs, args, errors_log)
        print_message(f"Added chart designer for {chart.upper()}", bcolors.OKGREEN, args)
