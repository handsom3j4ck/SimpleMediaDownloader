# SimpleMediaDownloader

- Powered by yt-dlp and ffmpeg. 
- Features:   - Video + Audio (extract MP3)   - Audio only   - Video only   - Supports single, multiple, and playlists
- Cross-platform (Linux/Windows)

## Features

- Download video + audio (extracts MP3)
- Download audio only (MP3, best quality)
- Download video only (no MP3 extraction)
- Supports single URLs, multiple URLs, and playlists
- Cross-platform: Works on Linux, macOS, and Windows
- Saves to the user's Downloads folder by default or a custom directory
- Progress tracking with retries for unstable connections
- Powered by `yt-dlp` for broad website support (YouTube, Vimeo, Dailymotion, and 1000+ more)

## Prerequisites

- **Python 3.6+**: Ensure Python is installed on your system.
- **yt-dlp**: A powerful tool for downloading media from various websites.
- **ffmpeg**: Required for audio extraction and video merging.

### Installation on Linux

Use your package manager to install dependencies.

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3 yt-dlp ffmpeg
```

#### Arch Linux

```bash
sudo pacman -S python yt-dlp ffmpeg
```

### Installation on Windows

1. **Install Python**:

   - Download and install Python 3 from python.org.
   - Ensure the "Add Python to PATH" option is checked during installation.

2. **Install yt-dlp**:

   - Open Command Prompt or PowerShell and run:

     ```bash
     pip install yt-dlp
     ```

3. **Install ffmpeg**:

   - Download the latest `ffmpeg` build from ffmpeg.org or a trusted source like gyan.dev.
   - Extract the downloaded archive to a folder (e.g., `C:\ffmpeg`).
   - Add `ffmpeg` to your system PATH:
     - Open the Start menu, search for "Edit the system environment variables," and open it.
     - Click "Environment Variables."
     - Under "System Variables," find and edit the `Path` variable.
     - Add the path to the `ffmpeg\bin` folder (e.g., `C:\ffmpeg\bin`).
     - Save and close all windows.
   - Verify installation by running `ffmpeg -version` in Command Prompt or PowerShell.

### Installation on macOS

```bash
brew install python yt-dlp ffmpeg
```

## Usage

1. Clone or download this repository:

   ```bash
   git clone https://github.com/yourusername/SimpleMediaDownloader.git
   cd SimpleMediaDownloader
   ```

2. Run the script:

   ```bash
   python3 SimpleMediaDownloader.py
   ```

3. Follow the on-screen menu:

   - Choose options 1–6 for downloading videos, audio, or playlists.
   - Option 7 for help.
   - Option 8 to exit.
   - Enter URLs when prompted (one per line for multiple URLs, press Enter twice to finish).
   - Specify a custom output directory or use the default (`~/Downloads`).

## Notes

- **Supported Sites**: YouTube, Vimeo, Dailymotion, and 1000+ more (via `yt-dlp`).
- **Playlists**: Use the full playlist URL (e.g., `youtube.com/playlist?list=...`).
- **Audio Quality**: MP3s are extracted with VBR (quality 0) for best results.
- **Retries**: The script retries failed downloads up to 5 times for unstable connections.
- **Interrupt**: Press `Ctrl+C` to cancel operations or exit the script.
- **Duplicate Downloads**: Skipped automatically to avoid overwrites.

## Troubleshooting

- Ensure `yt-dlp` and `ffmpeg` are installed and accessible in your PATH.
- Check URLs for validity (must start with `http://` or `https://`).
- If you encounter errors, run `pip install --upgrade yt-dlp` to update `yt-dlp`.
- For Windows, verify `ffmpeg` is added to PATH by running `ffmpeg -version`.
