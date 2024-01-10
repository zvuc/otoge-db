import json
import re
import hashlib
from functools import reduce
from .terminal import bcolors
from datetime import datetime

def print_message(message, color_name, args, log=''):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reset_color = bcolors.ENDC

    if args.escape:
        message = message.replace("'", r"\'")

    # if --nocolors is set
    if args.nocolors:
        color_name = ''
        reset_color = ''

    if log:
        with open(log, 'a', encoding='utf-8') as f:
            f.write(timestamp + ' ' + message + '\n')

    print(timestamp + ' ' + color_name + message + reset_color)

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

def generate_hash(text_input):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the text input
    sha256_hash.update(text_input.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_result = sha256_hash.hexdigest()

    return hash_result