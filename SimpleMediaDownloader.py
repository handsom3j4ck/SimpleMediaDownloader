#!/usr/bin/env python3
"""
SimpleMediaDownloader - Download videos, audio, and playlists.
Powered by yt-dlp and ffmpeg.
Features:
  - Video with Audio
  - Audio only
  - Video without Audio
  - Supports single, multiple, and playlists
  - Cross-platform (Linux/Windows)
"""

import os
import sys
import re
import shutil
import concurrent.futures
from collections import defaultdict

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed. Run: pip install yt-dlp")
    sys.exit(1)

# =============================
# Global Configuration
# =============================

# Default number of concurrent download threads
MAX_WORKERS = 5

# Track failed downloads during session: [(url, desc, error)]
FAILED_DOWNLOADS = []

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
    [1] Video with Audio (Single or Multiple)
    [2] Audio Only (Single or Multiple)
    [3] Video without Audio (Single or Multiple)
    [4] Video with Audio (Playlist Mode)
    [5] Audio Only (Playlist Mode)
    [6] Video without Audio (Playlist Mode)
    [7] Resume Failed Downloads
    [8] Download-Thread Settings
    [9] Help
    [10] Exit
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
- [1] & [4]: Download video with audio (mp4)
- [2] & [5]: Audio-only (no video saved)
- [3] & [6]: Video without audio (no audio track)
- Thread Settings: Adjust [8] to control how many videos download at once
- Failed downloads are tracked and can be retried via [7]
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
# Resume Failed Downloads
# =============================

def resume_failed_downloads():
    global FAILED_DOWNLOADS
    clear_and_banner()
    print("=== Resume Failed Downloads ===\n")

    if not FAILED_DOWNLOADS:
        print("No failed downloads to resume.")
        quit_prompt()
        return

    print("Failed downloads:")
    print("-" * 80)
    for i, (url, desc, error) in enumerate(FAILED_DOWNLOADS, start=1):
        print(f"[{i}] {desc}")
        print(f"    URL: {url}")
        print(f"    Reason: {error}")
        print()

    print("-" * 80)
    print("Options:")
    print("  - Retry all ............... [A]")
    print("  - Retry specific by number  [1, 2, ...]")
    print("  - Cancel .................. [C]")

    choice = input("\nChoose action: ").strip().lower()

    if choice == 'c':
        print("Cancelled.")
        quit_prompt()
        return
    elif choice == 'a':
        # Retry all, grouped by desc
        failed_by_desc = defaultdict(list)
        for url, d, err in FAILED_DOWNLOADS:
            failed_by_desc[d].append(url)
        FAILED_DOWNLOADS = []  # Clear before retry; failures will be re-added if they fail again
        for desc, urls in failed_by_desc.items():
            print(f"\nRetrying {len(urls)} failed downloads for {desc}...")
            _retry_downloads(urls, desc)
    elif ',' in choice:
        # Retry multiple specific
        idxs = [int(i.strip()) - 1 for i in choice.split(',') if i.strip().isdigit()]
        to_retry = []
        for idx in sorted(idxs, reverse=True):  # Pop in reverse to avoid index shifts
            if 0 <= idx < len(FAILED_DOWNLOADS):
                to_retry.append(FAILED_DOWNLOADS.pop(idx))
        for url, desc, _ in reversed(to_retry):  # Retry in original order
            print(f"\nRetrying: {url}")
            _retry_downloads([url], desc)
    elif choice.isdigit():
        # Retry single specific
        idx = int(choice) - 1
        if 0 <= idx < len(FAILED_DOWNLOADS):
            url, desc, _ = FAILED_DOWNLOADS.pop(idx)
            print(f"\nRetrying: {url}")
            _retry_downloads([url], desc)
        else:
            print("Invalid number.")
    else:
        print("Invalid choice.")

    quit_prompt()

