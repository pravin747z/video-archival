# YouTube Channel Recovery Tool

A Python script to recover YouTube playlists and videos using yt-dlp with cookie authentication for Azure VM compatibility.

## 🎯 Purpose

This tool helps recover YouTube channel content by downloading all videos from playlists while maintaining the original structure (playlist names as folders, original video titles as filenames).

## 📁 Project Structure

```
ch-767/
├── youtube_recovery.py     # Main recovery script
├── list.txt               # 149 playlist URLs (required)
├── cookies.txt            # YouTube cookies (required)
├── requirements.txt       # Python dependencies
├── download_log.txt       # Generated log file
├── README.md             # This file
└── downloads/            # Output folder (auto-created)
    ├── [Playlist Name 1]/
    │   ├── [Video Title 1].mp4
    │   ├── [Video Title 2].mp4
    │   └── ...
    ├── [Playlist Name 2]/
    └── ...
```

## ⚡ Quick Start

### Prerequisites

1. **Required Files**: Ensure these files exist in the same directory:
   - `list.txt` - Contains YouTube playlist URLs (one per line)
   - `cookies.txt` - YouTube authentication cookies

2. **Python Dependencies**: Install yt-dlp
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Tool

```powershell
python youtube_recovery.py
```

## 🔧 How It Works

### 1. Startup Validation
```
> python youtube_recovery.py
Checking required files...
✓ list.txt found (149 playlists)
✓ cookies.txt found
Starting YouTube Channel Recovery...
```

### 2. Processing Flow
```
Creating downloads/ directory...
Reading playlist URLs from list.txt...

[1/149] Processing: https://www.youtube.com/playlist?list=PLAkmEquH84Ds18DbF-XC_oGYqeP1HACIS
Getting playlist info...
Playlist: "Machine Learning Basics" (25 videos)
Creating folder: downloads/Machine Learning Basics/
Downloading videos... [████████████████████████████████████████] 100% (25/25)
✓ Playlist downloaded

[2/149] Processing: https://www.youtube.com/playlist?list=PLAkmEquH84Ds1rwe485z374Q8e2QAjVKD
Getting playlist info...
Playlist: "Python Tutorial Series" (15 videos)
Creating folder: downloads/Python Tutorial Series/
Downloading videos... [██████████████████████████] 67% (10/15)
```

### 3. Final Summary
```
YouTube Channel Recovery Complete!
Successfully downloaded: 145/149 playlists
Failed playlists: 4
Failed playlists logged to: download_log.txt
```

## 🛡️ Features

- **File Validation**: Automatically checks for required files
- **Progress Tracking**: Real-time progress with playlist and video counts
- **Timeout Protection**: Auto-terminates stuck downloads after 20 minutes
- **Error Handling**: Graceful handling of failed downloads
- **Simple Logging**: Basic status logging for each playlist
- **Azure VM Compatible**: Uses cookies to bypass YouTube's Azure VM blocking
- **Best Quality**: Downloads highest available video quality
- **Original Structure**: Preserves exact playlist names and video titles

## 🚨 Important Notes

### Azure VM Compatibility
- **Critical**: The `cookies.txt` file is essential for Azure VM environments
- YouTube blocks most Azure VM requests by default
- All operations require valid authentication cookies

### File Requirements
- Script will **immediately cancel** if either `list.txt` or `cookies.txt` is missing
- No virtual environment needed - keep it simple

### Download Behavior
- Downloads best available quality
- Creates folders with exact playlist names
- Uses original video titles as filenames
- Skips already downloaded videos (no overwrites)
- Continues interrupted downloads

## 📝 Log File

The script generates `download_log.txt` with simple status tracking:

```
=== YouTube Recovery Log ===
Date: 2025-06-30 14:30:15

✓ Playlist downloaded - Machine Learning Basics
✓ Playlist downloaded - Python Tutorial Series  
✗ Playlist was not able to download - Advanced Algorithms
✓ Playlist downloaded - Web Development Course

Summary:
Total playlists: 149
Successfully downloaded: 145
Failed: 4
```

## 🔧 Troubleshooting

### Common Issues

1. **Missing Files Error**
   ```
   ✗ list.txt not found!
   ERROR: Required files missing.
   ```
   **Solution**: Ensure `list.txt` and `cookies.txt` are in the same directory as the script

2. **Timeout Issues**
   ```
   ⚠️  Playlist download timeout (20+ minutes) - Terminating and skipping...
   ```
   **Solution**: Large playlists may timeout. Check your internet connection and retry

3. **Cookie Issues**
   ```
   Error: HTTP Error 403: Forbidden
   ```
   **Solution**: Update your `cookies.txt` file with fresh YouTube cookies

## 💡 Tips

- **Storage**: Expect ~200GB for all 149 playlists
- **Bandwidth**: Azure VM 4GB bandwidth recommended
- **Runtime**: Full recovery may take several hours
- **Monitoring**: Watch terminal output for real-time progress
- **Resuming**: Script can be safely restarted (skips existing downloads)

## 🎬 Expected Output Structure

```
downloads/
├── Machine Learning Fundamentals/
│   ├── Introduction to Neural Networks.mp4
│   ├── Deep Learning Basics.mp4
│   └── ...
├── Python Programming Course/
│   ├── Python Basics - Variables and Data Types.mp4
│   ├── Control Structures in Python.mp4
│   └── ...
└── Web Development Bootcamp/
    ├── HTML5 Essentials.mp4
    ├── CSS3 Advanced Techniques.mp4
    └── ...
```

---

**Note**: This tool is designed specifically for recovering lost YouTube channel content with proper authentication. Always respect YouTube's Terms of Service and content creators' rights.
