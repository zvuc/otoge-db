import argparse
import game
import shared
from shared.common_func import *

def main():
    game.GAME_MODULE.intl.add_intl_info(game.ARGS)

if __name__ == "__main__":
    custom_args = {
        '--strict': {'action':"store_true", 'help':'Strict match songs by checking levels for all charts'}
    }
    set_args_and_game_module(custom_args)
    main()
