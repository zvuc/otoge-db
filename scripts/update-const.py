import argparse
import shared
from shared.common_func import *

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--ongeki', action="store_true", help='Perform scripts for ongeki')
parser.add_argument('--chunithm', action="store_true", help='Perform scripts for chunithm')
parser.add_argument('--maimai', action="store_true", help='Perform scripts for maimai')
parser.add_argument('--date_from', type=int, default=0, help='Date range from in YYYYMMDD')
parser.add_argument('--date_until', type=int, default=0, help='Date range until in YYYYMMDD')
parser.add_argument('--id', default=0, help='Song ID, single (2064) or range (802-2310)')
parser.add_argument('--all', action="store_true", help='Run for all items')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')
parser.add_argument('--no_timestamp', action="store_true", help='Don\'t print timestamps on message output')
parser.add_argument('--clear_cache', action="store_true", help='Clears local cache on run')

args = parser.parse_args()

if args.ongeki:
    import ongeki as game_module
elif args.chunithm:
    import chunithm as game_module
elif args.maimai:
    import maimai as game_module
elif not args.ongeki and not args.chunithm and not args.maimai:
    print_message('Please specify which game: --ongeki, --chunithm, --maimai', bcolors.FAIL, args)
    exit()

if args.id != 0 and (args.date_from != 0 or args.date_until != 0):
    print_message('--id and --date_from / --date_until arguments cannot be used together.', bcolors.FAIL, args)
    exit()

game_module.const.update_const_data(args)
