# YT-DLP GUI

A modern, cross-platform desktop GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp) built with PyQt6.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

### Core
- **Single Video & Playlist Download** — Paste any supported URL and download in your preferred format
- **Format Selection** — Choose video+audio or audio-only extraction
- **Quality Selection** — Best, 4K, 1080p, 720p, 480p, 360p, or worst quality
- **Audio Extraction** — MP3, M4A, OPUS, FLAC, or WAV with bitrate control
- **Download Queue** — Queue multiple downloads with progress tracking
- **Download History** — Persistent history with quick folder access

### Advanced
- **Concurrent Downloads** — Up to 3 simultaneous downloads (configurable)
- **Drag & Drop** — Drop URLs directly onto the window
- **Batch Import** — Import multiple URLs at once from text or a file
- **Format Browser** — Browse and select from all available formats in a table
- **Subtitle Download** — Download and embed subtitles with language selection
- **SponsorBlock** — Auto-remove sponsor segments, intros, outros
- **Speed Limit** — Throttle download speed (500 KB/s to 10 MB/s)
- **Cookie Import** — Import cookies from Chrome, Firefox, Edge, Safari, and more
- **Custom Filename Templates** — Use yt-dlp template syntax for output filenames
- **System Tray** — Tray icon with completion notifications and quick show/quit actions
- **Light / Dark Theme** — Toggle between dark and light themes (persisted)

### Packaging
- **PyInstaller Build Script** — Build standalone executables for any OS

## Requirements

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (required for audio extraction, video merging, and subtitle embedding)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jeetjawale/ytdlp_gui.git
   cd ytdlp_gui
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (if not already installed):
   - **Linux:** `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo pacman -S ffmpeg` (Arch)
   - **macOS:** `brew install ffmpeg`
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Usage

```bash
python main.py
```

### Workflow

1. **Paste a URL** into the input field, drag & drop, or use batch import
2. **Click "Fetch Info"** to retrieve video/playlist metadata
3. **Browse Formats** (optional) to manually pick a specific format
4. **Configure options** — quality, subtitles, SponsorBlock, speed limit, filename template
5. **Click "Add to Queue"** to start downloading
6. **Monitor progress** in the Downloads tab (up to 3 concurrent)
7. **View history** in the History tab
8. **Use the tray icon** for quick show/hide and completion notifications

### Web Application Mode

The project now includes a lightweight Flask web application that can be deployed as a web service.

**Local Testing:**
```bash
# Start the Flask development server
python app.py
```
The app will bind to `0.0.0.0:8080`. You can test the endpoints:
- `http://localhost:8080/health`
- `http://localhost:8080/download-info?url=https://www.youtube.com/watch?v=...`

**Render Deployment:**
The provided `Dockerfile` is pre-configured for Render.
1. Create a new **Web Service** on Render.
2. Connect your repository.
3. Select **Docker** as the runtime environment.
4. Render will automatically expose the application on the provided `$PORT`.

### Building Standalone Executables

```bash
# Install PyInstaller
pip install pyinstaller

# Build (one-dir, recommended)
python build.py

# Build single-file executable
python build.py --onefile

# Output in dist/YT-DLP-GUI/
```

## Project Structure

```
ytdlp_gui/
├── main.py              # Application entry point
├── build.py             # PyInstaller build script
├── requirements.txt     # Python dependencies
├── README.md
├── src/                 # Application source code
│   ├── main_window.py   # Main window — orchestration, tray, drag & drop
│   ├── widgets.py       # Custom widgets (format panel, advanced settings, dialogs)
│   ├── workers.py       # Background threads (info fetch, format parsing, download)
│   ├── models.py        # Data models (DownloadItem, FormatInfo, DownloadStatus)
│   ├── settings.py      # JSON-backed settings persistence
│   ├── styles.py        # QSS dark + light theme stylesheets
│   ├── download_options.py # yt-dlp option building
│   ├── error_utils.py   # Error classification utilities
│   └── history_service.py  # Download history management
└── tests/               # Unit and integration tests
```

## Supported Sites

Any site supported by yt-dlp (1000+ sites). See the full list:  
https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## License

MIT
