import ipdb
import requests
import json
import re
import copy
import random
import time
from shared.common_func import *
from chunithm.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:1st'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:AIR'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:AIR_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:STAR'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:STAR_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:AMAZON'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:AMAZON_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:CRYSTAL'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:CRYSTAL_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:PARADISE'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:PARADISE_LOST'

# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:NEW'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:NEW_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUN'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUN_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:LUMINOUS'

# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUPER_STAR'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUPER_STAR_PLUS'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:NEW_(Asia)'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:NEW_PLUS_(Asia)'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUN_(Asia)'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:SUN_PLUS_(Asia)'
# wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:LUMINOUS_(Asia)'
wiki_url = 'https://silentblue.remywiki.com/CHUNITHM:LUMINOUS_PLUS_(Asia)'

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

# Update on top of existing music-ex
def add_intl_info():
    total_diffs = [0]

    print_message(f"Fetching International ver. song data from RemyWiki", 'H2', log=True)

    # Load JSON data
    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Get Wiki page
    print_message(f"Request URL: {wiki_url}", bcolors.ENDC, log=True, is_verbose=True)
    try:
        wiki = requests.get(wiki_url, timeout=5, headers=request_headers, allow_redirects=True)
    except requests.RequestException as e:
        print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, log=True, is_verbose=True)
        return


    # Parse HTML
    soup = BeautifulSoup(wiki.text, 'html.parser')

    # Find all tables with class 'bluetable'
    # song_list = soup.find('span', id="Song_List", class_="mw-headline")
    # song_list = soup.find('span', id="New_Songs", class_="mw-headline")
    song_list = soup.find('span', id="New_Songs_/_WORLD'S_END_Charts", class_="mw-headline")
    table = song_list.find_next('table', class_='bluetable')
    rows = table.find_all('tr')

    # Initialize a dictionary to store songs
    wiki_song = {}

    # Iterate through each row
    for row in rows:
        header_printed = [0]

        # Reset utility vars
        song_matched = False
        # If B/A/E/M fields are empty, it means only ULTIMA is added at this time
        only_ultima = False

        song_details = row.find_all('td')

        # skip header rows
        if len(song_details) <= 1:
            continue

        title = song_details[0].text.strip()
        artist = song_details[1].text.strip()

        # Find the closest previous th tag to get the datestamp
        date_stamp = None
        prev_th = row.find_previous('th')
        while prev_th:
            if prev_th.get('id') and re.match(r'\d{8}', prev_th['id']):
                date_stamp = prev_th
                break
            prev_th = prev_th.find_previous('th')

        if date_stamp:
            # Extract the date in yyyymmdd format if the id attribute matches
            date = date_stamp['id']
        else:
            # Skip if no datestamp found
            continue

        # Check if it's a WORLDS END song
        worlds_end_td = row.find('td', style="color:white; background:black;", colspan="5")
        if worlds_end_td:
            # Extract kanji and stars from WORLDS END row
            we_content = worlds_end_td.text.strip()
            we_kanji = we_content[0]
            we_star_count = we_content.count('☆')

            # Convert star count to integer value
            if we_star_count == 1:
                we_star = '1'
            elif we_star_count == 2:
                we_star = '3'
            elif we_star_count == 3:
                we_star = '5'
            elif we_star_count == 4:
                we_star = '7'
            elif we_star_count == 5:
                we_star = '9'
            else:
                # Handle unexpected star count
                we_star = None

            if we_star is not None:
                # Add song to dictionary with date
                wiki_song = {
                    'title': normalize_title(title),
                    'artist': normalize_title(artist),
                    'date': date,
                    'we_kanji': we_kanji,
                    'we_star': we_star
                }

                # Match WORLDS END songs with JSON data using we_kanji and we_star
                for song in local_music_ex_data:
                    old_song = copy.copy(song)

                    # Match found, compare WORLDS END chart levels
                    if (normalize_title(song['title']) == wiki_song['title'] and
                        song['we_kanji'] == wiki_song['we_kanji']):

                        # if normalize_title(song['artist']) == wiki_song['artist']:
                        #     print_message(f"Perfect match found", bcolors.ENDC)
                        # else:
                        #     print_message(f"JSON: {song['artist']}", bcolors.ENDC)
                        #     print_message(f"Wiki: {artist}", bcolors.ENDC)
                        #     response = input("Artist name mismatch. Proceed? (y/n): ")

                        #     # Checking the user's response
                        #     if response.lower() == 'y':
                        #         print("Proceeding with matched song")
                        #     else:
                        #         print("Continue matching with other songs in JSON...")
                        #         continue

                        if (song['we_star'] != we_star):
                            lazy_print_song_header(f"[{we_kanji}] {title}", header_printed, log=True, is_verbose=True)

                            if game.ARGS.strict:
                                print_message(f"- WORLDS END level (stars) mismatch. (JSON: {song['we_star']} vs Wiki: {we_star})", bcolors.FAIL, log=True, is_verbose=True)
                                continue
                            else:
                                print_message(f"- WORLDS END level (stars) mismatch. (JSON: {song['we_star']} vs Wiki: {we_star})", bcolors.WARNING, log=True, is_verbose=True)


                        # Match found, update JSON data
                        if song['intl'] == "0":
                            song['intl'] = "1"
                            lazy_print_song_header(f"[{we_kanji}] {title}", header_printed, log=True, is_verbose=True)
                            print_message(f"- Marked as available in Intl. ver.", bcolors.OKGREEN, log=True)

                        if 'date_intl_added' not in song or song['date_intl_added'] == '':
                            lazy_print_song_header(f"[{we_kanji}] {title}", header_printed, log=True, is_verbose=True)
                            print_message(f"- Date added ({wiki_song['date']})", bcolors.OKGREEN, log=True)
                            song['date_intl_added'] = wiki_song['date']

                        song_matched = True

                        if old_song == song:
                            lazy_print_song_header(f"[{we_kanji}] {title}", header_printed, log=True, is_verbose=True)
                            print_message("- Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
                        else:
                            total_diffs[0] += 1

                        break

        # Not a WORLDS END song, process normally
        else:
            lev_bas = song_details[2].text.strip()
            lev_adv = song_details[3].text.strip()
            lev_exp = song_details[4].text.strip()
            lev_mas = song_details[5].text.strip()
            lev_ult = song_details[6].text.strip()

            # Add song to dictionary with date
            wiki_song = {
                'title': normalize_title(title),
                'artist': normalize_title(artist),
                'date': date,
                'lev_bas': lev_bas,
                'lev_adv': lev_adv,
                'lev_exp': lev_exp,
                'lev_mas': lev_mas,
                'lev_ult': lev_ult
            }

            # Set only_remas and is_update
            if (wiki_song['lev_bas'] == '-' and
                wiki_song['lev_adv'] == '-' and
                wiki_song['lev_exp'] == '-' and
                wiki_song['lev_mas'] == '-' and
                wiki_song['lev_ult'] != '-'):
                only_ultima = True


            # Match non-WORLDS END songs with JSON data
            for song in local_music_ex_data:
                old_song = copy.copy(song)

                # Match found, compare level numbers
                if normalize_title(song['title']) == wiki_song['title']:
                    # if normalize_title(song['artist']) == wiki_song['artist']:
                    #     print_message(f"Perfect match found", bcolors.ENDC)
                    # else:
                    #     print_message(f"JSON: {song['artist']}", bcolors.ENDC)
                    #     print_message(f"Wiki: {artist}", bcolors.ENDC)
                    #     response = input("Artist name mismatch. Proceed? (y/n): ")

                    #     # Checking the user's response
                    #     if response.lower() == 'y':
                    #         print("Proceeding with matched song")
                    #     else:
                    #         print("Continue matching with other songs in JSON...")
                    #         continue

                    if only_ultima:
                        # Double-check with level
                        if song['lev_ult'] != wiki_song['lev_ult']:
                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                            if game.ARGS.strict:
                                print_message(f"- ULTIMA level mismatch. (JSON: {song['lev_ult']} vs Wiki: {wiki_song['lev_ult']})", bcolors.FAIL, log=True, is_verbose=True)
                                continue
                            else:
                                print_message(f"- ULTIMA level mismatch. (JSON: {song['lev_ult']} vs Wiki: {wiki_song['lev_ult']})", bcolors.WARNING, log=True, is_verbose=True)

                        if ('date_intl_updated' not in song or int(song['date_intl_updated']) < int(wiki_song['date'])):
                            song['date_intl_updated'] = wiki_song['date']
                            lazy_print_song_header(f"{title}", header_printed, log=True)
                            print_message(f"- Added update date", bcolors.OKBLUE, log=True)

                        song_matched = True

                        if old_song == song:
                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)
                            print_message("- Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
                        else:
                            total_diffs[0] += 1

                        break

                    else:
                        # Double-check with levels
                        if (song['lev_bas'] != wiki_song['lev_bas'] or
                            song['lev_adv'] != wiki_song['lev_adv'] or
                            song['lev_exp'] != wiki_song['lev_exp'] or
                            song['lev_mas'] != wiki_song['lev_mas']):

                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)

                            if game.ARGS.strict:
                                print_message(f"- One of the levels were not matched. (JSON: {song['lev_bas']}/{song['lev_adv']}/{song['lev_exp']}/{song['lev_mas']} vs Wiki: {wiki_song['lev_bas']}/{wiki_song['lev_adv']}/{wiki_song['lev_exp']}/{wiki_song['lev_mas']})", bcolors.FAIL, log=True)
                                continue
                            else:
                                print_message(f"- One of the levels were not matched. (JSON: {song['lev_bas']}/{song['lev_adv']}/{song['lev_exp']}/{song['lev_mas']} vs Wiki: {wiki_song['lev_bas']}/{wiki_song['lev_adv']}/{wiki_song['lev_exp']}/{wiki_song['lev_mas']})", bcolors.WARNING, log=True)

                        # Update JSON data
                        if song['intl'] == "0":
                            song['intl'] = "1"
                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)
                            print_message(f"- Marked as available in Intl. ver.", bcolors.OKGREEN, log=True, is_verbose=True)

                        if 'date_intl_added' not in song or song['date_intl_added'] == '':
                            song['date_intl_added'] = wiki_song['date']
                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)
                            print_message(f"- Added date", bcolors.OKGREEN, log=True, is_verbose=True)

                        # if song['date_added'] == '':
                        #     print_message(f"Date added ({wiki_song['date']})", bcolors.OKGREEN, log=True, is_verbose=True)
                        #     song['date_added'] = wiki_song['date']
                        # elif song['date_added'] != wiki_song['date']:
                        #     print_message(f"Date updated: (json: {song['date_added']} / wiki: {wiki_song['date']})", bcolors.OKGREEN, log=True, is_verbose=True)
                        #     song['date_added'] = wiki_song['date']

                        song_matched = True

                        if old_song == song:
                            lazy_print_song_header(f"{title}", header_printed, log=True, is_verbose=True)
                            print_message("- Done (Nothing updated)", bcolors.ENDC, is_verbose=True)
                        else:
                            total_diffs[0] += 1

                        break

        # if song was not matched (if break was not triggered)
        if song_matched is not True:
            if worlds_end_td:
                lazy_print_song_header(f"[{we_kanji}] {title}", header_printed, log=True)
            else:
                lazy_print_song_header(f"{title}", header_printed, log=True)

            print_message(f"- Song not found in JSON file", bcolors.FAIL, log=True)

    if total_diffs[0] == 0:
        print_message("(Nothing updated)", bcolors.ENDC, log=True)

    # Write updated JSON data to file
    with open(LOCAL_INTL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)



