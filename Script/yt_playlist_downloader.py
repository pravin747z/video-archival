import os
import subprocess
import argparse

def download_youtube_content(url, cookies_path="cookies.txt"):
    # Ensure yt-dlp is available
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("yt-dlp is not installed or not found in PATH.")
        return

    # Create base output directory
    base_dir = os.path.join(os.getcwd(), "project-mas")
    os.makedirs(base_dir, exist_ok=True)

    # Use yt-dlp to extract playlist or channel metadata
    print("Fetching playlist metadata...")
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_path, "--flat-playlist", "--print", "%(playlist_title)s", url],
            capture_output=True, text=True, check=True
        )
        playlist_title = result.stdout.strip().splitlines()[0]
    except subprocess.CalledProcessError:
        print("Failed to fetch playlist metadata.")
        return

    # Sanitize folder name
    safe_title = "".join(c for c in playlist_title if c.isalnum() or c in " _-").rstrip()
    playlist_dir = os.path.join(base_dir, safe_title)
    os.makedirs(playlist_dir, exist_ok=True)

    # Construct yt-dlp command
    output_template = os.path.join(playlist_dir, "%(title)s.%(ext)s")
    command = [
        "yt-dlp",
        "--cookies", cookies_path,
        "-o", output_template,
        url
    ]

    print(f"Downloading videos to: {playlist_dir}")
    subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube playlist or channel videos using yt-dlp and cookies.")
    parser.add_argument("url", help="YouTube playlist or channel URL")
    parser.add_argument("--cookies", default="cookies.txt", help="Path to cookies.txt file (default: cookies.txt)")
    args = parser.parse_args()

    download_youtube_content(args.url, args.cookies)
