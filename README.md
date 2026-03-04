# YT-DLP GUI

A modern, cross-platform desktop GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp) built with PyQt6.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

- **Single Video Download** — Paste any supported URL and download in your preferred format
- **Playlist Download** — Full playlist support with per-video progress tracking
- **Format Selection** — Choose between video+audio or audio-only extraction
- **Quality Selection** — Pick from Best, 4K, 1080p, 720p, 480p, 360p, or worst quality
- **Audio Extraction** — Extract audio as MP3, M4A, OPUS, FLAC, or WAV with bitrate control
- **Download Queue** — Queue multiple downloads; they process sequentially
- **Progress Tracking** — Real-time progress bar with speed, ETA, and file size
- **Download History** — Persistent history of completed downloads with quick folder access
- **Dark Theme** — Modern dark UI that's easy on the eyes

## Requirements

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (required for audio extraction and video merging)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
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

1. **Paste a URL** into the input field (or click the clipboard button)
2. **Click "Fetch Info"** to retrieve video/playlist metadata
3. **Select format options** — toggle audio-only, choose quality, set output directory
4. **Click "Add to Queue"** to start downloading
5. **Monitor progress** in the Downloads tab
6. **View history** in the History tab

## Project Structure

```
ytdlp_gui/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── README.md
└── src/
    ├── __init__.py
    ├── main_window.py   # Main window with all UI logic
    ├── widgets.py       # Custom Qt widgets (info card, format panel, queue, history)
    ├── workers.py       # Background threads (info fetch, download)
    ├── models.py        # Data models (DownloadItem, DownloadStatus)
    ├── settings.py      # JSON-backed settings persistence
    └── styles.py        # QSS dark theme stylesheet
```

## Supported Sites

Any site supported by yt-dlp (1000+ sites). See the full list:  
https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## License

MIT
