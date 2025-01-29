import argparse
import ipdb
import json
import os
import re
import requests
import hashlib
import importlib
import unicodedata
import game
from functools import reduce
from .terminal import bcolors
from datetime import datetime


def set_args_and_game_module(custom_args=None):
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--game', choices=['maimai', 'ongeki', 'chunithm'], help='Choose a game to perform scripts')
    parser.add_argument('--ongeki', action="store_true", help='Perform scripts for ongeki (shorthand for --game=\'ongeki\')')
    parser.add_argument('--chunithm', action="store_true", help='Perform scripts for chunithm (shorthand for --game=\'chunithm\')')
    parser.add_argument('--maimai', action="store_true", help='Perform scripts for maimai (shorthand for --game=\'maimai\')')
    parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
    parser.add_argument('--markdown', action="store_true", help='Print in GitHub-flavored markdown format')
    parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')
    parser.add_argument('--no_timestamp', action="store_true", help='Don\'t print timestamps on message output')
    parser.add_argument('--no_verbose', action="store_true", help='Only print significant changes and errors')


    # If there are custom arguments, extend the parser
    if custom_args:
        for custom_arg, options in custom_args.items():
            parser.add_argument(custom_arg, **options)

    args = parser.parse_args()

    if not args.game:
        if args.ongeki:
            args.game = 'ongeki'
        elif args.chunithm:
            args.game = 'chunithm'
        elif args.maimai:
            args.game = 'maimai'
        else:
            print_message('Please specify which game: --ongeki, --chunithm, --maimai', bcolors.FAIL, args)
            exit()

    if (hasattr(args, 'id') and args.id != 0) and \
       ((hasattr(args, 'date_from') and args.date_from != 0) or (hasattr(args, 'date_until') and args.date_until != 0)):
        print_message('--id and --date_from / --date_until arguments cannot be used together.', bcolors.FAIL, args)
        exit()

    # Import the game module dynamically
    game_module = importlib.import_module(args.game)

    # Set game module and game vars in the config
    game.GAME_MODULE = game_module
    game.GAME = args.game
    game.ARGS = args

    # Dynamically import the variables from game.py
    game_vars_module = importlib.import_module(f"{args.game}.game")
    game_paths_module = importlib.import_module(f"{args.game}.paths")

    # Set variables as attributes of the config module
    for var in dir(game_vars_module):
        if not var.startswith("__"):
            setattr(game, var, getattr(game_vars_module, var))

    for var in dir(game_paths_module):
        if not var.startswith("__"):
            setattr(game, var, getattr(game_paths_module, var))


