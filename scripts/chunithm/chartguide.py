# import ipdb
import requests
import os
import shutil
import json
import re
import copy
import html
from shared.common_func import *
from chunithm.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

VERSION_MAPPING = {
    "無印": "01",
    "PLUS": "01",
    "AIR": "02",
    "AIR+": "02",
    "STAR": "03",
    "STAR+": "03",
    "AMAZON": "04",
    "AMAZON+": "04",
    "CRYSTAL": "05",
    "CRYSTAL+": "05",
    "PARADISE": "06",
    "PARADISE×": "06",
    "NEW": "07",
    "NEW+": "07",
    "SUN": "08",
    "SUN+": "08",
    "LUMINOUS": "09",
    "LUMINOUS+": "09",
    "VERSE": "10",
    "X-VERSE": "10",
    "X-VERSE-X": "10",
    "Mate": "11"
}

PAGES = {
    "/new.html",
    "/sort/1.htm",
    "/sort/2.htm",
    "/sort/3.htm",
    "/sort/4.htm",
    "/sort/5.htm",
    "/sort/6.htm",
    "/sort/7.htm",
    "/sort/7+.htm",
    "/sort/8.htm",
    "/sort/8+.htm",
    "/sort/9.htm",
    "/sort/9+.htm",
    "/sort/10.htm",
    "/sort/10+.htm",
    "/sort/11.htm",
    "/sort/11+.htm",
    "/sort/12.htm",
    "/sort/12+.htm",
    "/sort/13.htm",
    "/sort/13+.htm",
    "/sort/14.htm",
    "/sort/14+.htm",
    "/sort/15.htm",
    "/sort/15+.htm",
    "/sort/ultima.htm",
    "/end.htm"
}

SDVXIN_BASE_URL = 'https://sdvx.in/'
_sdvxin_songs_cache = None


def load_sdvxin_songs():
    global _sdvxin_songs_cache
    if _sdvxin_songs_cache is not None:
        return _sdvxin_songs_cache

    songs = []
    for chunk in range(1, 21):
        response = requests.get(
            f"{SDVXIN_BASE_URL}chunithm/_/json/songs{chunk:02d}.json",
            timeout=10,
        )
        if response.status_code != 200 or not response.text.lstrip().startswith("["):
            continue
        response.encoding = 'utf-8'
        songs.extend(response.json())

    for path in ('songs_we.json', 'songs_wedel.json'):
        response = requests.get(
            f"{SDVXIN_BASE_URL}chunithm/_/json/{path}",
            timeout=10,
        )
        if response.status_code == 200 and response.text.lstrip().startswith("["):
            response.encoding = 'utf-8'
            songs.extend(response.json())

    _sdvxin_songs_cache = songs
    return songs


def normalize_sdvxin_title(title):
    title = normalize_brackets(str(title)).lower()
    return (
        title.replace('ä', 'a')
        .replace('å', 'a')
        .replace('ø', 'o')
        .replace('é', 'e')
        .replace('ö', 'o')
        .replace('☆', '')
        .replace('★', '')
        .replace('♥', '')
        .replace('♡', '')
        .replace('！', '!')
        .replace('’', "'")
        .replace('"', '')
        .replace(' ', '')
        .replace('　', '')
        .replace('～', '~')
        .replace('〜', '~')
        .replace('ー', '-')
        .replace('-', '')
        .replace('~', '')
    )


def find_sdvxin_song(songs, title, is_we=False):
    normalized_title = normalize_sdvxin_title(title)
    matching_songs = [
        song for song in songs
        if normalize_sdvxin_title(song.get('title', '')) == normalized_title
    ]
    if is_we:
        matching_songs = [
            song for song in matching_songs
            if song.get('genre') == "WORLD'S END"
        ]
    else:
        non_we_matches = [
            song for song in matching_songs
            if song.get('genre') != "WORLD'S END"
        ]
        if non_we_matches:
            matching_songs = non_we_matches
    exact_matches = matching_songs
    if exact_matches:
        return exact_matches[0]

    for song in songs:
        if is_we and song.get('genre') != "WORLD'S END":
            continue
        if not is_we and song.get('genre') == "WORLD'S END":
            continue
        candidate = normalize_sdvxin_title(song.get('title', ''))
        if candidate and (candidate in normalized_title or normalized_title in candidate):
            return song
    return None


def make_sdvxin_chart_link(sdvxin_song, difficulty):
    folder = 'end' if difficulty == 'we' else '10'
    suffix = 'end' if difficulty == 'we' else difficulty
    return f"{folder}/{str(sdvxin_song['id']).zfill(5)}{suffix}"

