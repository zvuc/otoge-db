import argparse
import game
import shared
from shared.common_func import *

def main():
    game.GAME_MODULE.const.update_const_data()

if __name__ == "__main__":
    custom_args = {
        '--date': {'type':int, 'default':0, 'help':'Date added in YYYYMMDD'},
        '--date_from': {'type':int, 'default':0, 'help':'Date range from in YYYYMMDD'},
        '--date_until': {'type':int, 'default':0, 'help':'Date range until in YYYYMMDD'},
        '--id': {'default':0, 'help':'Song ID, single (2064) or range (802-2310)'},
        '--all': {'action':"store_true", 'help':'Run for all items'},
        '--overwrite': {'action':"store_true", 'help':'Overwrite existing values'},
        '--clear_cache': {'action':"store_true", 'help':'Clears local cache on run'},
        '--legacy': {'action':"store_true", 'help':'Match with legacy sgimera format'}
    }
    set_args_and_game_module(custom_args)
    main()
