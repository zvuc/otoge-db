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

def print_message(message, color_name, args, log='', no_verbose=False):
    timestamp = ''
    print_color_name = ''
    reset_color = bcolors.ENDC

    if not args.no_timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' '

    if args.escape:
        message = message.replace("\\", "\\\\").replace("\"", "\\\"").replace("'", r"\'")

    # is header
    if color_name == 'HEADER':
        print_color_name = bcolors.BOLD + bcolors.HEADER

    if args.nocolors:
        print_color_name = ''
        reset_color = ''

    if args.markdown:
        if color_name == 'HEADER':
            print_color_name = '**'
            reset_color = '**'
        if color_name == bcolors.OKGREEN:
            print_color_name = '✅ '
            reset_color = ''
        if color_name == bcolors.WARNING:
            print_color_name = '⚠️ '
            reset_color = ''
        if color_name == bcolors.FAIL:
            print_color_name = '❗️ '
            reset_color = ''
        if color_name == bcolors.OKBLUE:
            print_color_name = 'ℹ️ '
            reset_color = ''

    if log:
        with open(log, 'a', encoding='utf-8') as f:
            f.write(timestamp + ' ' + message + '\n')

    if no_verbose is False:
        print(timestamp + print_color_name + message + reset_color)

def lazy_print_song_header(msg, diff_count, args, errors_log):
    if args.no_verbose and diff_count[0] == 0:
        # Lazy-print song name
        print_message(msg, 'HEADER', args, errors_log)
        diff_count[0] += 1

def parse_date(date_str, release_str):
    try:
        if date_str:
            return datetime.strptime(date_str, '%Y%m%d').date()

        # If 'date' is empty and 'release' exists, parse 'release' with YYMMDD format
        if date_str == '' and release_str:
            return datetime.strptime(release_str, '%y%m%d').date()

        # If both 'date' and 'release' are missing or invalid, return None or handle as needed
        return None
    except ValueError:
        # If parsing fails, return None or handle as needed
        return None

def get_last_date(local_music_data):
    all_dates = [parse_date(x.get('date', ''), x.get('release', '')) for x in local_music_data if x.get('date') or x.get('release')]

    # Exclude None values when finding the latest date
    valid_dates = [date for date in all_dates if date is not None]

    if valid_dates:
        latest_date = reduce(lambda x, y: x if x > y else y, valid_dates).strftime('%Y%m%d')
        return latest_date
    else:
        # Handle the case where all dates are None
        return None

def renew_lastupdated(local_json_ex_path, dest_html_path, args):
    with open(local_json_ex_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    latest_date = get_last_date(local_music_data)
    print_message(f"Updated datestamp on {dest_html_path} to {latest_date}", '', args)

    with open(dest_html_path, 'r', encoding='utf-8') as f:
        local_html_data = f.read()

    local_html_data = re.sub(r'block lastupdated\n\s*\|\s*(\d{8})',
                         rf'block lastupdated\n  | {latest_date}',
                         local_html_data,
                         flags=re.IGNORECASE)

    with open(dest_html_path, 'w', encoding='utf-8') as f:
        f.write(local_html_data)

def json_to_id_value_map(json, id_key):
    return {int(song['id']):song for song in json}

def json_to_hash_value_map(json, generate_hash_func):
    return {generate_hash_func(song):song for song in json}

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

def get_target_song_list(song_list, local_diffs_log_path, id_key, date_key, hash_key, args):
    if args.all:
        return [song for song in song_list]
    # prioritize id search if provided
    elif args.id != 0:
        if '-' in args.id:
            id_from = args.id.split('-')[0]
            id_to = args.id.split('-')[-1]
            return filter_songs_by_id_range(song_list, id_key, id_from, id_to)
        elif ',' in args.id:
            numbers = args.id.split(',')
            id_list = [int(num) for num in numbers]
            return filter_songs_by_id_list(song_list, id_key, id_list)
        else:
            return filter_songs_by_id(song_list, id_key, args.id)
    elif args.date_from != 0 or args.date_until != 0:
        latest_date = int(get_last_date(song_list))

        if args.date_from == 0:
            args.date_from = latest_date

        if args.date_until == 0:
            args.date_until = latest_date

        return filter_songs_by_date(song_list, date_key, args.date_from, args.date_until)
    else:
        # get id list from diffs.txt
        return get_songs_from_diffs(song_list, hash_key, local_diffs_log_path)


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

def get_songs_from_diffs(song_list, identifier, diffs_log):
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
        if (isinstance(identifier, str) and song[identifier] in unique_id) or \
           (callable(identifier) and identifier(song) in unique_id):
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

def archive_deleted_song(song, deleted_data):
    deleted_date = datetime.now().strftime('%Y%m%d')
    song['deleted_date'] = f"{deleted_date}"
    deleted_data.append(song)


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

