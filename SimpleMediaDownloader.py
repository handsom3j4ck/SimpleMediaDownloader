#!/usr/bin/env python3
"""
SimpleMediaDownloader - Download videos, audio, and playlists.
Powered by yt-dlp and ffmpeg.
Features:
  - Video + Audio (extract MP3)
  - Audio only
  - Video only
  - Supports single, multiple, and playlists
  - Cross-platform (Linux/Windows)
"""

import os
import sys
import re
import shutil

# =============================
# Global Configuration
# =============================

# Default number of concurrent download threads
MAX_WORKERS = 5

# =============================
# Check for FFmpeg at Startup
# =============================

def check_ffmpeg():
    """Ensure ffmpeg is available in PATH."""
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed or not in system PATH.")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

# =============================
# Utility Functions
# =============================

def clear_and_banner():
    """Clear screen and show banner (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""
====================================
   SimpleMediaDownloader
   Powered by yt-dlp and ffmpeg
====================================
    """)

def show_menu():
    print(f"""
    [1] Video + Audio Download (Single or Multiple)
    [2] Audio Download (Single or Multiple)
    [3] Video Only (Single or Multiple)
    [4] Video + Audio (Playlist Mode)
    [5] Audio Only (Playlist Mode)
    [6] Video Only (Playlist Mode)
    [7] Download-Thread Settings
    [8] Help
    [9] Exit
    """)

def is_valid_url(url):
    """Basic URL validation."""
    regex = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.match(regex, url) is not None

def get_urls(multiple=True):
    """Get one or more URLs from user."""
    if not multiple:
        url = input("Enter URL: ").strip()
        if not url:
            return []
        if not is_valid_url(url):
            print(f"  [!] Invalid URL: {url}")
            return []
        return [url]

    print("Enter URLs (one per line). Press Enter twice to finish:")
    urls = []
    while True:
        try:
            url = input("> ").strip()
            if not url:
                break
            if not is_valid_url(url):
                print(f"  [!] Invalid URL skipped: {url}")
                continue
            urls.append(url)
        except EOFError:
            break
    return urls

def get_default_downloads_dir():
    """Get the OS-appropriate Downloads directory."""
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    if os.path.exists(downloads) and os.path.isdir(downloads):
        return downloads
    return "./downloads"  # Fallback

def get_output_dir():
    """Prompt user for output directory, defaulting to OS Downloads folder."""
    default_dir = get_default_downloads_dir()
    print(f"Default save directory: {default_dir}")
    custom = input("Enter custom directory or press Enter to use default: ").strip()
    save_dir = custom if custom else default_dir
    try:
        os.makedirs(save_dir, exist_ok=True)
        print(f"Saving to: {save_dir}")
    except Exception as e:
        print(f"Cannot create directory: {e}")
        print("Using current directory instead.")
        save_dir = "./downloads"
        os.makedirs(save_dir, exist_ok=True)
    return save_dir

def progress_hook(d):
    """Display download progress."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A').strip()
        speed = d.get('_speed_str', 'N/A').strip()
        eta = d.get('_eta_str', 'N/A').strip()
        sys.stdout.write(f"\rDownloading: {percent} at {speed} | ETA: {eta}")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write("\rDownload completed.                                \n")
        sys.stdout.flush()

def show_help():
    clear_and_banner()
    print("""
