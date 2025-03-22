import argparse
import game
import shared
from shared.common_func import *

def main():
    game.GAME_MODULE.intl.add_intl_info()

    # temporary since chuni has no sync_json_data yet
    if(game.GAME_NAME == 'maimai'):
        game.GAME_MODULE.intl.sync_json_data()

    # Update the last updated time
    renew_lastupdated('intl', game.GAME_MODULE.paths.LOCAL_INTL_MUSIC_EX_JSON_PATH, game.GAME_MODULE.paths.LOCAL_INDEX_HTML_PATH)

if __name__ == "__main__":
    custom_args = {
        '--strict': {'action':"store_true", 'help':'Strict match songs by checking levels for all charts'}
    }
    set_args_and_game_module(custom_args)
    main()
