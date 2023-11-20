import requests
import json
from datetime import datetime
from functools import reduce
from bs4 import BeautifulSoup

wiki_base_url = 'https://wikiwiki.jp/gameongeki/'

# Update on top of existing music-ex
def update_songs_extra_data(local_music_ex_json_path, date_from, date_until):
    with open(local_music_ex_json_path, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = _filter_songs_by_date(local_music_ex_data, date_from, date_until)

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    f = open("diffs.txt", 'w')

    for song in target_song_list:
        _update_song_wiki_data(song)

    with open(local_music_ex_json_path, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)


def _filter_songs_by_date(song_list, date_from, date_until):
    target_song_list = []

    for song in song_list:
        song_date_int = int(song.get("date"))

        if date_from <= song_date_int <= date_until:
            target_song_list.append(song)

    return target_song_list


def _update_song_wiki_data(song):
    title = (
        song['title']
        .replace('&', '＆')
        .replace(':', '：')
        .replace('[', '［')
        .replace(']', '］')
        .replace('#', '＃')
    )

    # use existing URL if already present
    if 'wikiwiki_url' in song and song['wikiwiki_url']:
        url = song['wikiwiki_url']
        wiki = requests.get(url)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " (URL already present!) : " + song['title'])
        return _parse_wikiwiki(song, wiki, url)

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
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " failed to guess wiki page : " + song['title'])
                return song

            else:
                url = guess_url
                return _parse_wikiwiki(song, wiki, url)
                
        else:
            url = guess_url
            
            return _parse_wikiwiki(song, wiki, url)


def _parse_wikiwiki(song, wiki, url):
    soup = BeautifulSoup(wiki.text, 'html.parser')
    tables = soup.select("#body table")

    overview_heads = tables[0].select('th')

    if song['lunatic'] == '1':
        overview_data = [head.find_parent('tr').select('td:last-of-type') for head in overview_heads]
    else:
        overview_data = [head.find_parent('tr').select('td:not([rowspan])') for head in overview_heads]

    overview_heads = [head.text for head in overview_heads]
    overview_data = [data[0].text for data in overview_data]

    overview_hash = dict(zip(overview_heads, overview_data))

    character_level = overview_hash["対戦相手"].split(" Lv.")
    character = character_level[0]
    level = character_level[1]

    details = tables[1]
    details_heads = [th.text for th in details.select("thead th")]
    details_data = [[cell.text for cell in level.select("th,td")] for level in details.select("tbody tr")]

    for details_datum in details_data:
        level_hash = dict(zip(details_heads, details_datum))

        if song['lunatic'] == '' and level_hash['難易度'] == 'BASIC':
            song["lev_bas_notes"] = level_hash["総ノート数"].replace(',', '')
            song["lev_bas_bells"] = level_hash["BELL"].replace(',', '')
            song["lev_bas_i"] = level_hash["譜面定数"]
            song["lev_bas_designer"] = level_hash["譜面製作者"]
        elif song['lunatic'] == '' and level_hash['難易度'] == 'ADVANCED':
            song["lev_adv_notes"] = level_hash["総ノート数"].replace(',', '')
            song["lev_adv_bells"] = level_hash["BELL"].replace(',', '')
            song["lev_adv_i"] = level_hash["譜面定数"]
            song["lev_adv_designer"] = level_hash["譜面製作者"]
        elif song['lunatic'] == '' and level_hash['難易度'] == 'EXPERT':
            song["lev_exc_notes"] = level_hash["総ノート数"].replace(',', '')
            song["lev_exc_bells"] = level_hash["BELL"].replace(',', '')
            song["lev_exc_i"] = level_hash["譜面定数"]
            song["lev_exc_designer"] = level_hash["譜面製作者"]
        elif song['lunatic'] == '' and level_hash['難易度'] == 'MASTER':
            song["lev_mas_notes"] = level_hash["総ノート数"].replace(',', '')
            song["lev_mas_bells"] = level_hash["BELL"].replace(',', '')
            song["lev_mas_i"] = level_hash["譜面定数"]
            song["lev_mas_designer"] = level_hash["譜面製作者"]
        elif song['lunatic'] == '1' and level_hash['難易度'] == 'LUNATIC':
            song["lev_lnt_notes"] = level_hash["総ノート数"].replace(',', '')
            song["lev_lnt_bells"] = level_hash["BELL"].replace(',', '')
            song["lev_lnt_i"] = level_hash["譜面定数"]
            song["lev_lnt_designer"] = level_hash["譜面製作者"]

    song['enemy_lv'] = level

    song['bpm'] = overview_hash['BPM']

    song['wikiwiki_url'] = url

    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " updated song extra data from wiki : " + song['title'])

    return song



def get_last_date(local_music_json_path):
    with open(local_music_json_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated
