#!/usr/bin/env python3
"""
YouTube Channel Recovery Tool
Recovers YouTube playlists and videos using yt-dlp with cookies for Azure VM compatibility
"""

import os
import sys
import subprocess
import time
import json
import re
from datetime import datetime
from pathlib import Path

class YouTubeRecovery:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.list_file = self.script_dir / "list.txt"
        self.cookies_file = self.script_dir / "cookies.txt"
        self.downloads_dir = self.script_dir / "downloads"
        self.log_file = self.script_dir / "download_log.txt"
        self.failed_playlists = []
        self.success_count = 0
        self.total_playlists = 0
        
    def check_required_files(self):
        """Check if required files exist"""
        print("Checking required files...")
        
        if not self.list_file.exists():
            print("✗ list.txt not found!")
            print("ERROR: Required files missing. Please ensure list.txt and cookies.txt are in the same directory.")
            print("Operation cancelled.")
            sys.exit(1)
            
        if not self.cookies_file.exists():
            print("✗ cookies.txt not found!")
            print("ERROR: Required files missing. Please ensure list.txt and cookies.txt are in the same directory.")
            print("Operation cancelled.")
            sys.exit(1)
            
        # Count playlists
        with open(self.list_file, 'r', encoding='utf-8') as f:
            self.total_playlists = len([line.strip() for line in f if line.strip()])
            
        print(f"✓ list.txt found ({self.total_playlists} playlists)")
        print("✓ cookies.txt found")
        print("Starting YouTube Channel Recovery...")
        
    def create_downloads_directory(self):
        """Create downloads directory if it doesn't exist"""
        print("\nCreating downloads/ directory...")
        self.downloads_dir.mkdir(exist_ok=True)
        
    def sanitize_filename(self, filename):
        """Remove invalid characters for file/folder names"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        # Remove extra spaces and dots
        filename = re.sub(r'\s+', ' ', filename).strip('. ')
        return filename
        
    def get_playlist_info(self, playlist_url):
        """Get playlist title and video count using yt-dlp"""
        try:
            cmd = [
                'yt-dlp',
                '--cookies', str(self.cookies_file),
                '--dump-json',
                '--flat-playlist',
                playlist_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    # Get playlist title from first video's uploader or playlist title
                    first_line = json.loads(lines[0])
                    playlist_title = first_line.get('playlist_title', 'Unknown Playlist')
                    video_count = len(lines)
                    return playlist_title, video_count
                    
            return None, 0
            
        except Exception as e:
            print(f"Error getting playlist info: {e}")
            return None, 0
            
    def download_playlist(self, playlist_url, playlist_name, video_count):
        """Download a single playlist using yt-dlp with advanced fault tolerance"""
        try:
            # Sanitize playlist name for folder
            safe_playlist_name = self.sanitize_filename(playlist_name)
            playlist_folder = self.downloads_dir / safe_playlist_name
            
            print(f"Creating folder: downloads/{safe_playlist_name}/")
            playlist_folder.mkdir(exist_ok=True)
            
            # yt-dlp command optimized for MAXIMUM video quality with enhanced error handling
            cmd = [
                'yt-dlp',
                '-v',
                '--cookies', str(self.cookies_file),
                '--format', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                '--output', str(playlist_folder / '%(title)s.%(ext)s'),
                '--no-overwrites',
                '--continue',
                '--ignore-errors',  # Skip individual video errors, continue with playlist
                '--no-abort-on-error',  # Don't abort entire playlist on single video failure
                '--merge-output-format', 'mp4',
                '--socket-timeout', '30',  # Individual video timeout
                '--retries', '3',  # Retry failed videos 3 times
                '--fragment-retries', '5',  # Retry failed fragments
                playlist_url
            ]
            
            print(f"Downloading videos (45min timeout)... ", end='', flush=True)
            
            # Run with extended timeout (45 minutes = 2700 seconds)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2700)
            
            # Check if at least some videos were downloaded successfully
            downloaded_files = list(playlist_folder.glob('*.mp4'))
            
            if len(downloaded_files) > 0:
                success_rate = (len(downloaded_files) / video_count) * 100 if video_count > 0 else 0
                print(f"[████████████████████████████████████████] {success_rate:.1f}% ({len(downloaded_files)}/{video_count})")
                
                # Log any skipped videos for transparency
                if len(downloaded_files) < video_count:
                    skipped_count = video_count - len(downloaded_files)
                    print(f"⚠️  {skipped_count} videos skipped due to individual errors")
                
                return True
            else:
                print("[✗] No videos downloaded")
                if result.stderr:
                    print(f"Error details: {result.stderr[:200]}...")  # Truncate long errors
                return False
                
        except subprocess.TimeoutExpired:
            print("[✗] Timeout (>45 minutes)")
            print("⚠️  Playlist download timeout (45+ minutes) - Checking partial success...")
            
            # Even on timeout, check if some videos were downloaded
            downloaded_files = list(playlist_folder.glob('*.mp4'))
            if len(downloaded_files) > 0:
                print(f"✓ Partial success: {len(downloaded_files)} videos downloaded before timeout")
                return True
            return False
            
        except Exception as e:
            print(f"[✗] Error: {e}")
            return False
            
    def log_result(self, playlist_name, success, url="", additional_info=""):
        """Log the result of playlist download with enhanced details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✓ Playlist downloaded" if success else "✗ Playlist was not able to download"
        
        # Write to log file with additional details
        with open(self.log_file, 'a', encoding='utf-8') as f:
            log_entry = f"{status} - {playlist_name}"
            if additional_info:
                log_entry += f" ({additional_info})"
            f.write(f"{log_entry}\n")
            
        if success:
            self.success_count += 1
        else:
            self.failed_playlists.append({"name": playlist_name, "url": url})
            
    def process_playlists(self):
        """Process all playlists from list.txt"""
        print("Reading playlist URLs from list.txt...\n")
        
        # Initialize log file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=== YouTube Recovery Log ===\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
        with open(self.list_file, 'r', encoding='utf-8') as f:
            playlist_urls = [line.strip() for line in f if line.strip()]
            
        for i, playlist_url in enumerate(playlist_urls, 1):
            print(f"[{i}/{self.total_playlists}] Processing: {playlist_url}")
            
            # Get playlist info
            print("Getting playlist info...")
            playlist_name, video_count = self.get_playlist_info(playlist_url)
            
            if playlist_name:
                print(f'Playlist: "{playlist_name}" ({video_count} videos)')
                
                # Download playlist with advanced error handling
                success = self.download_playlist(playlist_url, playlist_name, video_count)
                
                # Get actual download statistics for logging
                if success:
                    safe_playlist_name = self.sanitize_filename(playlist_name)
                    playlist_folder = self.downloads_dir / safe_playlist_name
                    downloaded_files = list(playlist_folder.glob('*.mp4')) if playlist_folder.exists() else []
                    actual_count = len(downloaded_files)
                    
                    if actual_count == video_count:
                        status_msg = "✓ Playlist downloaded (100% complete)"
                        log_info = f"{actual_count}/{video_count} videos"
                    else:
                        status_msg = f"✓ Playlist downloaded ({actual_count}/{video_count} videos)"
                        log_info = f"{actual_count}/{video_count} videos, {video_count - actual_count} skipped"
                else:
                    status_msg = "✗ Playlist was not able to download"
                    log_info = "complete failure"
                
                print(status_msg)
                self.log_result(playlist_name, success, playlist_url, log_info)
                
            else:
                print("✗ Could not get playlist info")
                self.log_result("Unknown Playlist", False, playlist_url)
                
            print()  # Empty line for readability
            
    def print_summary(self):
        """Print final summary"""
        failed_count = len(self.failed_playlists)
        
        print("="*50)
        print("YouTube Channel Recovery Complete!")
        print(f"Successfully downloaded: {self.success_count}/{self.total_playlists} playlists")
        print(f"Failed playlists: {failed_count}")
        
        # Add summary to log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nSummary:\n")
            f.write(f"Total playlists: {self.total_playlists}\n")
            f.write(f"Successfully downloaded: {self.success_count}\n")
            f.write(f"Failed: {failed_count}\n")
            
        if failed_count > 0:
            print(f"\nFailed playlists logged to: {self.log_file}")
            
    def run(self):
        """Main execution function"""
        try:
            self.check_required_files()
            self.create_downloads_directory()
            self.process_playlists()
            self.print_summary()
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    recovery = YouTubeRecovery()
    recovery.run()
