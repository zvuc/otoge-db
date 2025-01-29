import argparse
import game
import shared
from shared.common_func import *

def main():
    # Load new song data
    added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data = game.GAME_MODULE.songs.load_new_song_data()

    # Renew music ex data
    game.GAME_MODULE.songs.renew_music_ex_data(
        added_songs, updated_songs, unchanged_songs, removed_songs, old_local_music_data
    )

    # Update the last updated time
    renew_lastupdated('jp', game.GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, game.GAME_MODULE.paths.LOCAL_INDEX_HTML_PATH)
    # Uncomment other renew_lastupdated calls if needed
    # renew_lastupdated(GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, GAME_MODULE.paths.LOCAL_LEVELS_HTML_PATH)
    # renew_lastupdated(GAME_MODULE.paths.LOCAL_MUSIC_EX_JSON_PATH, GAME_MODULE.paths.LOCAL_NAMUWIKI_EXPORT_PATH)

if __name__ == "__main__":
    set_args_and_game_module()
    main()
