"""Background worker threads for yt-dlp operations."""

import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal

import yt_dlp

from .models import FormatInfo


class InfoWorker(QThread):
    """Fetches video/playlist metadata in the background."""

    info_ready = pyqtSignal(dict)
    formats_ready = pyqtSignal(list)  # list of FormatInfo
    thumbnail_ready = pyqtSignal(bytes)
    error = pyqtSignal(str)

    def __init__(self, url: str, cookie_browser: str = ""):
        super().__init__()
        self.url = url
        self.cookie_browser = cookie_browser

    def run(self):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": "in_playlist",
            }
            if self.cookie_browser:
                opts["cookiesfrombrowser"] = (self.cookie_browser,)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                sanitized = ydl.sanitize_info(info)
                self.info_ready.emit(sanitized)

                # Parse available formats into FormatInfo objects
                raw_formats = sanitized.get("formats", [])
                formats = []
                for f in raw_formats:
                    fi = FormatInfo(
                        format_id=str(f.get("format_id", "")),
                        ext=f.get("ext", ""),
                        resolution=f.get("resolution", "audio only")
                        if f.get("resolution")
                        else f"{f.get('width', '?')}x{f.get('height', '?')}"
                        if f.get("width")
                        else "audio only",
                        fps=f.get("fps"),
                        vcodec=f.get("vcodec", "none") or "none",
                        acodec=f.get("acodec", "none") or "none",
                        filesize=f.get("filesize") or f.get("filesize_approx"),
                        tbr=f.get("tbr"),
                        note=f.get("format_note", ""),
                    )
                    formats.append(fi)
                if formats:
                    self.formats_ready.emit(formats)

                # Try to fetch thumbnail
                thumb_url = sanitized.get("thumbnail", "")
                if not thumb_url:
                    thumbnails = sanitized.get("thumbnails", [])
                    if thumbnails:
                        thumb_url = thumbnails[-1].get("url", "")
                    elif sanitized.get("entries"):
                        first = sanitized["entries"][0]
                        thumb_url = (
                            first.get("thumbnail", "")
                            or (
                                first.get("thumbnails", [{}])[-1].get("url", "")
                                if first.get("thumbnails")
                                else ""
                            )
                        )

                if thumb_url:
                    req = urllib.request.Request(
                        thumb_url,
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        self.thumbnail_ready.emit(resp.read())

        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    """Downloads a video/playlist in the background with progress reporting."""

    progress = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, url: str, ydl_opts: dict):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        self._cancelled = False

    def cancel(self):
        """Request cancellation of the download."""
        self._cancelled = True

    def _progress_hook(self, d: dict):
        if self._cancelled:
            raise yt_dlp.utils.DownloadCancelled()

        status = d.get("status", "")

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total > 0 else 0

            info = d.get("info_dict", {})
            playlist_index = info.get("playlist_autonumber") or info.get(
                "playlist_index"
            )
            playlist_count = info.get("n_entries") or info.get("playlist_count")

            self.progress.emit(
                {
                    "status": "downloading",
                    "percent": percent,
                    "speed": d.get("_speed_str", "N/A").strip(),
                    "eta": d.get("_eta_str", "N/A").strip(),
                    "total": d.get("_total_bytes_str", "").strip(),
                    "downloaded": d.get("_downloaded_bytes_str", "").strip(),
                    "playlist_index": playlist_index,
                    "playlist_count": playlist_count,
                    "video_title": info.get("title", ""),
                }
            )

        elif status == "finished":
            self.progress.emit(
                {
                    "status": "processing",
                    "filename": d.get("filename", ""),
                }
            )

    def _postprocessor_hook(self, d: dict):
        if d["status"] == "started":
            self.status_update.emit("Post-processing...")
        elif d["status"] == "finished":
            self.status_update.emit("Done")

    def run(self):
        try:
            self.ydl_opts["progress_hooks"] = [self._progress_hook]
            self.ydl_opts["postprocessor_hooks"] = [self._postprocessor_hook]

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])

            if not self._cancelled:
                self.finished.emit()

        except yt_dlp.utils.DownloadCancelled:
            self.error.emit("Cancelled")
        except Exception as e:
            if self._cancelled:
                self.error.emit("Cancelled")
            else:
                self.error.emit(str(e))
