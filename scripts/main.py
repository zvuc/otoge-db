from utils import *

server_music_data_url = "https://ongeki.sega.jp/assets/data/music.json"
server_music_jacket_base_url = "https://ongeki.sega.jp/assets/img/music/"
local_music_json_path = "data/music.json"
local_music_ex_json_path = "data/music-ex.json"
local_index_html_path = "index.html"

new_song_data = load_new_song_data(local_music_json_path, server_music_data_url)
renew_music_ex_data(new_song_data, local_music_ex_json_path, server_music_jacket_base_url)
renew_lastupdated(local_music_ex_json_path, local_index_html_path)
