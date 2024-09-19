import argparse
import game
import shared
from shared.common_func import *

def main():
    game.GAME_MODULE.wiki.update_songs_extra_data()
    # renew_lastupdated(game.GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, game.GAME_MODULE.paths.LOCAL_INDEX_HTML_PATH, args)


if __name__ == "__main__":
    custom_args = {
        '--date': {'type':int, 'default':0, 'help':'Date added in YYYYMMDD'},
        '--date_from': {'type':int, 'default':0, 'help':'Date range from in YYYYMMDD'},
        '--date_until': {'type':int, 'default':0, 'help':'Date range until in YYYYMMDD'},
        '--id': {'default':0, 'help':'Song ID, single (2064) or range (802-2310)'},
        '--all': {'action':"store_true", 'help':'Run for all items'},
        '--noskip': {'action':"store_true", 'help':'Don\'t skip items that already have URL'},
        '--overwrite': {'action':"store_true", 'help':'Overwrite existing values'}
    }
    set_args_and_game_module(custom_args)
    main()
