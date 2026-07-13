#!/usr/bin/env python3
import os
import sys
import json
import re
import subprocess
import tempfile
import unicodedata
from PIL import Image

# Ensure root is in sys.path
sys.path.append(os.getcwd())

# Inject default --ongeki parameter if not specified
if "--ongeki" not in sys.argv and "--game" not in sys.argv:
    sys.argv.append("--ongeki")

import game
from ongeki.paths import *
from shared.common_func import *

# Path for cached youtube videos list
YT_CACHE_PATH = "ongeki/youtube_videos_cache.json"

def get_youtube_videos(force_refresh=False):
    """
    Fetches the video titles and links from the YouTube channel `@ongeki_humen`
    and caches them locally to avoid hitting YouTube rate limits.
    """
    if not force_refresh and os.path.exists(YT_CACHE_PATH):
        try:
            with open(YT_CACHE_PATH, "r", encoding="utf-8") as f:
                print_message("Loaded YouTube videos list from cache.", is_verbose=True)
                return json.load(f)
        except Exception as e:
            print_message(f"Error reading cache, will re-fetch: {e}", bcolors.WARNING, is_verbose=True)

    print_message("Fetching video list from YouTube channel @ongeki_humen...", is_verbose=True)
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s\t%(id)s",
        "https://www.youtube.com/@ongeki_humen/videos"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print_message(f"Error calling yt-dlp: {result.stderr}", bcolors.FAIL)
        sys.exit(1)

    videos = {}
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if not line or "\t" not in line:
            continue
        title, vid_id = line.split("\t", 1)
        videos[title.strip()] = f"https://www.youtube.com/watch?v={vid_id.strip()}"

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(YT_CACHE_PATH), exist_ok=True)
    with open(YT_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    print_message(f"Successfully cached {len(videos)} videos.", is_verbose=True)
    return videos

def extract_song_title_from_video(video_title):
    """
    Extracts the clean song title from video titles like:
    '[オンゲキ] Λlteration [MASTER 14] (譜面確認)' -> 'Λlteration'
    """
    # Remove prefix '[オンゲキ]'
    t = re.sub(r"^\[オンゲキ\]\s*", "", video_title)
    # Remove suffix like '[MASTER 14] (譜面確認)' or '(譜面確認)'
    t = re.sub(r"\s*\[[^\]]+\]\s*\(譜面確認\)$", "", t)
    t = re.sub(r"\s*\(譜面確認\)$", "", t)
    return t.strip()

def normalize_title(title):
    """
    Normalizes a song title to facilitate robust matching.
    """
    if not title:
        return ""
    # NFKC normalizes full-width to half-width characters
    title = unicodedata.normalize('NFKC', title)
    title = title.lower()
    # Remove spaces and common punctuation/symbols
    title = re.sub(r"\s+", "", title)
    title = re.sub(r"[・\-~〜☆★+=&＆!！？?*()（）[\]「」'\"’“”]", "", title)
    return title

def extract_and_detect_attribute(video_url):
    """
    Extracts a frame at 10 seconds using stream seeking,
    resizes it to 480x854, crops the badge, and detects the color.
    """
    print_message(f"Getting stream URL for: {video_url}", is_verbose=True)
    cmd = ["yt-dlp", "-g", "-f", "bestvideo[height<=1080]", video_url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_message(f"Failed to get stream URL: {result.stderr}", bcolors.WARNING, is_verbose=True)
        return None

    stream_url = result.stdout.strip()
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Seek to 10s and extract 1 frame
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-ss", "00:00:10",
            "-i", stream_url,
            "-vframes", "1",
            "-q:v", "2",
            tmp_path
        ]
        res = subprocess.run(ffmpeg_cmd, capture_output=True)
        if res.returncode != 0 or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            print_message(f"ffmpeg frame extraction failed: {res.stderr}", bcolors.WARNING, is_verbose=True)
            return None

        # Load and resize to canonical Vertical Play resolution
        img = Image.open(tmp_path)
        img = img.resize((480, 854))

        # Heart of the attribute badge circle (relative to the full rescaled play screen)
        x_start, x_end = 415 + 12, 415 + 19
        y_start, y_end = 285 + 14, 285 + 22

        pixels = []
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                r, g, b = img.getpixel((x, y))[:3]
                pixels.append((r, g, b))

        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)

        print_message(f"Color Analysis -> Avg R: {avg_r:.1f}, Avg G: {avg_g:.1f}, Avg B: {avg_b:.1f}", is_verbose=True)

        # Classification logic based on dominant colors
        if avg_r > avg_g and avg_r > avg_b:
            return "FIRE"
        elif avg_g > avg_b:
            return "LEAF"
        else:
            return "AQUA"
            
    except Exception as e:
        print_message(f"Error during frame extraction/analysis: {e}", bcolors.WARNING, is_verbose=True)
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    # Load song data
    if not os.path.exists(LOCAL_MUSIC_EX_JSON_PATH):
        print_message(f"Error: Could not find {LOCAL_MUSIC_EX_JSON_PATH}", bcolors.FAIL)
        sys.exit(1)

    with open(LOCAL_MUSIC_EX_JSON_PATH, "r", encoding="utf-8") as f:
        music_ex = json.load(f)

    # Fetch cached videos
    yt_videos = get_youtube_videos(force_refresh=game.ARGS.refresh)
    
    # Map normalized video title to video URL
    normalized_videos = {}
    for video_title, url in yt_videos.items():
        clean_title = extract_song_title_from_video(video_title)
        norm_title = normalize_title(clean_title)
        # Avoid overwriting with lower difficulty videos if MASTER is available
        if norm_title not in normalized_videos or "[MASTER" in video_title:
            normalized_videos[norm_title] = (video_title, url)

    # Filter target songs
    target_songs = []
    for song in music_ex:
        # If specific ID is requested, filter by it
        if game.ARGS.id and song.get("id") != game.ARGS.id:
            continue
            
        # Only process if enemy_type is empty (or missing)
        if not song.get("enemy_type"):
            target_songs.append(song)

    print_message(f"Found {len(target_songs)} songs missing enemy type.", is_verbose=True)
    if not target_songs:
        print_message("Nothing to process.", is_verbose=True)
        return

    processed_count = 0
    updated_songs = []

    # Print markdown header if required
    if game.ARGS.markdown:
        print_message("Updated Enemy Types", 'H3')

    for song in target_songs:
        if game.ARGS.limit > 0 and processed_count >= game.ARGS.limit:
            print_message(f"Reached limit of {game.ARGS.limit} songs.", is_verbose=True)
            break

        title = song.get("title", "")
        song_id = song.get("id", "")
        norm_title = normalize_title(title)
        
        header_printed = [0]
        song_header = f"{title}"

        # Try to find a matched video
        match = normalized_videos.get(norm_title)
        if not match:
            # Fallback fuzzy matching (check if normalized video title contains song title)
            found = False
            for v_norm, (v_orig, v_url) in normalized_videos.items():
                if norm_title in v_norm or v_norm in norm_title:
                    print_message(f"Fuzzy matched to video: '{v_orig}'", is_verbose=True)
                    match = (v_orig, v_url)
                    found = True
                    break
            if not found:
                lazy_print_song_header(song_header, header_printed, is_verbose=True)
                print_message(f"- Could not find YouTube video match", bcolors.WARNING, is_verbose=True)
                continue
        else:
            print_message(f"Matched video: '{match[0]}'", is_verbose=True)

        video_url = match[1]
        detected_attr = extract_and_detect_attribute(video_url)
        
        if detected_attr:
            lazy_print_song_header(song_header, header_printed, log=True)
            print_message(f"- Detected enemy type: {detected_attr}", bcolors.OKGREEN, log=True)
            song["enemy_type"] = detected_attr
            updated_songs.append(song)
            processed_count += 1
        else:
            lazy_print_song_header(song_header, header_printed, log=True)
            print_message(f"- FAILED to extract/detect attribute", bcolors.FAIL, log=True)

    print_message(f"Processed {processed_count} songs.", is_verbose=True)
    
    if updated_songs and not game.ARGS.dry_run:
        print_message(f"Saving changes to {LOCAL_MUSIC_EX_JSON_PATH}...", is_verbose=True)
        sort_and_save_json(music_ex, LOCAL_MUSIC_EX_JSON_PATH)
        print_message("Changes saved successfully!", is_verbose=True)
    elif game.ARGS.dry_run:
        print_message("Dry-run mode. No changes saved.", is_verbose=True)

if __name__ == "__main__":
    custom_args = {
        "--refresh": {"action": "store_true", "help": "Force refresh the YouTube videos cache."},
        "--dry-run": {"action": "store_true", "help": "Dry run (detect but do not write to JSON)."},
        "--id": {"type": str, "help": "Process only a specific song ID."},
        "--limit": {"type": int, "default": 0, "help": "Limit the number of songs to process (0 for unlimited)."}
    }
    set_args_and_game_module(custom_args)
    main()
