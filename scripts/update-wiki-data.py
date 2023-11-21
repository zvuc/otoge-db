from utils import *
from wikiwiki import *
import argparse

local_music_json_path = "data/music.json"
local_music_ex_json_path = "data/music-ex.json"

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--date_from', type=int, default=0, help='Date range from')
parser.add_argument('--date_until', type=int, default=0, help='Date range until')
parser.add_argument('--id', type=int, default=0, help='Song ID')

args = parser.parse_args()


update_songs_extra_data(local_music_ex_json_path, args.date_from, args.date_until, args.id)