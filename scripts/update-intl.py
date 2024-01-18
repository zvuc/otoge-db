import argparse
import shared

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--ongeki', action="store_true", help='Perform scripts for ongeki')
parser.add_argument('--chunithm', action="store_true", help='Perform scripts for chunithm')
parser.add_argument('--maimai', action="store_true", help='Perform scripts for maimai')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')
parser.add_argument('--skipwiki', action="store_true", help='Skip wiki fetch')

args = parser.parse_args()

if args.ongeki:
	import ongeki as game_module
elif args.chunithm:
	import chunithm as game_module
elif args.maimai:
	import maimai as game_module
elif not args.ongeki and not args.chunithm and not args.maimai:
	print('Please specify which game: --ongeki, --chunithm, --maimai')
	exit()

game_module.intl.add_intl_info(args)
