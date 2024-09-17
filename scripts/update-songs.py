import argparse
import game
import shared
from shared.common_func import *

def main():
    # Load new song data
    added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data = game.GAME_MODULE.utils.load_new_song_data()

    # Renew music ex data
    game.GAME_MODULE.utils.renew_music_ex_data(
        added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data, ARGS
    )

    # Update the last updated time
    renew_lastupdated(game.GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, game.GAME_MODULE.paths.LOCAL_INDEX_HTML_PATH, ARGS)
    # Uncomment other renew_lastupdated calls if needed
    # renew_lastupdated(GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, GAME_MODULE.paths.LOCAL_LEVELS_HTML_PATH, ARGS)
    # renew_lastupdated(GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, GAME_MODULE.paths.LOCAL_NAMUWIKI_EXPORT_PATH, ARGS)

if __name__ == "__main__":
    custom_args = {
        '--skipwiki': {'action':"store_true", 'help':'Skip wiki fetch'}
    }
    set_args_and_game_module(custom_args)
    main()
