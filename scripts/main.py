from utils import *

server_music_data_url = "https://ongeki.sega.jp/assets/json/music/music_red.json"
server_music_jacket_base_url = "https://ongeki.sega.jp/assets/img/pages/music/thumbnail/"
local_music_json_path = "data/music.json"
local_music_ex_json_path = "data/music-ex.json"
local_diffs_log_path = "diffs.txt"
local_index_html_path = "index.html"
local_levels_html_path = "lv/index.html"
local_namuwiki_export_path = "namuwiki-export.html"

new_song_data = load_new_song_data(local_music_json_path, server_music_data_url)
renew_music_ex_data(new_song_data, local_music_ex_json_path, server_music_jacket_base_url, local_diffs_log_path)
renew_lastupdated(local_music_ex_json_path, local_index_html_path)
renew_lastupdated(local_music_ex_json_path, local_levels_html_path)
renew_lastupdated(local_music_ex_json_path, local_namuwiki_export_path)