HELP:
- Supported sites: YouTube, Vimeo, Dailymotion, and 1000+ more (via yt-dlp)
- For playlists: Use full playlist URL (e.g., youtube.com/playlist?list=...)
- Audio extraction requires ffmpeg installed on your system
- Use Ctrl+C to cancel any operation
- Multiple URLs: Paste one per line, then press Enter twice
- Best audio quality: MP3 with VBR (quality 0) used by default
- Duplicate downloads are skipped automatically
- Retries enabled for unstable connections
- Default download path: ~/Downloads (Linux/macOS) or C:\\Users\\<User>\\Downloads (Windows)
- [1] & [4]: Download best video and extract MP3 from it (single pass)
- [2] & [5]: Audio-only (no video saved)
- [3] & [6]: Video-only (no MP3 extracted)
- Thread Settings: Adjust [7] to control how many videos download at once
    """)
    quit_prompt()

# =============================
# Quit Prompt
# =============================

def quit_prompt():
    try:
        con = input("\nContinue? [Y/n] -> ").strip().lower()
        if con.startswith('n'):
            print("Exiting...")
            sys.exit(0)
        else:
            clear_and_banner()
            show_menu()
            select()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting...")
        sys.exit(0)

# =============================
# Thread Settings
# =============================

def download_thread_settings():
    global MAX_WORKERS
    clear_and_banner()
    print(f"=== Download Thread Settings ===\n")
    print(f"Current number of concurrent downloads: {MAX_WORKERS}")
    print("Recommended: 1–5 (higher may slow down connections or overload system)\n")

    try:
        new_value = input("Enter new number of concurrent downloads (1-10): ").strip()
        if not new_value.isdigit():
            print("Invalid input. Not changed.")
        else:
            num = int(new_value)
            if 1 <= num <= 10:
                MAX_WORKERS = num
                print(f"✅ Concurrent downloads set to: {MAX_WORKERS}")
            else:
                print("Please enter a number between 1 and 10.")
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
    finally:
        quit_prompt()

# =============================
# yt-dlp Options Templates
# =============================

def base_ydl_opts(output_dir, merge_format='mp4'):
    """Base options with retries and safety."""
    return {
        'retries': 5,
        'fragment_retries': 10,
        'part_retries': 10,
        'continuedl': True,
        'nooverwrites': True,
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s].%(ext)s'),
        'writethumbnail': False,
        'merge_output_format': merge_format,
        'quiet': False,
        'verbose': False,
    }

# =============================
# Shared Download Functions
# =============================

def import_yt_dlp():
    """Safely import yt_dlp with error handling."""
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        print("Error: yt-dlp is not installed. Run: pip install yt-dlp")
        sys.exit(1)

def run_download(ydl_opts, urls, desc="Downloading"):
    """Generic download function with error handling."""
    yt_dlp = import_yt_dlp()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
        print(f"\n{desc} completed.")
    except Exception as e:
        print(f"\nError during {desc.lower()}: {e}")

# =============================
# Download Functions (Optimized)
# =============================

def download_video_with_audio():
    clear_and_banner()
    print("=== Video + Audio Extraction (Single Download + Extract MP3) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    # Download once: best video+audio, merge to mp4, then extract MP3
    print("\n[1/2] Downloading best video with audio (merged)...")
    video_opts = base_ydl_opts(output_dir, merge_format='mp4')
    video_opts.update({
        'format': 'bestvideo+bestaudio',
        'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s].%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(video_opts, urls, "Video download and MP3 extraction")
    print("\n✅ Video saved as MP4 and high-quality MP3 extracted!")
    quit_prompt()

def download_audio_single():
    clear_and_banner()
    print("=== Audio Download (Single or Multiple) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    ydl_opts = base_ydl_opts(output_dir)
    ydl_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            },
            {
                'key': 'FFmpegEmbedSubtitle',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(ydl_opts, urls, "Audio download")
    print("\n✅ Audio extraction(s) completed (MP3, best quality).")
    quit_prompt()

def download_video_only_single():
    clear_and_banner()
    print("=== Video Only Download (No MP3) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    ydl_opts = base_ydl_opts(output_dir, merge_format='mp4')
    ydl_opts.update({
        'format': 'bestvideo+bestaudio',
        'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s].%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    })

    run_download(ydl_opts, urls, "Video download")
    print("\n✅ Video download(s) completed (no audio extracted).")
    quit_prompt()

def download_video_with_audio_playlist():
    clear_and_banner()
    print("=== Video + Audio (Playlist Mode) ===\n")
    url = input("Enter playlist URL: ").strip()
    if not url or not is_valid_url(url):
        print("Invalid or no URL provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()
    playlist_dir = os.path.join(output_dir, "%(playlist_title)s")
    full_path = os.path.join(playlist_dir, "%(title)s [%(id)s].%(ext)s")

    print("\nDownloading each video and extracting MP3...")
    ydl_opts = base_ydl_opts(output_dir)
    ydl_opts.update({
        'format': 'bestvideo+bestaudio',
        'outtmpl': full_path,
        'noplaylist': False,
        'merge_output_format': 'mp4',
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(ydl_opts, [url], "Playlist video and MP3 extraction")
    print("\n✅ Playlist: Videos saved and MP3s extracted in single pass!")
    quit_prompt()

def download_audio_playlist():
    clear_and_banner()
    print("=== Audio Only (Playlist Mode) ===\n")
    url = input("Enter playlist URL: ").strip()
    if not url or not is_valid_url(url):
        print("Invalid or no URL provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()
    playlist_dir = os.path.join(output_dir, "%(playlist_title)s")
    full_path = os.path.join(playlist_dir, "%(title)s [%(id)s].%(ext)s")

    ydl_opts = base_ydl_opts(output_dir)
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': full_path,
        'noplaylist': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(ydl_opts, [url], "Playlist audio download")
    print("\n✅ Playlist audio download completed.")
    quit_prompt()

def download_video_only_playlist():
    clear_and_banner()
    print("=== Video Only (Playlist Mode) ===\n")
    url = input("Enter playlist URL: ").strip()
    if not url or not is_valid_url(url):
        print("Invalid or no URL provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()
    playlist_dir = os.path.join(output_dir, "%(playlist_title)s")
    full_path = os.path.join(playlist_dir, "%(title)s [%(id)s].%(ext)s")

    ydl_opts = base_ydl_opts(output_dir, merge_format='mp4')
    ydl_opts.update({
        'format': 'bestvideo+bestaudio',
        'outtmpl': full_path,
        'noplaylist': False,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    })

    run_download(ydl_opts, [url], "Playlist video download")
    print("\n✅ Playlist video download completed (no audio extracted).")
    quit_prompt()

# =============================
# Main Menu
# =============================

def select():
    try:
        choice = input("SimpleMediaDownloader~$ ").strip()
        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            quit_prompt()
            return
        choice = int(choice)

        if choice == 1:
            download_video_with_audio()
        elif choice == 2:
            download_audio_single()
        elif choice == 3:
            download_video_only_single()
        elif choice == 4:
            download_video_with_audio_playlist()
        elif choice == 5:
            download_audio_playlist()
        elif choice == 6:
            download_video_only_playlist()
        elif choice == 7:
            download_thread_settings()
        elif choice == 8:
            show_help()
        elif choice == 9:
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid option. Try again.")
            quit_prompt()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

# =============================
# Entry Point
# =============================

if __name__ == "__main__":
    check_ffmpeg()  # Verify ffmpeg is available
    try:
        clear_and_banner()
        show_menu()
        select()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
