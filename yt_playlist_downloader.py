import os
import subprocess
import argparse

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def extract_playlists(channel_url, cookies_path):
    print("🔍 Extracting playlists from channel...")
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_path, "--flat-playlist", "--print", "%(playlist_url)s", channel_url],
            capture_output=True, text=True, check=True
        )
        playlist_urls = list(set(line.strip() for line in result.stdout.splitlines() if "playlist?list=" in line))
        return playlist_urls
    except subprocess.CalledProcessError as e:
        print("❌ Failed to extract playlists.")
        print(e.stderr)
        return []

def get_playlist_title(playlist_url, cookies_path):
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_path, "--flat-playlist", "--print", "%(playlist_title)s", playlist_url],
            capture_output=True, text=True, check=True
        )
        return sanitize_filename(result.stdout.strip().splitlines()[0])
    except:
        return "Unknown_Playlist"

def download_playlist(playlist_url, cookies_path, output_dir):
    playlist_title = get_playlist_title(playlist_url, cookies_path)
    playlist_path = os.path.join(output_dir, playlist_title)
    os.makedirs(playlist_path, exist_ok=True)
    print(f"⬇️ Downloading playlist: {playlist_title}")
    command = [
        "yt-dlp",
        "--cookies", cookies_path,
        "-o", os.path.join(playlist_path, "%(title)s.%(ext)s"),
        playlist_url
    ]
    subprocess.run(command)

def main():
    parser = argparse.ArgumentParser(description="Download all playlists from a YouTube channel using yt-dlp and cookies.txt")
    parser.add_argument("url", help="YouTube channel URL")
    parser.add_argument("--cookies", default="cookies.txt", help="Path to cookies.txt file")
    args = parser.parse_args()

    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "project-mas")
    os.makedirs(output_dir, exist_ok=True)

    playlist_urls = extract_playlists(args.url, args.cookies)
    if not playlist_urls:
        print("No playlists found.")
        return

    print(f"✅ Found {len(playlist_urls)} playlists.")
    playlist_file = os.path.join(output_dir, "playlist_links.txt")
    with open(playlist_file, "w", encoding="utf-8") as f:
        for url in playlist_urls:
            f.write(url + "\n")

    for playlist_url in playlist_urls:
        download_playlist(playlist_url, args.cookies, output_dir)

if __name__ == "__main__":
    main()
