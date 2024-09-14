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
parser.add_argument('--no_verbose', action="store_true", help='Only print significant changes and errors')
parser.add_argument('--skipwiki', action="store_true", help='Skip wiki fetch')

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

added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data = game_module.utils.load_new_song_data()
game_module.utils.renew_music_ex_data(added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data, args)
renew_lastupdated(game_module.paths.LOCAL_MUSIC_EX_JSON_PATH, game_module.paths.LOCAL_INDEX_HTML_PATH, args)
# game_module.utils.renew_lastupdated(game_module.paths.LOCAL_MUSIC_EX_JSON_PATH, game_module.paths.LOCAL_LEVELS_HTML_PATH, args)
# game_module.utils.renew_lastupdated(game_module.paths.LOCAL_MUSIC_EX_JSON_PATH, game_module.paths.LOCAL_NAMUWIKI_EXPORT_PATH, args)
