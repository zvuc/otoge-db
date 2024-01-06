import argparse
import shared

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--ongeki', action="store_true", help='Perform scripts for ongeki')
parser.add_argument('--chunithm', action="store_true", help='Perform scripts for chunithm')
parser.add_argument('--maimai', action="store_true", help='Perform scripts for maimai')
parser.add_argument('--date_from', type=int, default=0, help='Date range from')
parser.add_argument('--date_until', type=int, default=0, help='Date range until')
parser.add_argument('--id', default=0, help='Song ID')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')

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

game_module.wiki.update_songs_extra_data(args)