def print_message(message, color_name='', args=None, log=False, is_verbose=False):
    if args is None:
        args = game.ARGS

    timestamp = ''
    print_color_name = color_name
    reset_color = bcolors.ENDC

    if not args.no_timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' '

    if args.escape:
        message = message.replace("\\", "\\\\").replace("\"", "\\\"").replace("'", r"\'")

    # is header
    if color_name == 'HEADER' or color_name == 'H2' or color_name == 'H3':
        print_color_name = bcolors.BOLD + bcolors.HEADER

    if args.nocolors:
        print_color_name = ''
        reset_color = ''

    if args.markdown:
        if color_name == 'H2':
            print_color_name = '## '
            reset_color = ''
        if color_name == 'H3':
            print_color_name = '### '
            reset_color = ''
        if color_name == 'HEADER':
            print_color_name = '**'
            reset_color = '**'
            print('')
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
        with open(game.LOCAL_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(timestamp + ' ' + message + '\n')

    # Do nothing if message is verbose and no_verbose is set
    if is_verbose is True and args.no_verbose is True:
        return
    else:
        print(timestamp + print_color_name + message + reset_color)

def lazy_print_song_header(msg, header_printed, args=None, log=False, is_verbose=False):
    if args is None:
        args = game.ARGS

    # If message should only print in verbose mode
    if is_verbose is True and args.no_verbose is True:
        return

    # If header was not printed yet print song name
    if header_printed[0] == 0:
        header_printed[0] += 1
        print_message(msg, 'HEADER', log=log)

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

def get_last_date(region, local_music_data):
    if region == 'jp':
        all_dates = [parse_date(x.get('date_added', ''), x.get('release', '')) for x in local_music_data if x.get('date_added') or x.get('release')]
    if region == 'intl':
        all_dates = [parse_date(x.get('date_intl_added', ''), x.get('date_intl_updated', '')) for x in local_music_data if x.get('date_intl_added') or x.get('date_intl_updated')]

    # Exclude None values when finding the latest date
    valid_dates = [date for date in all_dates if date is not None]

    if valid_dates:
        latest_date = reduce(lambda x, y: x if x > y else y, valid_dates).strftime('%Y%m%d')
        return latest_date
    else:
        # Handle the case where all dates are None
        return None

def renew_lastupdated(region, local_json_ex_path, dest_html_path):
    with open(local_json_ex_path, 'r', encoding='utf-8') as f:
        local_music_data = json.load(f)

    latest_date = get_last_date(region, local_music_data)

    with open(dest_html_path, 'r', encoding='utf-8') as f:
        local_html_data = f.read()

    pattern_map = {
        'jp': r'block lastupdated-jp\n\s*\|\s*(\d{8})',
        'intl': r'block lastupdated-intl\n\s*\|\s*(\d{8})'
    }

    if region not in pattern_map:
        return  # Exit if region is not recognized

    pattern = pattern_map[region]
    match = re.search(pattern, local_html_data, re.IGNORECASE)

    if match and match.group(1) == latest_date:
        return  # Exit if the date hasn't changed

    updated_html = re.sub(pattern, rf'block lastupdated-{region}\n  | {latest_date}', local_html_data, flags=re.IGNORECASE)

    with open(dest_html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print_message(f"Updated datestamp on {dest_html_path} to {latest_date}", '')


def json_to_id_value_map(json, id_key):
    return {int(song['id']):song for song in json}

def json_to_hash_value_map(json, *keys):
    return {generate_hash_from_keys(song, *keys): song for song in json}

def generate_hash_from_keys(song, *keys):
    # Check for game-specific hash keys
    if game.GAME_NAME == "maimai":
        if 'lev_utage' in song:
            keys = game.HASH_KEYS_UTAGE
        else:
            keys = game.HASH_KEYS
    else:
        # Use keys provided or default to empty list if not specified
        if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
            keys = keys[0]
        else:
            keys = keys

    hash_string = ''.join(str(song[key]) for key in keys)
    return generate_hash(hash_string)

def generate_hash(text_input):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the text input
    sha256_hash.update(text_input.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_result = sha256_hash.hexdigest()

    return hash_result

def get_target_song_list(song_list, local_diffs_log_path, id_key, date_key, hash_key):
    args = game.ARGS

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
    elif args.date != 0:
        return filter_songs_by_date(song_list, date_key, args.date, args.date)
    elif args.date_from != 0 or args.date_until != 0:
        latest_date = int(get_last_date('jp', song_list))

        if args.date_from == 0:
            args.date_from = latest_date

        if args.date_until == 0:
            args.date_until = latest_date

        return filter_songs_by_date(song_list, date_key, args.date_from, args.date_until)
    else:
        # get id list from diffs.txt
        return get_songs_from_diffs(song_list, local_diffs_log_path, hash_key)


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

def get_songs_from_diffs(song_list, diffs_log, identifier):
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
        if callable(identifier):
            # identifier is a function name
            song_identifier = identifier(song)
        else:
            song_identifier = generate_hash_from_keys(song, identifier)

        if song_identifier in unique_id:
            target_song_list.append(song)

    return target_song_list

def update_song_key(song, key, new_data, remove_comma=False, diff_count=None):

    # skip if new data is placeholder or empty
    if new_data in ['？', '?', '??', '???', '-', '']:
        return

    # Check if key exists in song
    if key in song:
        # Skip if new data is same as existing data
        if song[key] == new_data:
            return
        # skip if dest already has a valid value (other than ?) AND force overwrite is not set
        if (song[key] != '' and song[key] not in ['？', '?']) and not game.ARGS.overwrite:
            return

    # Write
    song[key] = new_data
    diff_count[0] += 1

    if remove_comma:
        song[key] = song[key].replace(',', '')

    return

def archive_deleted_song(song, deleted_data):
    deleted_date = datetime.now().strftime('%Y%m%d')
    song['deleted_date'] = f"{deleted_date}"
    deleted_data.append(song)


def print_keys_change(song, old_song, song_diffs):
    # Define the possible level keys (both normal and dx versions)
    any_changes = False

    # Iterate over each key in level_keys
    for key in game.LEVEL_KEYS:
        # Check if the key exists in both song and old_song
        if key in song and key in old_song:
            # Compare the values of the key in both dictionaries
            if song[key] != old_song[key]:
                # Print the difference in the format: key: old_value -> new_value

                # Lazy-print song name
                lazy_print_song_header(f"{song['title']}", song_diffs, log=True)

                print_message(f"- Level changed! {key}: {old_song[key]} → {song[key]}", bcolors.OKBLUE)
                any_changes = True

    new_tag_key = game.NEW_TAG_KEY
    if new_tag_key in song and new_tag_key in old_song:
        if song[new_tag_key] != old_song[new_tag_key]:
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)

            print_message(f"- New marker removed", bcolors.OKBLUE)
            any_changes = True


    for key in game.OTHER_KEYS:
        if key in song and key in old_song:
            if song[key] != old_song[key]:
                lazy_print_song_header(f"{song['title']}", song_diffs, log=True)

                print_message(f"- {key}: {old_song[key]} → {song[key]}", bcolors.ENDC)
                any_changes = True

    for key in game.LEVEL_CONST_KEYS:
        if key in song and key in old_song:
            if song[key] != old_song[key]:
                lazy_print_song_header(f"{song['title']}", song_diffs, log=True)
                if song[key] == "":
                    print_message(f"- Const cleared! {key}: (was {old_song[key]})", bcolors.WARNING)
                else:
                    print_message(f"- Const changed! {key}: {old_song[key]} → {song[key]}", bcolors.OKBLUE)

                any_changes = True

    return any_changes

# Check for keys that are removed or modified and print the changes.
def detect_key_removals_or_modifications(song, old_song, song_diffs):
    keys_removed = False

    # Check for key removal (keys in old_song but not in song)
    for key in old_song:
        if key in game.IGNORE_KEYS:
            continue
        if key not in song:
            # Most likely, "key" (unlock status) is removed
            # Lazy-print song name
            lazy_print_song_header(f"{song['title']}", song_diffs, log=True)

            print_message(f"- Song is now unlocked by default", bcolors.OKGREEN)
            keys_removed = True

    # Check for key modification
    keys_changed = print_keys_change(song, old_song, song_diffs)

    # Return True if any keys are removed or modified
    return keys_changed or keys_removed


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
        .replace('／', '')
        .replace('/', '')
        .replace('.', '')
        .replace('、', '')
        .replace(',', '')
    )

    return string

def get_and_save_page_to_local(url, output_path, local_cache_dir):
    response = requests.get(url)
    response.encoding = 'ansi'

    if not os.path.exists(local_cache_dir):
        os.makedirs(local_cache_dir)

    if response.status_code == 200:
        # Save the content to a local file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print_message(f"Saved {url} to {output_path}", bcolors.OKBLUE, is_verbose=True)
    else:
        print_message(f"Failed to retrieve {url}. Status code: {response.status_code}", bcolors.FAIL, log=True)

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


def sort_dict_keys(input_dict):
    """
    Sorts the keys of a dictionary according to the order specified in the KEY_ORDER global variable.

    Args:
        input_dict (dict): The dictionary to sort.

    Returns:
        dict: A new dictionary with keys sorted as per KEY_ORDER.
    """

    # Sort the keys based on their index in KEY_ORDER; keys not in KEY_ORDER are appended at the end
    sorted_keys = sorted(input_dict.keys(), key=lambda k: game.KEY_ORDER.index(k) if k in game.KEY_ORDER else float('inf'))

    return {key: input_dict[key] for key in sorted_keys}

def record_diffs(song, song_hash, diff_type):
    with open(game.LOCAL_DIFFS_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(diff_type.upper() + ' ' + song_hash + '\n')
