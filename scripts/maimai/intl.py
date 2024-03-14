import ipdb
import requests
import json
import re
import copy
import random
import time
from shared.common_func import *
from maimai.paths import *
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

wiki_url = 'https://silentblue.remywiki.com/maimai_DX:BUDDiES_(Asia)'
errors_log = LOCAL_ERROR_LOG_PATH
request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

# Update on top of existing music-ex
def add_intl_info(args):
    print_message(f"Fetching International ver. song data from RemyWiki", bcolors.ENDC, args, errors_log, args.no_verbose)

    # Load JSON data
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    # Get Wiki page
    print_message(f"Request URL: {wiki_url}", bcolors.ENDC, args, errors_log, args.no_verbose)
    try:
        wiki = requests.get(wiki_url, timeout=5, headers=request_headers, allow_redirects=True)
    except requests.RequestException as e:
        print_message(f"Error while loading wiki page: {e}", bcolors.FAIL, args, errors_log, args.no_verbose)
        return


    # Parse HTML
    soup = BeautifulSoup(wiki.text, 'html.parser')

    # Find all tables with class 'bluetable'
    song_list = soup.find('span', id="New_Songs_/_DX_Charts", class_="mw-headline")
    table = song_list.find_next('table', class_='bluetable')
    rows = table.find_all('tr')

    # Initialize a dictionary to store songs
    wiki_song = {}

    # Iterate through each row
    for row in rows:
        # Reset utility vars
        song_matched = False
        # If this is empty, it means the song has single chart type (dx/std unknown)
        wiki_chart_type = ''
        # If B/A/E/M fields are empty, it means only Re:MAS is added at this time
        only_remas = False

        song_details = row.find_all('td')

        # skip header rows
        if len(song_details) <= 1:
            continue

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

        # Check if it's a UTAGE song
        utage_td = row.find('td', style="color:white; background:#dc39b8;", colspan="4")

        if utage_td:
            # Extract kanji and stars from UTAGE row
            title = song_details[1].text.strip()
            artist = song_details[2].text.strip()
            kanji = song_details[0].text.strip()[0]
            lev_utage = song_details[3].text.strip()

            # Add song to dictionary with date
            wiki_song = {
                'title': normalize_title(title),
                'artist': normalize_title(artist),
                'date': date,
                'kanji': kanji,
                'lev_utage': lev_utage
            }

            # Match UTAGE songs with JSON data using kanji and we_star
            for song in local_music_ex_data:
                # Match found, compare UTAGE chart levels
                if ('kanji' in song and
                    normalize_title(song['title']) == f'[{wiki_song['kanji']}]{wiki_song['title']}' and
                    normalize_title(song['artist']) == wiki_song['artist'] and
                    song['kanji'] == wiki_song['kanji']):

                    if ('lev_utage' in song and song['lev_utage'] == wiki_song['lev_utage'] or
                    'dx_lev_utage' in song and song['dx_lev_utage'] == wiki_song['lev_utage']):

                        print_message(f"{title}", 'HEADER', args, errors_log, args.no_verbose)

                        if song['intl'] == '0':
                            song['intl'] = "1"
                            print_message(f"Marked as available in Intl. ver.", bcolors.OKGREEN, args, errors_log, args.no_verbose)


                        if ('date_intl_added' not in song or song['date_intl_added'] == '000000'):
                            song['date_intl_added'] = wiki_song['date']
                            print_message(f"✅ Intl. added date (UTAGE)", bcolors.OKGREEN, args, errors_log, args.no_verbose)
                        else:
                            if 'date_intl_updated' not in song and int(wiki_song['date']) > int(song['date_intl_added']):
                                song['date_intl_updated'] = wiki_song['date']
                                print_message(f"✅ Intl. updated date (UTAGE)", bcolors.OKBLUE, args, errors_log, args.no_verbose)

                            # If date from wiki is later than existing date, consider it as updated date
                            elif 'date_intl_updated' in song and int(wiki_song['date']) > int(song['date_intl_updated']):
                                song['date_intl_updated'] = wiki_song['date']
                                print_message(f"✅ Intl. updated date (UTAGE)", bcolors.OKBLUE, args, errors_log, args.no_verbose)

                        break

        # Not a UTAGE song, process normally
        else:
            # If <small> tag is present, it means the song has both chart types
            small_tag = song_details[0].find('small')
            if small_tag:
                chart_type_text = small_tag.text.strip()

                if 'Standard' in chart_type_text:
                    wiki_chart_type = 'std'
                else:
                    wiki_chart_type = 'dx'


            title = song_details[0].find('a').text.strip()
            artist = song_details[1].text.strip()
            lev_bas = song_details[2].text.strip()
            lev_adv = song_details[3].text.strip()
            lev_exp = song_details[4].text.strip()
            lev_mas = song_details[5].text.strip()
            lev_remas = song_details[6].text.strip()

            # Add song to dictionary with date
            wiki_song = {
                'title': normalize_title(title),
                'artist': normalize_title(artist),
                'date': date,
                'lev_bas': lev_bas,
                'lev_adv': lev_adv,
                'lev_exp': lev_exp,
                'lev_mas': lev_mas,
                'lev_remas': lev_remas
            }

            # Set only_remas and is_update
            if (wiki_song['lev_bas'] == '-' and
                wiki_song['lev_adv'] == '-' and
                wiki_song['lev_exp'] == '-' and
                wiki_song['lev_mas'] == '-' and
                wiki_song['lev_remas'] != '-'):
                only_remas = True

            print_message(f"{title}", 'HEADER', args, errors_log, args.no_verbose)


            # Match wiki song with song from JSON file
            for song in local_music_ex_data:
                song_matched = False
                # Skip if UTAGE
                if 'kanji' in song:
                    continue

                # Match with title and artist
                if (normalize_title(song['title']) == wiki_song['title'] and normalize_title(song['artist']) == wiki_song['artist']):
                    # If wiki_chart_type is not explicitly set (single chart type)
                    # Get chart type from JSON song
                    if wiki_chart_type == '':
                        # Check chart type in json:
                        if 'lev_bas' in song:
                            wiki_chart_type == 'std'
                        elif 'dx_lev_bas' in song:
                            wiki_chart_type == 'dx'

                    if wiki_chart_type == 'std':
                        # if song only has remas added
                        if only_remas:
                            if song['lev_remas'] != wiki_song['lev_remas']:
                                if args.strict:
                                    print_message(f"One of the levels were not matched.", bcolors.FAIL, args, errors_log, args.no_verbose)
                                    continue
                                else:
                                    print_message(f"One of the levels were not matched.", bcolors.WARNING, args, errors_log, args.no_verbose)

                        else:
                            if ((song['lev_bas'] != wiki_song['lev_bas'] or
                                song['lev_adv'] != wiki_song['lev_adv'] or
                                song['lev_exp'] != wiki_song['lev_exp'] or
                                song['lev_mas'] != wiki_song['lev_mas'])):

                                if args.strict:
                                    print_message(f"One of the levels were not matched.", bcolors.FAIL, args, errors_log, args.no_verbose)
                                    continue
                                else:
                                    print_message(f"One of the levels were not matched.", bcolors.WARNING, args, errors_log, args.no_verbose)

                    elif wiki_chart_type == 'dx':
                         # if song only has remas added
                        if only_remas:
                            if song['dx_lev_remas'] != wiki_song['lev_remas']:
                                if args.strict:
                                    print_message(f"One of the levels were not matched.", bcolors.FAIL, args, errors_log, args.no_verbose)
                                    continue
                                else:
                                    print_message(f"One of the levels were not matched.", bcolors.WARNING, args, errors_log, args.no_verbose)

                        else:
                            if ((song['dx_lev_bas'] != wiki_song['lev_bas'] or
                                song['dx_lev_adv'] != wiki_song['lev_adv'] or
                                song['dx_lev_exp'] != wiki_song['lev_exp'] or
                                song['dx_lev_mas'] != wiki_song['lev_mas'])):

                                if args.strict:
                                    print_message(f"One of the levels were not matched.", bcolors.FAIL, args, errors_log, args.no_verbose)
                                    continue
                                else:
                                    print_message(f"One of the levels were not matched.", bcolors.WARNING, args, errors_log, args.no_verbose)

                    # Mark as available in Intl
                    if song['intl'] == '0':
                        song['intl'] = "1"
                        print_message(f"Marked as available in Intl. ver.", bcolors.OKGREEN, args, errors_log, args.no_verbose)

                    if song['intl'] != '0':
                        if only_remas or wiki_chart_type == 'std' or wiki_chart_type == 'dx':
                            if 'date_intl_updated' not in song or int(wiki_song['date']) > int(song['date_intl_updated']):
                                song['date_intl_updated'] = wiki_song['date']
                                print_message(f"✅ Intl. update date", bcolors.OKBLUE, args, errors_log, args.no_verbose)
                        else:
                            if ('date_intl_added' not in song or song['date_intl_added'] == '000000'):
                                song['date_intl_added'] = wiki_song['date']
                                print_message(f"✅ Intl. added date", bcolors.OKGREEN, args, errors_log, args.no_verbose)
                            else:
                                if 'date_intl_updated' not in song and int(wiki_song['date']) > int(song['date_intl_added']):
                                    song['date_intl_updated'] = wiki_song['date']
                                    print_message(f"✅ Intl. update date", bcolors.OKBLUE, args, errors_log, args.no_verbose)

                                # If date from wiki is later than existing date, consider it as updated date
                                elif 'date_intl_updated' in song and int(wiki_song['date']) > int(song['date_intl_updated']):
                                    song['date_intl_updated'] = wiki_song['date']
                                    print_message(f"✅ Intl. update date", bcolors.OKBLUE, args, errors_log, args.no_verbose)

                    song_matched = True
                    break

            # if song was not matched (if break was not triggered)
            if song_matched is not True:
                print_message(f"Song not matched", bcolors.FAIL, args, errors_log)

    # Write updated JSON data to file
    with open(LOCAL_MUSIC_EX_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)

