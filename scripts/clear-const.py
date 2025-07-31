import argparse
import game
import shared
from shared.common_func import *

def main():
    # ipdb.set_trace()
    args = game.ARGS
    this_game = game.GAME_MODULE

    LOCAL_DIFFS_LOG_PATH = this_game.paths.LOCAL_DIFFS_LOG_PATH

    if not args.region:
        if args.jp:
            args.region = 'jp'
            target_json = this_game.paths.LOCAL_MUSIC_EX_JSON_PATH
        elif args.intl:
            if args.game == 'ongeki':
                print_message('Ongeki doesn\'t have an international release yet!', bcolors.FAIL, args)
                exit()
            args.region = 'intl'
            target_json = this_game.paths.LOCAL_INTL_MUSIC_EX_JSON_PATH
        else:
            print_message('Please specify which region: --jp, --intl', bcolors.FAIL, args)
            exit()


    print_message(f"Clearing chart constants", 'H2', log=True)

    with open(target_json, 'r', encoding='utf-8') as f:
        local_music_ex_data = json.load(f)

    target_song_list = get_target_song_list(local_music_ex_data, LOCAL_DIFFS_LOG_PATH, 'sort', 'date_added')

    if len(target_song_list) == 0:
        print_message("(Nothing to update)", bcolors.ENDC, log=True)
        return

    updated_count = 0

    for song in target_song_list:
        changed = False
        for key in list(song.keys()):
            if key in this_game.game.LEVEL_CONST_KEYS and song[key] != "":
                song[key] = ""
                changed = True
        if changed:
            updated_count += 1

    print_message(f"Cleared constants for {updated_count} song(s)", bcolors.OKGREEN, log=True)

    with open(target_json, 'w', encoding='utf-8') as f:
        json.dump(local_music_ex_data, f, ensure_ascii=False, indent=2)
    print_message(f"Saved changes to {target_json}", bcolors.OKBLUE, log=True)

if __name__ == "__main__":
    custom_args = {
        '--date': {'type':int, 'default':0, 'help':'Date added in YYYYMMDD'},
        '--date_from': {'type':int, 'default':0, 'help':'Date range from in YYYYMMDD'},
        '--date_until': {'type':int, 'default':0, 'help':'Date range until in YYYYMMDD'},
        '--id': {'default':0, 'help':'Song ID, single (2064) or range (802-2310)'},
        '--all': {'action':"store_true", 'default':True, 'help':'Run for all items'},
        '--region': {
            'type': str,
            'choices': ['maimai', 'ongeki', 'chunithm'],
            'help': 'Specify which data to run the script on'
        },
        '--jp': {'action':"store_true", 'help':'Run scripts for JP version (shorthand for --region=\'jp\')'},
        '--intl': {'action':"store_true", 'help':'Run scripts for INTL version (shorthand for --region=\'intl\')'},
    }
    set_args_and_game_module(custom_args)
    main()
