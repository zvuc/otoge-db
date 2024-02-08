import argparse
import shared
from shared.common_func import *

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--ongeki', action="store_true", help='Perform scripts for ongeki')
parser.add_argument('--chunithm', action="store_true", help='Perform scripts for chunithm')
parser.add_argument('--maimai', action="store_true", help='Perform scripts for maimai')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--markdown', action="store_true", help='Print in GitHub-flavored markdown format')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')
parser.add_argument('--no_timestamp', action="store_true", help='Don\'t print timestamps on message output')
parser.add_argument('--skipwiki', action="store_true", help='Skip wiki fetch')

args = parser.parse_args()

if args.ongeki:
    print_message('Ongeki doesn\'t have an international release yet!', bcolors.FAIL, args)
    exit()
elif args.chunithm:
    import chunithm as game_module
elif args.maimai:
    import maimai as game_module
elif not args.ongeki and not args.chunithm and not args.maimai:
    print_message('Please specify which game: --ongeki, --chunithm, --maimai', bcolors.FAIL, args)
    exit()

game_module.intl.add_intl_info(args)
