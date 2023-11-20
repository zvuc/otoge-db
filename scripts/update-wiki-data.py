from utils import *
from wikiwiki import *
import argparse

local_music_json_path = "data/music.json"
local_music_ex_json_path = "data/music-ex.json"
latest_date = int(get_last_date(local_music_json_path))

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--date_from', type=int, default=latest_date, help='Date range from')
parser.add_argument('--date_until', type=int, default=latest_date, help='Date range until')

args = parser.parse_args()


update_songs_extra_data(local_music_ex_json_path, args.date_from, args.date_until)