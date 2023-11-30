import const
from utils import *
import argparse

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--nocolors', action="store_true", help='Print messages in color')
parser.add_argument('--escape', action="store_true", help='Escape unsafe characters for git message output')
parser.add_argument('--skipwiki', action="store_true", help='Skip wiki fetch')

args = parser.parse_args()

new_song_data = load_new_song_data()
renew_music_ex_data(new_song_data, args.nocolors, args.escape, args.skipwiki)
renew_lastupdated(const.LOCAL_INDEX_HTML_PATH)
renew_lastupdated(const.LOCAL_LEVELS_HTML_PATH)
renew_lastupdated(const.LOCAL_NAMUWIKI_EXPORT_PATH)

# asdf