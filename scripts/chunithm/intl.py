# import ipdb
import requests
import json
from shared.common_func import *
from chunithm.paths import *

# Update on top of existing music-ex
def add_intl_info(args):
    fetch_intl_json_from_server()

    # Load JSON files
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r') as f:
        jp_song_list = json.load(f)
    with open(LOCAL_INTL_MUSIC_JSON_PATH, 'r') as f:
        intl_song_list = json.load(f)

    # Create a dictionary to store hashes from file B
    intl_song_hashes = {song['id']: song for song in intl_song_list}

    # Check for common items and update A.json
    for song in jp_song_list:
        jp_song_hash = song['id']
        if jp_song_hash in intl_song_hashes:
            if "intl" not in song or song["intl"] == '':
                song["intl"] = "1"
                print_message(f"Song added to International ver.: {song['title']}", bcolors.OKGREEN, args)
            # song["release_intl"] = intl_song_hashes[jp_song_hash]["release"]
            # if "key" in intl_song_hashes[jp_song_hash]:
            #     song["key_intl"] = intl_song_hashes[jp_song_hash]["key"]

    # Save updated A.json
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(jp_song_list, f, ensure_ascii=False, indent=2)

def fetch_intl_json_from_server():
    server_intl_music_data = requests.get(SERVER_INTL_MUSIC_DATA_URL).json()

    with open(LOCAL_INTL_MUSIC_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(server_intl_music_data, f, ensure_ascii=False, indent=2)
