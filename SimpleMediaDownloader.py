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
    print("""
    [1] Video + Audio Download (Single or Multiple)
    [2] Audio Download (Single or Multiple)
    [3] Video Only (Single or Multiple)
    [4] Video + Audio (Playlist Mode)
    [5] Audio Only (Playlist Mode)
    [6] Video Only (Playlist Mode)
    [7] Help
    [8] Exit
    """)

def is_valid_url(url):
    """Basic URL validation."""
    regex = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.match(regex, url) is not None

def get_urls(multiple=True):
    """Get one or more URLs from user."""
    if not multiple:
        url = input("Enter URL: ").strip()
        return [url] if url else []

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
    else:
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
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        sys.stdout.write(f"\rDownloading: {percent} at {speed} | ETA: {eta} ")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\nDownload completed.")

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
- [1] & [4]: Download best video AND extract MP3 automatically
- [2] & [5]: Audio-only (no video downloaded)
- [3] & [6]: Video-only (no MP3 extracted)
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
    }

# =============================
# Download Functions
# =============================

def download_video_with_audio():
    clear_and_banner()
    print("=== Video + Audio Extraction (Best of Both) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    try:
        import yt_dlp

        # Step 1: Download best video
        print("\n[1/2] Downloading best video (with audio)...")
        video_opts = base_ydl_opts(output_dir, merge_format='mp4')
        video_opts.update({
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s] - VIDEO.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        })
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download(urls)

        # Step 2: Extract best audio as MP3
        print("\n[2/2] Extracting best audio as MP3...")
        audio_opts = base_ydl_opts(output_dir)
        audio_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s] - AUDIO.%(ext)s'),
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
            'quiet': True,
        })
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download(urls)

        print("\nVideo saved and high-quality MP3 extracted!")
    except Exception as e:
        print(f"\nError: {e}")
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

    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
        print("\nAudio extraction(s) completed (MP3, best quality).")
    except Exception as e:
        print(f"\nError: {e}")
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

    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
        print("\nVideo download(s) completed (no audio extracted).")
    except Exception as e:
        print(f"\nError: {e}")
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
    video_path = os.path.join(playlist_dir, "%(title)s [%(id)s] - VIDEO.%(ext)s")
    audio_path = os.path.join(playlist_dir, "%(title)s [%(id)s] - AUDIO.%(ext)s")

    try:
        import yt_dlp

        # Step 1: Download best video for each in playlist
        print("\n[1/2] Downloading best video (merged) for each item...")
        video_opts = base_ydl_opts(output_dir)
        video_opts.update({
            'format': 'bestvideo+bestaudio',
            'outtmpl': video_path,
            'noplaylist': False,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        })
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        # Step 2: Extract best audio as MP3 for each
        print("\n[2/2] Extracting best audio as MP3 for each...")
        audio_opts = base_ydl_opts(output_dir)
        audio_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
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
            'quiet': True,
        })
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        print("\nPlaylist: Videos saved and MP3s extracted!")
    except Exception as e:
        print(f"\nError: {e}")
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

    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nPlaylist audio download completed.")
    except Exception as e:
        print(f"\nError: {e}")
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

    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nPlaylist video download completed (no audio extracted).")
    except Exception as e:
        print(f"\nError: {e}")
    quit_prompt()

# =============================
# Main Menu
# =============================

def select():
    try:
        choice = input("SimpleMediaDownloader~$ ").strip()
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
            show_help()
        elif choice == 8:
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid option. Try again.")
            quit_prompt()
    except (ValueError, KeyboardInterrupt):
        print("\nInvalid input. Exiting...")
        sys.exit(1)

# =============================
# Entry Point
# =============================

if __name__ == "__main__":
    try:
        clear_and_banner()
        show_menu()
        select()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
