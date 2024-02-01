import ipdb
import json
import os
import re
import requests
import hashlib
import unicodedata
from functools import reduce
from .terminal import bcolors
from datetime import datetime

def print_message(message, color_name, args, log=''):
    timestamp = ''
    reset_color = bcolors.ENDC

    if not args.no_timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' '

    if args.escape:
        message = message.replace("'", r"\'")

    # if --nocolors is set
    if args.nocolors:
        color_name = ''
        reset_color = ''

    if log:
        with open(log, 'a', encoding='utf-8') as f:
            f.write(timestamp + ' ' + message + '\n')

    print(timestamp + color_name + message + reset_color)

def get_last_date(local_json_path):
    with open(local_json_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')
    
    return lastupdated

def renew_lastupdated(local_json_path, dest_html_path, args):
    with open(local_json_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    all_dates = [datetime.strptime(x['date'], '%Y%m%d').date() for x in local_music_data]
    lastupdated = f"DATA: {reduce(lambda x, y: x if x > y else y, all_dates).strftime('%Y%m%d')}"
    print_message(f"Updated datestamp on {dest_html_path} to {lastupdated}", '', args)

    with open(dest_html_path, 'r', encoding='utf-8') as f:
        local_html_data = f.read()

    local_html_data = re.sub(r'(<[^>]+ class="lastupdated"[^>]*>).*(</[^>]+>)',
                             rf'\1<span>{lastupdated}</span>\2',
                             local_html_data,
                             flags=re.IGNORECASE)

    with open(dest_html_path, 'w', encoding='utf-8') as f:
        f.write(local_html_data)

def json_to_id_value_map(json, song_id):
    return {song_id:song for song in json}

def generate_hash(text_input):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the text input
    sha256_hash.update(text_input.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_result = sha256_hash.hexdigest()

    return hash_result

def maimai_generate_hash(song):
    if 'lev_utage' in song:
        return generate_hash(song['title'] + song['lev_utage'] + song['kanji'])
    else:
        return generate_hash(song['title'] + song['image_url'])

def filter_songs_by_date(song_list, date_key, date_from, date_until):
    target_song_list = []

    for song in song_list:
        song_date_int = int(song.get(date_key))

        if date_from <= song_date_int <= date_until:
            target_song_list.append(song)

    return target_song_list

def filter_songs_by_id(song_list, id_key, song_id):
    target_song_list = []

    for song in song_list:
        if int(song_id) == int(song.get(id_key)):
            target_song_list.append(song)

    return target_song_list

def filter_songs_by_id_range(song_list, id_key, id_from, id_to):
    target_song_list = []

    for song in song_list:
        song_id_int = int(song.get(id_key))

        if int(id_from) <= song_id_int <= int(id_to):
            target_song_list.append(song)

    return target_song_list

def filter_songs_by_id_list(song_list, id_key, id_list):
    target_song_list = []

    for song in song_list:
        song_id_int = int(song.get(id_key))

        if song_id_int in id_list:
            target_song_list.append(song)

    return target_song_list

def filter_songs_from_diffs(song_list, song_id, diffs_log):
    with open(diffs_log, 'r') as f:
        diff_lines = f.readlines()

    # Create a set of identifiers from the lines in diffs.txt
    prefixes_to_remove = ['NEW ', 'UPDATED ']
    for prefix in prefixes_to_remove:
        diff_lines = [line.replace(prefix, '') for line in diff_lines]

    unique_id = {line.strip() for line in diff_lines}

    target_song_list = []
    # Filter songs based on the identifiers
    for song in song_list:
        if song_id in unique_id:
            target_song_list.append(song)

    return target_song_list

def update_song_key(song, key, new_data, remove_comma=False, diff_count=None):
    # if source key doesn't exist, exit
    if key not in song:
        return
    # if source is not empty, don't overwrite
    if not (song[key] == ''):
        return
    # skip if new data is placeholder
    if new_data in ['？', '??', '???', '-']:
        return
    # Only overwrite if new data is not empty and is not same
    if not (new_data == '') and not (song[key] == new_data):
        diff_count[0] += 1
        song[key] = new_data

        if remove_comma:
            song[key] = song[key].replace(',', '')

        return

def normalize_unicode(input_string):
    return ''.join([unicodedata.normalize('NFKC', char) for char in input_string])

def remove_diacritics(input_string):
    # Define a mapping of characters with diacritics to their plain equivalents
    diacritics_mapping = {
        'À': 'A',
        'Á': 'A',
        'Â': 'A',
        'Ã': 'A',
        'Ä': 'A',
        'Å': 'A',
        'Æ': 'AE',
        'Ç': 'C',
        'È': 'E',
        'É': 'E',
        'Ê': 'E',
        'Ë': 'E',
        'Ì': 'I',
        'Í': 'I',
        'Î': 'I',
        'Ï': 'I',
        'Ñ': 'N',
        'Ò': 'O',
        'Ó': 'O',
        'Ô': 'O',
        'Õ': 'O',
        'Ö': 'O',
        'Ø': 'O',
        'Ù': 'U',
        'Ú': 'U',
        'Û': 'U',
        'Ü': 'U',
        'Ý': 'Y',
        'Þ': 'TH',
        'ß': 'ss',
    }

    # Replace characters with diacritics using the mapping
    for char, replacement in diacritics_mapping.items():
        input_string = input_string.replace(char, replacement)

    return input_string

def normalize_title(string: str):
    string = normalize_unicode(string)
    string = remove_diacritics(string.upper())
    string = (
        string
        # .replace('＠', '@')
        # .replace('＆', '&')
        # .replace('＆', '&')
        # .replace('：', ':')
        # .replace('［', '[')
        # .replace('］', ']')
        .replace('＃', '#')
        .replace('”', '"')
        .replace('“', '"')
        .replace('’', '\'')
        # .replace('！', '!')
        # .replace('？', '?')
        # .replace('（', '(')
        # .replace('）', ')')
        # .replace('／', '/')
        .replace('　', '')
        .replace(' ', '')
        .replace('～', '~')
        .replace('〜', '~')
        .replace('ー', '-')
        .replace('×', 'X')
        .replace('゛', '"')
        .replace('☆', '')
        .replace('★', '')
        .replace('♥', '')
        .replace('❤', '')
        .replace('♡', '')
        .replace('◆', '')
    )

    return string

def get_and_save_page_to_local(url, output_path, args, local_cache_dir):
    response = requests.get(url)
    response.encoding = 'ansi'

    if not os.path.exists(local_cache_dir):
        os.makedirs(local_cache_dir)

    if response.status_code == 200:
        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print_message(f"Saved {url} to {output_path}", bcolors.OKBLUE, args)
    else:
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL, args, errors_log)

def evaluate_lv_num(lv, expression):
    # Strip '+' from the input number
    lv = lv.rstrip('+')

    # Define a list of operators in the order of preference
    operators = ['>=', '<=', '>', '<', '==']

    # Define a dictionary to map comparison operators to functions
    operators_dict = {'>': lambda x, y: x > y,
                      '>=': lambda x, y: x >= y,
                      '<': lambda x, y: x < y,
                      '<=': lambda x, y: x <= y,
                      '==': lambda x, y: x == y}

    # Extract the operator and threshold from the expression
    for operator in operators:
        if expression.startswith(operator):
            threshold = expression[len(operator):]
            break
    else:
        # If no operator is found, assume '='
        operator, threshold = '=', expression

    # Convert threshold to integer for comparison
    threshold = int(threshold)

    # Compare the stripped number with the threshold using the specified operator
    return operators_dict[operator](int(lv), threshold)
