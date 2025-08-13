# SimpleMediaDownloader 🎥🔊

A simple, user-friendly command-line tool to download videos, audio, and playlists from YouTube, Vimeo, Dailymotion, and over 1000+ sites — powered by [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) and `ffmpeg`.

---

## ✨ Features

- **Video with Audio Download**  
  Download the best quality video and audio, then merge into MP4.

- **Audio Only (MP3)**  
  Extract high-quality MP3s (VBR quality 0) directly — perfect for music or podcasts.

- **Video Only (No Audio Extraction)**  
  Download video without extracting audio .

- **Supports:**
  - ✅ Single URLs
  - ✅ Multiple URLs (paste one per line)
  - ✅ Playlists (YouTube, etc.)

- **Cross-Platform**  
  Works seamlessly on **Linux**, **Windows**, and **macOS**.

- **Smart Output Handling**
  - Saves to your system's `Downloads` folder by default.
  - Option to specify a custom directory.
  - Playlist downloads are saved in organized subfolders.

- **Robust & Resilient**
  - Retries failed downloads (up to 5 times).
  - Resume failed downloads later using the built-in retry system.
  - Progress tracking with real-time speed and ETA.
  - Skips duplicates automatically.

- **User-Friendly Menu**
  - Interactive terminal interface.
  - Thread settings to control concurrent downloads.
  - Help and error guidance built-in.

---

## ⚙️ Prerequisites

Before using this tool, ensure the following are installed:

- **Python 3.6 or higher**  
- **yt-dlp** — media downloading backend  
- **ffmpeg** — for audio extraction and video merging  

---

### 🐧 Linux (Debian/Ubuntu, Arch, etc.)

#### Debian/Ubuntu and derivatives

```bash
sudo apt update
sudo apt install python3 yt-dlp ffmpeg
```

#### Arch Linux and derivatives

```bash
sudo pacman -S python yt-dlp ffmpeg
```

> ✅ Both `yt-dlp` and `ffmpeg` are available in official repositories — no `pip` required!

---

### 💻 Windows

1. **Install Python 3**
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check **"Add Python to PATH"** during installation

2. **Install yt-dlp**
   Open **Command Prompt** or **PowerShell** and run:
   ```bash
   pip install yt-dlp
   ```

3. **Install ffmpeg**
   - Download a static build from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) or [https://gyan.dev/ffmpeg/builds/](https://gyan.dev/ffmpeg/builds/)
   - Extract the ZIP to a folder (e.g., `C:\ffmpeg`)
   - Add `C:\ffmpeg\bin` to your **system PATH**:
     - Press `Win + S`, search for "Environment Variables"
     - Click **"Edit the system environment variables"**
     - Click **"Environment Variables"**
     - Under **System Variables**, find `Path` → **Edit** → **New** → Add the path to `ffmpeg\bin`
   - Verify installation:
     ```cmd
     ffmpeg -version
     ```

---

### 🍏 macOS

Using [Homebrew](https://brew.sh/):

```bash
brew install python yt-dlp ffmpeg
```

> ✅ All dependencies in one command!

---

## 🚀 Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/handsom3j4ck/SimpleMediaDownloader.git
   cd SimpleMediaDownloader
   ```

2. **Make the script executable (Linux/macOS):**

   ```bash
   chmod +x SimpleMediaDownloader.py
   ```

3. **Run the script:**

   ```bash
   python SimpleMediaDownloader.py
   ```

   > On some systems, use `python3` instead of `python`.

4. **Follow the on-screen menu:**

   ```
   [1] Video + Audio Download (Single or Multiple)
   [2] Audio Download (Single or Multiple)
   [3] Video Only (Single or Multiple)
   [4] Video + Audio (Playlist Mode)
   [5] Audio Only (Playlist Mode)
   [6] Video Only (Playlist Mode)
   [7] Resume Failed Downloads
   [8] Download-Thread Settings
   [9] Help
   [10] Exit
   ```

   - Enter your choice (e.g., `1` for video+audio).
   - Paste one or more URLs (press Enter twice to finish).
   - Choose output directory (default: `~/Downloads` or `C:\Users\YourName\Downloads`).
   - Watch progress in real time.

---

## 🔁 Resume Failed Downloads

If any downloads fail due to network issues:

- Select **[7] Resume Failed Downloads** from the menu.
- Choose to retry **all** or a **specific** failed item.
- The script remembers failure reasons and allows targeted recovery.

---

## ⚙️ Thread Settings

- Use **[8] Download-Thread Settings** to adjust how many downloads can run concurrently.
- Default: **5** (recommended range: 1–10).
- Higher values may overload your connection or system.

---

## 📂 Output Structure

- **Single downloads:** Saved directly to your chosen directory.
- **Playlists:** Saved in a subfolder named after the playlist:
  ```
  Downloads/
  └── My Favorite Songs/
      ├── Song 1 [abc123].mp3
      ├── Song 2 [def456].mp3
      └── ...
  ```

- Filenames include video title and ID to avoid conflicts.

---

## 📌 Notes

- **Supported Sites:** Over 1000 platforms including YouTube, Vimeo, Dailymotion, Twitch clips, and more — thanks to `yt-dlp`.
- **Audio Quality:** MP3s are extracted using **VBR (Variable Bitrate) at quality 0** — near-lossless and high fidelity.
- **Duplicate Handling:** The script skips existing files to prevent overwrites.
- **Playlist URLs:** Use the full URL (e.g., `https://www.youtube.com/playlist?list=PL...`).
- **Cancel Anytime:** Press `Ctrl+C` to stop a download or exit the script safely.
- **FFmpeg Required:** Needed for MP3 extraction and video merging. Without it, audio-only and video+audio modes will fail.

---

## 🛠️ Troubleshooting

| Issue | Solution |
|------|----------|
| `Error: ffmpeg is not installed` | Install `ffmpeg` and ensure it's in your system `PATH`. Test with `ffmpeg -version`. |
| `yt-dlp: command not found` | Install via `pip install yt-dlp` or your system package manager. |
| Invalid URL error | Ensure URLs start with `http://` or `https://`. |
| Downloads failing repeatedly | Update `yt-dlp`: `pip install --upgrade yt-dlp` |
| Permission denied on save | Choose a different output directory or run with proper permissions. |
| Windows PATH issues | Re-run Python installer and check "Add to PATH", or manually add `ffmpeg\bin`. |

---

## 📦 Dependencies

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — MIT License  
- [`ffmpeg`](https://ffmpeg.org/) — LGPL/GPL  
- Python 3 standard library only (no other external PyPI packages required)

---

## 🙌 Acknowledgments

- Huge thanks to the `yt-dlp` team for maintaining an incredible media downloading tool.
- `ffmpeg` developers for enabling powerful audio/video processing.

---

> ✅ **SimpleMediaDownloader** — Simple, powerful, and reliable media downloading for everyone.
