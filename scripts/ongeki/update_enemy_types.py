#!/usr/bin/env python3
import os
import sys
import json
import re
import argparse
import subprocess
import tempfile
import unicodedata
from PIL import Image

# Ensure root is in sys.path
sys.path.append(os.getcwd())

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
                print("Loaded YouTube videos list from cache.")
                return json.load(f)
        except Exception as e:
            print(f"Error reading cache, will re-fetch: {e}")

    print("Fetching video list from YouTube channel @ongeki_humen...")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s\t%(id)s",
        "https://www.youtube.com/@ongeki_humen/videos"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"Error calling yt-dlp: {result.stderr}")
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

    print(f"Successfully cached {len(videos)} videos.")
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
    print(f"Getting stream URL for: {video_url}")
    cmd = ["yt-dlp", "-g", "-f", "bestvideo[height<=1080]", video_url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to get stream URL: {result.stderr}")
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
            print(f"ffmpeg frame extraction failed: {res.stderr}")
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

        print(f"Color Analysis -> Avg R: {avg_r:.1f}, Avg G: {avg_g:.1f}, Avg B: {avg_b:.1f}")

        # Classification logic based on dominant colors
        if avg_r > avg_g and avg_r > avg_b:
            return "FIRE"
        elif avg_g > avg_b:
            return "LEAF"
        else:
            return "AQUA"
            
    except Exception as e:
        print(f"Error during frame extraction/analysis: {e}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    parser = argparse.ArgumentParser(description="Auto-detect ONGEKI enemy types from YouTube chart videos.")
    parser.add_argument("--refresh", action="store_true", help="Force refresh the YouTube videos cache.")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (detect but do not write to JSON).")
    parser.add_argument("--id", type=str, help="Process only a specific song ID.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of songs to process (0 for unlimited).")
    args = parser.parse_args()

    # Load song data
    if not os.path.exists(LOCAL_MUSIC_EX_JSON_PATH):
        print(f"Error: Could not find {LOCAL_MUSIC_EX_JSON_PATH}")
        sys.exit(1)

    with open(LOCAL_MUSIC_EX_JSON_PATH, "r", encoding="utf-8") as f:
        music_ex = json.load(f)

    # Fetch cached videos
    yt_videos = get_youtube_videos(force_refresh=args.refresh)
    
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
        if args.id and song.get("id") != args.id:
            continue
            
        # Only process if enemy_type is empty (or missing)
        if not song.get("enemy_type"):
            target_songs.append(song)

    print(f"Found {len(target_songs)} songs missing enemy type.")
    if not target_songs:
        print("Nothing to process.")
        return

    processed_count = 0
    updated_songs = []

    for song in target_songs:
        if args.limit > 0 and processed_count >= args.limit:
            print(f"Reached limit of {args.limit} songs.")
            break

        title = song.get("title", "")
        song_id = song.get("id", "")
        norm_title = normalize_title(title)
        
        print(f"\nProcessing song ID {song_id}: '{title}' (Normalized: '{norm_title}')")

        # Try to find a matched video
        match = normalized_videos.get(norm_title)
        if not match:
            # Fallback fuzzy matching (check if normalized video title contains song title)
            found = False
            for v_norm, (v_orig, v_url) in normalized_videos.items():
                if norm_title in v_norm or v_norm in norm_title:
                    print(f"Fuzzy matched to video: '{v_orig}'")
                    match = (v_orig, v_url)
                    found = True
                    break
            if not found:
                print(f"Could not find YouTube video match for '{title}'. Skipping.")
                continue
        else:
            print(f"Matched video: '{match[0]}'")

        video_url = match[1]
        detected_attr = extract_and_detect_attribute(video_url)
        
        if detected_attr:
            print(f"SUCCESS: Song '{title}' (ID {song_id}) -> Detected enemy type: {detected_attr}")
            song["enemy_type"] = detected_attr
            updated_songs.append(song)
            processed_count += 1
        else:
            print(f"FAILED to extract/detect attribute for '{title}'. Skipping.")

    print(f"\nProcessed {processed_count} songs.")
    
    if updated_songs and not args.dry_run:
        print(f"Saving changes to {LOCAL_MUSIC_EX_JSON_PATH}...")
        sort_and_save_json(music_ex, LOCAL_MUSIC_EX_JSON_PATH)
        print("Changes saved successfully!")
    elif args.dry_run:
        print("Dry-run mode. No changes saved.")

if __name__ == "__main__":
    main()