def _retry_downloads(urls, mode):
    """Internal helper to retry downloads based on mode."""
    output_dir = get_output_dir()
    ydl_opts = base_ydl_opts(output_dir)
    is_playlist = "Playlist" in mode
    if is_playlist:
        playlist_dir = os.path.join(output_dir, "%(playlist_title)s")
        ydl_opts['outtmpl'] = os.path.join(playlist_dir, "%(title)s [%(id)s].%(ext)s")
        ydl_opts['noplaylist'] = False
    else:
        ydl_opts['noplaylist'] = True
    if "Video with Audio" in mode:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio',
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                },
                {
                    'key': 'FFmpegMetadata',
                }
            ],
        })
    elif "Audio" in mode:
        ydl_opts.update({
            'format': 'bestaudio/best',
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
    elif "Video without Audio" in mode:
        ydl_opts.update({
            'format': 'bestvideo',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        })
    run_download_with_log(ydl_opts, urls, mode)

# =============================
# yt-dlp Options Templates
# =============================

def base_ydl_opts(output_dir):
    """Base options with retries and safety."""
    return {
        'retries': 5,
        'fragment_retries': 10,
        'continuedl': True,
        'nooverwrites': True,
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s].%(ext)s'),
        'writethumbnail': False,
        'quiet': False,
        'verbose': False,
    }

# =============================
# Shared Download Functions
# =============================

def download_single(ydl_opts, url, desc):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"[✓] {desc} succeeded: {url}")
        return None
    except Exception as e:
        err_msg = str(e).split('\n')[0]
        print(f"[✗] {desc} failed: {url} - {err_msg}")
        return (url, desc, err_msg)

def run_download(ydl_opts, urls, desc="Downloading"):
    """Generic download function with error handling and failure logging."""
    global FAILED_DOWNLOADS
    failed = []
    if not urls:
        return
    if len(urls) > 1:
        # Concurrent downloads for multiple URLs
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(download_single, ydl_opts.copy(), url, desc): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result = future.result()
                    if result:
                        failed.append(result)
                except Exception as exc:
                    url = future_to_url[future]
                    err_msg = str(exc).split('\n')[0]
                    print(f"[✗] {desc} failed: {url} ({err_msg})")
                    failed.append((url, desc, err_msg))
    else:
        # Single URL
        result = download_single(ydl_opts, urls[0], desc)
        if result:
            failed.append(result)
    if failed:
        FAILED_DOWNLOADS.extend(failed)
        print(f"\n❌ {len(failed)}/{len(urls)} download(s) failed. Use [7] to retry.")

def run_download_with_log(ydl_opts, urls, desc):
    """Wrapper that logs failures (used by retry)."""
    run_download(ydl_opts, urls, desc)

# =============================
# Download Functions (Optimized)
# =============================

def download_video_with_audio():
    clear_and_banner()
    print("=== Video with Audio (Single or Multiple) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    ydl_opts = base_ydl_opts(output_dir)
    ydl_opts.update({
        'noplaylist': True,
        'format': 'bestvideo+bestaudio',
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(ydl_opts, urls, "Video with Audio")
    print("\n✅ Video with audio download(s) completed (MP4)!")
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
        'noplaylist': True,
        'format': 'bestaudio/best',
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

    run_download(ydl_opts, urls, "Audio")
    print("\n✅ Audio extraction(s) completed (MP3, best quality).")
    quit_prompt()

def download_video_only_single():
    clear_and_banner()
    print("=== Video without Audio (Single or Multiple) ===\n")
    urls = get_urls(multiple=True)
    if not urls:
        print("No valid URLs provided.")
        quit_prompt()
        return

    output_dir = get_output_dir()

    ydl_opts = base_ydl_opts(output_dir)
    ydl_opts.update({
        'noplaylist': True,
        'format': 'bestvideo',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    })

    run_download(ydl_opts, urls, "Video without Audio")
    print("\n✅ Video without audio download(s) completed.")
    quit_prompt()

def download_video_with_audio_playlist():
    clear_and_banner()
    print("=== Video with Audio (Playlist Mode) ===\n")
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
        'noplaylist': False,
        'format': 'bestvideo+bestaudio',
        'outtmpl': full_path,
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    run_download(ydl_opts, [url], "Playlist Video with Audio")
    print("\n✅ Playlist: Videos with audio downloaded!")
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
        'noplaylist': False,
        'format': 'bestaudio/best',
        'outtmpl': full_path,
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

    run_download(ydl_opts, [url], "Playlist Audio")
    print("\n✅ Playlist audio download completed.")
    quit_prompt()

def download_video_only_playlist():
    clear_and_banner()
    print("=== Video without Audio (Playlist Mode) ===\n")
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
        'noplaylist': False,
        'format': 'bestvideo',
        'outtmpl': full_path,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    })

    run_download(ydl_opts, [url], "Playlist Video without Audio")
    print("\n✅ Playlist video without audio download completed.")
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
            resume_failed_downloads()
        elif choice == 8:
            download_thread_settings()
        elif choice == 9:
            show_help()
        elif choice == 10:
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
