import const
from utils import *
from chartguide import *
import argparse

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--date_from', type=int, default=0, help='Date range from')
parser.add_argument('--date_until', type=int, default=0, help='Date range until')
parser.add_argument('--id', type=int, default=0, help='Song ID')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')

args = parser.parse_args()

update_chartguide_data(args.date_from, args.date_until, args.id, args.nocolors, args.escape)