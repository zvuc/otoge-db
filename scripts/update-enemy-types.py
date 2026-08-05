import argparse
import sys
import game
import shared
from shared.common_func import *

# Inject default --ongeki parameter if not specified
if not any(arg in sys.argv for arg in ("--ongeki", "--chunithm", "--maimai", "--game")):
    sys.argv.append("--ongeki")

def main():
    if game.GAME == 'ongeki':
        import ongeki.enemy_types
        ongeki.enemy_types.update_enemy_types()
    else:
        print_message(f"Game {game.GAME} does not support updating enemy types.", bcolors.FAIL)
        sys.exit(1)

if __name__ == "__main__":
    custom_args = {
        "--refresh": {"action": "store_true", "help": "Force refresh the YouTube videos cache."},
        "--dry-run": {"action": "store_true", "help": "Dry run (detect but do not write to JSON)."},
        "--id": {"type": str, "help": "Process only a specific song ID."},
        "--limit": {"type": int, "default": 0, "help": "Limit the number of songs to process (0 for unlimited)."}
    }
    set_args_and_game_module(custom_args)
    main()
