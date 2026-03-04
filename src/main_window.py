"""Main application window for the YT-DLP GUI."""

import os
import time
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .models import DownloadItem, DownloadStatus
from .settings import Settings
from .styles import DARK_THEME
from .widgets import (
    FormatPanel,
    HistoryPanel,
    QueuePanel,
    VideoInfoCard,
)
from .workers import DownloadWorker, InfoWorker


class MainWindow(QMainWindow):
    """Main application window with URL input, format options, queue, and history."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT-DLP GUI")
        self.setMinimumSize(820, 620)
        self.resize(960, 720)
        self.setStyleSheet(DARK_THEME)

        # ── State ──
        self.current_info: Optional[dict] = None
        self.download_queue: List[DownloadItem] = []
        self.active_worker: Optional[DownloadWorker] = None
        self.active_item: Optional[DownloadItem] = None
        self.info_worker: Optional[InfoWorker] = None
        self.settings = Settings()

        self._setup_ui()
        self._connect_signals()
        self._load_history()

    # ──────────────────────────────────
    # UI Setup
    # ──────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(18, 18, 18, 12)

        # ─── URL bar ───
        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText(
            "Paste a YouTube, Vimeo, or any supported URL here..."
        )

        self.paste_btn = QPushButton("\U0001f4cb")
        self.paste_btn.setToolTip("Paste from clipboard")
        self.paste_btn.setObjectName("pasteBtn")
        self.paste_btn.setFixedSize(42, 42)

        self.fetch_btn = QPushButton("\U0001f50d  Fetch Info")
        self.fetch_btn.setObjectName("fetchBtn")
        self.fetch_btn.setFixedWidth(130)
        self.fetch_btn.setFixedHeight(42)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.paste_btn)
        url_layout.addWidget(self.fetch_btn)
        main_layout.addLayout(url_layout)

        # ─── Video info card (hidden until fetch) ───
        self.info_card = VideoInfoCard()
        self.info_card.hide()
        main_layout.addWidget(self.info_card)

        # ─── Format options panel (hidden until fetch) ───
        default_dir = self.settings.get("output_dir", "")
        self.format_panel = FormatPanel(default_dir)
        self.format_panel.hide()
        main_layout.addWidget(self.format_panel)

        # ─── Add to Queue button (hidden until fetch) ───
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.add_queue_btn = QPushButton("\U0001f4e5  Add to Queue")
        self.add_queue_btn.setObjectName("addQueueBtn")
        self.add_queue_btn.setFixedWidth(170)
        self.add_queue_btn.setFixedHeight(40)
        self.add_queue_btn.hide()
        btn_layout.addWidget(self.add_queue_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ─── Tabs (Downloads / History) ───
        self.tabs = QTabWidget()
        self.queue_panel = QueuePanel()
        self.history_panel = HistoryPanel()
        self.tabs.addTab(self.queue_panel, "\U0001f4e5 Downloads (0)")
        self.tabs.addTab(self.history_panel, "\U0001f4cb History (0)")
        main_layout.addWidget(self.tabs, 1)

        # ─── Status bar ───
        self.statusBar().showMessage("Ready \u2014 Paste a URL to get started")

    # ──────────────────────────────────
    # Signal connections
    # ──────────────────────────────────

    def _connect_signals(self):
        self.fetch_btn.clicked.connect(self.fetch_info)
        self.paste_btn.clicked.connect(self._paste_url)
        self.url_input.returnPressed.connect(self.fetch_info)
        self.add_queue_btn.clicked.connect(self.add_to_queue)
        self.format_panel.browse_btn.clicked.connect(self._browse_output_dir)
        self.history_panel.history_cleared.connect(self._on_history_cleared)

    # ──────────────────────────────────
    # URL & Info Fetching
    # ──────────────────────────────────

    def _paste_url(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            if text:
                self.url_input.setText(text.strip())

    def _browse_output_dir(self):
        current = self.format_panel.output_dir.text()
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", current
        )
        if dir_path:
            self.format_panel.output_dir.setText(dir_path)
            self.settings.set("output_dir", dir_path)

    def fetch_info(self):
        """Fetch video/playlist metadata from the entered URL."""
        url = self.url_input.text().strip()
        if not url:
            self.statusBar().showMessage("Please enter a URL first")
            return

        # Disconnect any previous worker signals
        if self.info_worker is not None:
            try:
                self.info_worker.info_ready.disconnect()
                self.info_worker.thumbnail_ready.disconnect()
                self.info_worker.error.disconnect()
            except (TypeError, RuntimeError):
                pass

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("\u23f3  Fetching...")
        self.statusBar().showMessage(f"Fetching info for: {url}")

        # Hide previous results
        self.info_card.hide()
        self.format_panel.hide()
        self.add_queue_btn.hide()
        self.current_info = None

        self.info_worker = InfoWorker(url)
        self.info_worker.info_ready.connect(self._on_info_ready)
        self.info_worker.thumbnail_ready.connect(self._on_thumbnail_ready)
        self.info_worker.error.connect(self._on_info_error)
        self.info_worker.start()

    def _on_info_ready(self, info: dict):
        self.current_info = info
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("\U0001f50d  Fetch Info")

        is_playlist = info.get("_type") == "playlist"
        title = info.get("title", "Unknown")

        self.info_card.update_info(info)
        self.info_card.show()
        self.format_panel.show()
        self.add_queue_btn.show()

        if is_playlist:
            count = len(info.get("entries", []))
            self.statusBar().showMessage(
                f"Playlist: {title} ({count} video{'s' if count != 1 else ''})"
            )
        else:
            self.statusBar().showMessage(f"Video: {title}")

    def _on_thumbnail_ready(self, data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            self.info_card.set_thumbnail(pixmap)

    def _on_info_error(self, error: str):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("\U0001f50d  Fetch Info")
        self.statusBar().showMessage(f"Error: {error}")
        QMessageBox.warning(
            self, "Fetch Error",
            f"Failed to fetch video info:\n\n{error}",
        )

    # ──────────────────────────────────
    # Queue Management
    # ──────────────────────────────────

    def add_to_queue(self):
        """Create a DownloadItem from current info and add it to the queue."""
        if not self.current_info:
            return

        info = self.current_info
        is_playlist = info.get("_type") == "playlist"
        entries_count = len(info.get("entries", [])) if is_playlist else 1

        item = DownloadItem(
            url=self.url_input.text().strip(),
            title=info.get("title", "Unknown"),
            duration=info.get("duration", 0) or 0,
            uploader=info.get("uploader", "") or info.get("channel", "") or "",
            thumbnail_url=info.get("thumbnail", ""),
            is_playlist=is_playlist,
            playlist_count=entries_count,
            audio_only=self.format_panel.audio_only_check.isChecked(),
            quality=self.format_panel.get_quality(),
            audio_format=self.format_panel.get_audio_format(),
            audio_quality=self.format_panel.get_audio_quality(),
            output_dir=self.format_panel.output_dir.text().strip(),
            total_videos=entries_count,
        )

        self.download_queue.append(item)
        widget = self.queue_panel.add_item(item)
        widget.cancel_clicked.connect(lambda i=item: self._cancel_download(i))

        self._update_tab_counts()
        self.statusBar().showMessage(f"Added to queue: {item.title}")

        # Reset UI for next URL
        self.url_input.clear()
        self.info_card.hide()
        self.format_panel.hide()
        self.add_queue_btn.hide()
        self.current_info = None

        # Switch to downloads tab
        self.tabs.setCurrentIndex(0)

        self._process_queue()

    def _process_queue(self):
        """Start the next queued download if nothing is active."""
        if self.active_worker is not None:
            return

        for item in self.download_queue:
            if item.status == DownloadStatus.QUEUED:
                self._start_download(item)
                return

    def _start_download(self, item: DownloadItem):
        item.status = DownloadStatus.DOWNLOADING
        self.active_item = item

        opts = self._build_ydl_opts(item)
        self.active_worker = DownloadWorker(item.url, opts)

        self.active_worker.progress.connect(
            lambda data, i=item: self._on_progress(i, data)
        )
        self.active_worker.finished.connect(
            lambda i=item: self._on_download_finished(i)
        )
        self.active_worker.error.connect(
            lambda err, i=item: self._on_download_error(i, err)
        )
        self.active_worker.status_update.connect(
            lambda msg, i=item: self._on_status_update(i, msg)
        )
        self.active_worker.start()

        self.queue_panel.update_item(item)
        self.statusBar().showMessage(f"Downloading: {item.title}")

    def _build_ydl_opts(self, item: DownloadItem) -> dict:
        """Build yt-dlp options dict from a DownloadItem."""
        output_dir = item.output_dir or os.path.expanduser("~/Downloads")
        os.makedirs(output_dir, exist_ok=True)

        opts: dict = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "noplaylist": False,  # allow playlists
        }

        if item.audio_only:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": item.audio_format,
                    "preferredquality": item.audio_quality,
                }
            ]
        else:
            quality = item.quality
            if quality == "best":
                opts["format"] = "bestvideo+bestaudio/best"
            elif quality == "worst":
                opts["format"] = "worst"
            else:
                height = quality.replace("p", "")
                opts["format"] = (
                    f"bestvideo[height<={height}]+bestaudio"
                    f"/best[height<={height}]/best"
                )
            opts["merge_output_format"] = "mp4"

        return opts

    # ──────────────────────────────────
    # Download Callbacks
    # ──────────────────────────────────

    def _on_progress(self, item: DownloadItem, data: dict):
        status = data.get("status", "")

        if status == "downloading":
            video_percent = data.get("percent", 0)

            # Calculate overall progress for playlists
            pl_index = data.get("playlist_index")
            pl_count = data.get("playlist_count")
            if pl_count and pl_count > 1 and pl_index:
                per_video = 100.0 / pl_count
                item.progress = (pl_index - 1) * per_video + (video_percent / 100.0) * per_video
                item.current_video_index = pl_index
                item.total_videos = pl_count
            else:
                item.progress = video_percent

            item.speed = data.get("speed", "")
            item.eta = data.get("eta", "")
            item.filesize = data.get("total", "")

            if data.get("video_title"):
                item.current_video_title = data["video_title"]

        elif status == "processing":
            item.status = DownloadStatus.PROCESSING
            if data.get("filename"):
                item.output_path = data["filename"]

        self.queue_panel.update_item(item)

    def _on_status_update(self, item: DownloadItem, message: str):
        if "Post-processing" in message:
            item.status = DownloadStatus.PROCESSING
        self.queue_panel.update_item(item)

    def _on_download_finished(self, item: DownloadItem):
        item.status = DownloadStatus.COMPLETED
        item.progress = 100.0
        item.completed_at = time.time()

        self.active_worker = None
        self.active_item = None

        self.queue_panel.update_item(item)
        self.history_panel.add_item(item)
        self._save_history()
        self._update_tab_counts()
        self.statusBar().showMessage(f"Completed: {item.title}")

        self._process_queue()

    def _on_download_error(self, item: DownloadItem, error: str):
        if "Cancelled" in error:
            item.status = DownloadStatus.CANCELLED
        else:
            item.status = DownloadStatus.ERROR
            item.error_message = error

        self.active_worker = None
        self.active_item = None

        self.queue_panel.update_item(item)
        self._update_tab_counts()

        if item.status == DownloadStatus.ERROR:
            self.statusBar().showMessage(f"Error downloading {item.title}: {error}")
        else:
            self.statusBar().showMessage(f"Cancelled: {item.title}")

        self._process_queue()

    def _cancel_download(self, item: DownloadItem):
        """Cancel a download (active or queued)."""
        if item is self.active_item and self.active_worker:
            self.active_worker.cancel()
        elif item.status == DownloadStatus.QUEUED:
            item.status = DownloadStatus.CANCELLED
            self.queue_panel.update_item(item)
            self._update_tab_counts()

    # ──────────────────────────────────
    # History
    # ──────────────────────────────────

    def _load_history(self):
        history = self.settings.get("history", [])
        if isinstance(history, list):
            for entry in history:
                if isinstance(entry, dict):
                    self.history_panel.add_history_entry(entry)
        self._update_tab_counts()

    def _save_history(self):
        entries = self.history_panel.get_entries()
        self.settings.set("history", entries[-200:])

    def _on_history_cleared(self):
        self.settings.set("history", [])
        self._update_tab_counts()

    # ──────────────────────────────────
    # Helpers
    # ──────────────────────────────────

    def _update_tab_counts(self):
        active = sum(
            1 for i in self.download_queue
            if i.status in (
                DownloadStatus.QUEUED,
                DownloadStatus.DOWNLOADING,
                DownloadStatus.PROCESSING,
            )
        )
        self.tabs.setTabText(0, f"\U0001f4e5 Downloads ({active})")
        self.tabs.setTabText(
            1, f"\U0001f4cb History ({self.history_panel.count()})"
        )

    def closeEvent(self, event):
        """Handle window close — prompt if download is active."""
        if self.active_worker and self.active_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A download is in progress. Cancel it and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.active_worker.cancel()
            self.active_worker.wait(3000)

        self._save_history()
        self.settings.save()
        event.accept()
