import argparse
import game
import shared
from shared.common_func import *

def main():
    game.GAME_MODULE.intl.add_intl_info()

    if game.GAME_NAME in ('maimai', 'chunithm'):
        game.GAME_MODULE.intl.sync_json_data()

    # Update the last updated time
    renew_lastupdated('intl', game.GAME_MODULE.paths.LOCAL_INTL_MUSIC_EX_JSON_PATH, game.GAME_MODULE.paths.LOCAL_META_PUG_PATH)

if __name__ == "__main__":
    custom_args = {
        '--strict': {'action':"store_true", 'help':'Strict match songs by checking levels for all charts'}
    }
    set_args_and_game_module(custom_args)
    main()