# Update on top of existing music-ex
def update_chartguide_data():
    print_message(f"Chartguide link search", 'H2')

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Create error log file if it doesn't exist
    f = open("errors.txt", 'w')

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'id', 'date_added')

    if len(target_song_list) == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " nothing updated")
        return

    sdvxin_songs = load_sdvxin_songs()
    total_diffs = [0]

    for song in target_song_list:
        _update_song_chartguide_data(song, total_diffs, sdvxin_songs)

    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)


def _update_song_chartguide_data(song, total_diffs, sdvxin_songs):
    header_printed = [0]
    old_song = copy.copy(song)
    sdvxin_song = find_sdvxin_song(
        sdvxin_songs,
        song['title'],
        is_we=bool(song.get('we_kanji')),
    )
    if sdvxin_song is None:
        print_message(f"No matching sdvx.in song: {song['title']}", bcolors.FAIL, log=True)
        return song

    charts = [('we', 'lev_we_chart_link')] if song['we_kanji'] else [
        ('exp', 'lev_exp_chart_link'),
        ('mst', 'lev_mas_chart_link'),
    ]
    if song.get('lev_ult'):
        charts.append(('ult', 'lev_ult_chart_link'))

    for chart, target_key in charts:
        if song.get(target_key) and not game.ARGS.overwrite:
            continue
        song[target_key] = make_sdvxin_chart_link(sdvxin_song, chart)
        lazy_print_song_header(f"{song['id']} {song['title']}", header_printed, log=True)
        print_message(f"Updated chart link ({chart.upper()})", bcolors.OKGREEN)

    if old_song == song:
        print_message("Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
    else:
        total_diffs[0] += 1

    return song

def _parse_page(song, lv_page_url, lv_page_file_path, target_key, url_pattern):
    content = None
    try:
        file_full_path = os.path.join(LOCAL_SDVXIN_CACHE_DIR + lv_page_file_path)
        with open(file_full_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        _get_and_save_page_to_local(lv_page_url)

        try:
            file_full_path = os.path.join(LOCAL_SDVXIN_CACHE_DIR + lv_page_file_path)
            with open(file_full_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except:
            print_message(f"Cache not found ({lv_page_file_path})", bcolors.ENDC)
    except Exception as e:
        print_message(f"Error reading file: {e}", bcolors.FAIL)
        return None, None

    if content is None:
        return None, None

    soup = BeautifulSoup(content, 'html.parser')
    song_dict = {}

    # Find all script tags with src attribute starting with "/chunithm/"
    # script_tags = soup.find_all('script', src=lambda s: s and s.startswith(url_pattern))
    script_tags = soup.find_all('script', src=lambda s: s and url_pattern.search(s))

    # Extract script tag src and song_title and add to the dictionary
    script_src = ''

    for script_tag in script_tags:
        script_src = script_tag['src']

        # Find song title in comment
        extracted_song_title = script_tag.find_next(text=lambda text:isinstance(text, Comment))

        # If comment doesn't contain title, request URL to get title
        if extracted_song_title == '':
            print_message(f"- Requesting page to fetch title - {script_src}", bcolors.OKBLUE, is_verbose=True)
            try:
                response = requests.get(SDVXIN_BASE_URL + script_src, timeout=5)
                response.encoding = 'ansi'
                clean_title = _clean_js_title(response.text)
                print_message(f"- Title is: {clean_title}", bcolors.OKBLUE, is_verbose=True)

                if clean_title:
                    extracted_song_title = clean_title
            except requests.RequestException as e:
                print_message(f"Failed to fetch title from {script_src}: {e}", bcolors.FAIL)

        if extracted_song_title:
            extracted_song_title = extracted_song_title.strip()
            song_dict[script_src] = extracted_song_title

    song_id = _extract_song_id(song, song_dict, song['title'])

    # Last check to see if page is valid
    if song_id != None:
        print_message(f"- Requesting page for validation - {song_id}", bcolors.OKBLUE, is_verbose=True)
        try:
            response = requests.get(SDVXIN_BASE_URL + song_id, timeout=5)
            response.encoding = 'ansi'
            clean_title = _clean_js_title(response.text)
            print_message(f"- Title is: {clean_title}", bcolors.OKBLUE, is_verbose=True)

            if not clean_title:
                song_id = ''
        except requests.RequestException as e:
            print_message(f"Failed to validate page {song_id}: {e}", bcolors.FAIL)
            song_id = ''

    return song_id, script_src

def _get_and_save_page_to_local(url):
    full_url = SDVXIN_BASE_URL + game.GAME_NAME + url

    # Handle main page (new songs)
    if url == '':
        full_url = SDVXIN_BASE_URL + game.GAME_NAME + '.html'

    try:
        response = requests.get(full_url, timeout=5)
        response.encoding = 'ansi'
    except requests.RequestException as e:
        print_message(f"Failed to retrieve {url}: {e}", bcolors.FAIL)
        return

    if not os.path.exists(LOCAL_SDVXIN_CACHE_DIR):
        os.makedirs(LOCAL_SDVXIN_CACHE_DIR)

    if response.status_code == 200:
        # Extract the filename from the URL
        filename = 'new.html'

        if url != '':
            filename = url.lstrip('/').replace('/', '_')

        output_path = os.path.join(LOCAL_SDVXIN_CACHE_DIR, filename)

        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print_message(f"Saved {url} to {output_path}", bcolors.OKBLUE, log=True, is_verbose=True)
    else:
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL)

def _clean_js_title(js_content):
    match = re.search(r'var TITLE\d+=\s*"(.*?)";', js_content)
    if not match:
        match = re.search(r'var TITLE\d+=\s*\'(.*?)\';', js_content)
        if not match:
            return None
    
    html_title = match.group(1)
    title = html.unescape(html_title)
    title = re.sub(r'(?i)<br\s*/?>', ' ', title)
    title = re.sub(r'<[^>]*?>', '', title)
    title = title.replace(r'\"', '"').replace(r"\'", "'")
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def _normalize_title_for_comparison(title_str):
    title_str = title_str.lower()
    title_str = normalize_brackets(title_str)
    title_str = (
        title_str
        .replace('ä', 'a')
        .replace('å', 'a')
        .replace('ø', 'o')
        .replace('é', 'e')
        .replace('ö', 'o')
        .replace('☆', '')
        .replace('★', '')
        .replace('♥', '')
        .replace('♡', '')
        .replace('！', '!')
        .replace('"', '')
        .replace('”', '')
        .replace('“', '')
        .replace('’', '\'')
        .replace(' ', '')
        .replace('　', '')
        .replace('～', '~')
        .replace('〜', '~')
        .replace('ー', '-')
        .replace('-', '')
        .replace('~', '')
    )
    return title_str

def _is_match(title, song_title):
    title = title.lower()
    song_title = song_title.lower()

    if title == song_title:
        return True

    song_title_alt = (
        song_title
        .replace('ä', 'a')
        .replace('å', 'a')
        .replace('ø', 'o')
        .replace('é', 'e')
        .replace('ö', 'o')
        .replace('☆', '')
        .replace('♥', '')
        .replace('♡', '')
        .replace('！', '!')
        .replace('"', '”')
    )
    if title == song_title_alt:
        return True

    title_brackets = normalize_brackets(title)
    song_title_brackets = normalize_brackets(song_title)
    if title_brackets == song_title_brackets:
        return True

    pattern = re.compile(r'[-～].*?[-～]')
    song_title_wo_subtitle = re.sub(pattern, '', song_title).strip()
    if title == song_title_wo_subtitle:
        return True

    match_similarity = compare_strings(title, song_title)
    if match_similarity > 80:
        return True

    return False

def _extract_song_id(song, song_dict, song_title):
    for song_id, title in song_dict.items():
        if _is_match(title, song_title):
            print_message(f"- Match found using comment ({song_id})", bcolors.OKBLUE, log=True, is_verbose=True)
            return song_id

    print_message(f"- No match using comments directly. Checking potential matches for: {song_title}", bcolors.WARNING, log=True, is_verbose=True)
    normalized_song_title = _normalize_title_for_comparison(song_title)

    for song_id, title in song_dict.items():
        normalized_comment = _normalize_title_for_comparison(title)

        if normalized_comment and (normalized_comment in normalized_song_title or normalized_song_title in normalized_comment):
            print_message(f"- Potential match found: '{title}' (JS: {song_id}). Fetching full title...", bcolors.OKBLUE, log=True, is_verbose=True)
            try:
                response = requests.get(SDVXIN_BASE_URL + song_id, timeout=5)
                response.encoding = 'ansi'
                full_js_title = _clean_js_title(response.text)
                if full_js_title:
                    print_message(f"- Fetched full title: '{full_js_title}'", bcolors.OKBLUE, log=True, is_verbose=True)
                    if _is_match(full_js_title, song_title):
                        print_message(f"- Match found using fetched full title ({song_id})", bcolors.OKBLUE, log=True, is_verbose=True)
                        return song_id
            except Exception as e:
                print_message(f"Error fetching JS title from {song_id}: {e}", bcolors.FAIL)

    print_message(f"- Match not found", bcolors.FAIL, log=True, is_verbose=True)
    return None

