"""Main application window for the YT-DLP GUI."""

import os
import time
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .models import DownloadItem, DownloadStatus, FormatInfo
from .settings import Settings
from .styles import DARK_THEME, LIGHT_THEME
from .widgets import (
    AdvancedSettingsPanel,
    BatchImportDialog,
    FormatBrowserDialog,
    FormatPanel,
    HistoryPanel,
    QueuePanel,
    VideoInfoCard,
)
from .workers import DownloadWorker, InfoWorker


class MainWindow(QMainWindow):
    """Main application window with all features."""

    MAX_CONCURRENT = 3  # configurable concurrent download limit

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT-DLP GUI")
        self.setMinimumSize(880, 660)
        self.resize(1000, 760)

        # ── State ──
        self.current_info: Optional[dict] = None
        self.current_formats: List[FormatInfo] = []
        self.download_queue: List[DownloadItem] = []
        self.active_workers: Dict[str, DownloadWorker] = {}  # item.id -> worker
        self.info_worker: Optional[InfoWorker] = None
        self.settings = Settings()
        self._dark_mode = self.settings.get("dark_mode", True)

        # Apply theme
        self.setStyleSheet(DARK_THEME if self._dark_mode else LIGHT_THEME)

        # Enable drag & drop
        self.setAcceptDrops(True)

        self._setup_ui()
        self._setup_tray()
        self._connect_signals()
        self._load_history()

    # ──────────────────────────────────
    # UI Setup
    # ──────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(18, 14, 18, 12)

        # ─── Top toolbar row: URL bar + batch + theme ───
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText(
            "Paste a YouTube, Vimeo, or any supported URL here... (or drag & drop)"
        )

        self.paste_btn = QPushButton("\U0001f4cb")
        self.paste_btn.setToolTip("Paste from clipboard")
        self.paste_btn.setObjectName("pasteBtn")
        self.paste_btn.setFixedSize(42, 42)

        self.fetch_btn = QPushButton("\U0001f50d  Fetch Info")
        self.fetch_btn.setObjectName("fetchBtn")
        self.fetch_btn.setFixedWidth(130)
        self.fetch_btn.setFixedHeight(42)

        self.batch_btn = QPushButton("\U0001f4c4")
        self.batch_btn.setToolTip("Batch import multiple URLs")
        self.batch_btn.setObjectName("batchBtn")
        self.batch_btn.setFixedSize(42, 42)

        self.theme_btn = QPushButton("\U0001f319" if self._dark_mode else "\u2600\ufe0f")
        self.theme_btn.setToolTip("Toggle light / dark theme")
        self.theme_btn.setObjectName("themeToggle")
        self.theme_btn.setFixedSize(38, 38)

        top_row.addWidget(self.url_input)
        top_row.addWidget(self.paste_btn)
        top_row.addWidget(self.fetch_btn)
        top_row.addWidget(self.batch_btn)
        top_row.addWidget(self.theme_btn)
        main_layout.addLayout(top_row)

        # ─── Video info card (hidden until fetch) ───
        self.info_card = VideoInfoCard()
        self.info_card.hide()
        main_layout.addWidget(self.info_card)

        # ─── Format options panel (hidden until fetch) ───
        default_dir = self.settings.get("output_dir", "")
        self.format_panel = FormatPanel(default_dir)
        self.format_panel.hide()
        main_layout.addWidget(self.format_panel)

        # ─── Advanced settings panel (hidden until fetch) ───
        self.advanced_panel = AdvancedSettingsPanel()
        self.advanced_panel.hide()
        main_layout.addWidget(self.advanced_panel)

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
        self.statusBar().showMessage(
            "Ready \u2014 Paste a URL, drag & drop, or use batch import"
        )

    # ──────────────────────────────────
    # System Tray
    # ──────────────────────────────────

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # Use application icon or a default
        icon = self.windowIcon()
        if icon.isNull():
            icon = QIcon.fromTheme("video-x-generic")
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("YT-DLP GUI")

        tray_menu = QMenu()
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_from_tray)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _show_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def _quit_from_tray(self):
        self._force_quit = True
        self.close()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._show_from_tray()

    def _notify(self, title: str, message: str):
        """Send a system tray notification."""
        if self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title, message,
                QSystemTrayIcon.MessageIcon.Information, 3000,
            )

    # ──────────────────────────────────
    # Signal connections
    # ──────────────────────────────────

    def _connect_signals(self):
        self.fetch_btn.clicked.connect(self.fetch_info)
        self.paste_btn.clicked.connect(self._paste_url)
        self.url_input.returnPressed.connect(self.fetch_info)
        self.add_queue_btn.clicked.connect(self.add_to_queue)
        self.format_panel.browse_btn.clicked.connect(self._browse_output_dir)
        self.format_panel.browse_formats_clicked.connect(self._open_format_browser)
        self.history_panel.history_cleared.connect(self._on_history_cleared)
        self.batch_btn.clicked.connect(self._open_batch_import)
        self.theme_btn.clicked.connect(self._toggle_theme)

    # ──────────────────────────────────
    # Drag & Drop
    # ──────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime = event.mimeData()
        if mime.hasUrls() or mime.hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        urls: List[str] = []

        if mime.hasUrls():
            for url in mime.urls():
                text = url.toString().strip()
                if text:
                    urls.append(text)
        elif mime.hasText():
            for line in mime.text().splitlines():
                line = line.strip()
                if line:
                    urls.append(line)

        if len(urls) == 1:
            self.url_input.setText(urls[0])
            self.fetch_info()
        elif urls:
            self._batch_fetch(urls)

        event.acceptProposedAction()

    # ──────────────────────────────────
    # Theme Toggle
    # ──────────────────────────────────

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self.setStyleSheet(DARK_THEME if self._dark_mode else LIGHT_THEME)
        self.theme_btn.setText("\U0001f319" if self._dark_mode else "\u2600\ufe0f")
        self.settings.set("dark_mode", self._dark_mode)

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

        # Disconnect any previous worker
        if self.info_worker is not None:
            try:
                self.info_worker.info_ready.disconnect()
                self.info_worker.formats_ready.disconnect()
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
        self.advanced_panel.hide()
        self.add_queue_btn.hide()
        self.current_info = None
        self.current_formats = []
        self.format_panel.clear_manual_format()
        self.format_panel.browse_formats_btn.hide()

        cookie_browser = self.advanced_panel.get_cookie_browser()
        self.info_worker = InfoWorker(url, cookie_browser)
        self.info_worker.info_ready.connect(self._on_info_ready)
        self.info_worker.formats_ready.connect(self._on_formats_ready)
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
        self.advanced_panel.show()
        self.add_queue_btn.show()

        if is_playlist:
            count = len(info.get("entries", []))
            self.statusBar().showMessage(
                f"Playlist: {title} ({count} video{'s' if count != 1 else ''})"
            )
        else:
            self.statusBar().showMessage(f"Video: {title}")

    def _on_formats_ready(self, formats: list):
        self.current_formats = formats
        self.format_panel.browse_formats_btn.show()

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
    # Format Browser
    # ──────────────────────────────────

    def _open_format_browser(self):
        if not self.current_formats:
            self.statusBar().showMessage("No format data available")
            return
        dialog = FormatBrowserDialog(self.current_formats, self)
        dialog.format_selected.connect(self.format_panel.set_manual_format)
        dialog.exec()

    # ──────────────────────────────────
    # Batch Import
    # ──────────────────────────────────

    def _open_batch_import(self):
        dialog = BatchImportDialog(self)
        dialog.urls_ready.connect(self._batch_fetch)
        dialog.exec()

    def _batch_fetch(self, urls: List[str]):
        """Add multiple URLs to the queue using current format settings."""
        count = 0
        for url in urls:
            url = url.strip()
            if not url:
                continue
            item = DownloadItem(
                url=url,
                title=url[:60] + "..." if len(url) > 60 else url,
                audio_only=self.format_panel.audio_only_check.isChecked(),
                quality=self.format_panel.get_quality(),
                audio_format=self.format_panel.get_audio_format(),
                audio_quality=self.format_panel.get_audio_quality(),
                output_dir=self.format_panel.output_dir.text().strip(),
                filename_template=self.format_panel.get_filename_template(),
                format_id=self.format_panel.get_selected_format_id(),
                write_subs=self.advanced_panel.get_write_subs(),
                embed_subs=self.advanced_panel.get_embed_subs(),
                subtitle_langs=self.advanced_panel.get_subtitle_langs(),
                speed_limit=self.advanced_panel.get_speed_limit(),
                cookie_browser=self.advanced_panel.get_cookie_browser(),
                sponsorblock=self.advanced_panel.get_sponsorblock(),
            )
            self._enqueue_item(item)
            count += 1

        self.tabs.setCurrentIndex(0)
        self.statusBar().showMessage(f"Batch added {count} URL{'s' if count != 1 else ''} to queue")
        self._process_queue()

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
            filename_template=self.format_panel.get_filename_template(),
            format_id=self.format_panel.get_selected_format_id(),
            total_videos=entries_count,
            # Advanced options
            write_subs=self.advanced_panel.get_write_subs(),
            embed_subs=self.advanced_panel.get_embed_subs(),
            subtitle_langs=self.advanced_panel.get_subtitle_langs(),
            speed_limit=self.advanced_panel.get_speed_limit(),
            cookie_browser=self.advanced_panel.get_cookie_browser(),
            sponsorblock=self.advanced_panel.get_sponsorblock(),
        )

        self._enqueue_item(item)
        self.statusBar().showMessage(f"Added to queue: {item.title}")

        # Reset UI for next URL
        self.url_input.clear()
        self.info_card.hide()
        self.format_panel.hide()
        self.advanced_panel.hide()
        self.add_queue_btn.hide()
        self.current_info = None
        self.current_formats = []
        self.format_panel.clear_manual_format()
        self.format_panel.browse_formats_btn.hide()

        self.tabs.setCurrentIndex(0)
        self._process_queue()

    def _enqueue_item(self, item: DownloadItem):
        """Add a DownloadItem to the queue and create its widget."""
        self.download_queue.append(item)
        widget = self.queue_panel.add_item(item)
        widget.cancel_clicked.connect(lambda i=item: self._cancel_download(i))
        self._update_tab_counts()

    def _process_queue(self):
        """Start queued downloads up to MAX_CONCURRENT."""
        active_count = len(self.active_workers)
        if active_count >= self.MAX_CONCURRENT:
            return

        for item in self.download_queue:
            if item.status == DownloadStatus.QUEUED:
                self._start_download(item)
                active_count += 1
                if active_count >= self.MAX_CONCURRENT:
                    return

    def _start_download(self, item: DownloadItem):
        item.status = DownloadStatus.DOWNLOADING

        opts = self._build_ydl_opts(item)
        worker = DownloadWorker(item.url, opts)

        worker.progress.connect(
            lambda data, i=item: self._on_progress(i, data)
        )
        worker.finished.connect(
            lambda i=item: self._on_download_finished(i)
        )
        worker.error.connect(
            lambda err, i=item: self._on_download_error(i, err)
        )
        worker.status_update.connect(
            lambda msg, i=item: self._on_status_update(i, msg)
        )

        self.active_workers[item.id] = worker
        worker.start()

        self.queue_panel.update_item(item)
        self.statusBar().showMessage(f"Downloading: {item.title}")

    def _build_ydl_opts(self, item: DownloadItem) -> dict:
        """Build yt-dlp options dict from a DownloadItem."""
        output_dir = item.output_dir or os.path.expanduser("~/Downloads")
        os.makedirs(output_dir, exist_ok=True)

        template = item.filename_template or "%(title)s.%(ext)s"
        opts: dict = {
            "outtmpl": os.path.join(output_dir, template),
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "noplaylist": False,
        }

        # ── Format selection ──
        if item.format_id:
            # Manual format from format browser
            opts["format"] = item.format_id
        elif item.audio_only:
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

        # ── Subtitles ──
        if item.write_subs:
            opts["writesubtitles"] = True
            opts["subtitleslangs"] = [
                lang.strip() for lang in item.subtitle_langs.split(",")
            ]
            if item.embed_subs:
                pps = opts.get("postprocessors", [])
                pps.append({"key": "FFmpegEmbedSubtitle"})
                opts["postprocessors"] = pps

        # ── Speed limit ──
        if item.speed_limit > 0:
            opts["ratelimit"] = item.speed_limit

        # ── Cookies ──
        if item.cookie_browser:
            opts["cookiesfrombrowser"] = (item.cookie_browser,)

        # ── SponsorBlock ──
        if item.sponsorblock:
            pps = opts.get("postprocessors", [])
            pps.append({
                "key": "SponsorBlock",
                "categories": ["sponsor", "intro", "outro", "selfpromo", "interaction"],
            })
            pps.append({"key": "ModifyChapters", "remove_sponsor_segments": ["sponsor", "intro", "outro", "selfpromo", "interaction"]})
            opts["postprocessors"] = pps

        return opts

    # ──────────────────────────────────
    # Download Callbacks
    # ──────────────────────────────────

    def _on_progress(self, item: DownloadItem, data: dict):
        status = data.get("status", "")

        if status == "downloading":
            video_percent = data.get("percent", 0)

            pl_index = data.get("playlist_index")
            pl_count = data.get("playlist_count")
            if pl_count and pl_count > 1 and pl_index:
                per_video = 100.0 / pl_count
                item.progress = (
                    (pl_index - 1) * per_video
                    + (video_percent / 100.0) * per_video
                )
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

        # Clean up worker
        self.active_workers.pop(item.id, None)

        self.queue_panel.update_item(item)
        self.history_panel.add_item(item)
        self._save_history()
        self._update_tab_counts()

        msg = f"Completed: {item.title}"
        self.statusBar().showMessage(msg)
        self._notify("Download Complete", item.title)

        self._process_queue()

    def _on_download_error(self, item: DownloadItem, error: str):
        if "Cancelled" in error:
            item.status = DownloadStatus.CANCELLED
        else:
            item.status = DownloadStatus.ERROR
            item.error_message = error

        self.active_workers.pop(item.id, None)

        self.queue_panel.update_item(item)
        self._update_tab_counts()

        if item.status == DownloadStatus.ERROR:
            self.statusBar().showMessage(
                f"Error downloading {item.title}: {error}"
            )
            self._notify("Download Error", f"{item.title}: {error}")
        else:
            self.statusBar().showMessage(f"Cancelled: {item.title}")

        self._process_queue()

    def _cancel_download(self, item: DownloadItem):
        """Cancel a download (active or queued)."""
        worker = self.active_workers.get(item.id)
        if worker:
            worker.cancel()
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
        """Minimize to tray instead of closing, unless explicitly quitting."""
        if not getattr(self, "_force_quit", False) and self.tray_icon.isSystemTrayAvailable():
            # If downloads are running, minimize to tray
            if self.active_workers:
                event.ignore()
                self.hide()
                self._notify(
                    "Still Running",
                    f"{len(self.active_workers)} download(s) in progress"
                )
                return

        # Actually quit
        if self.active_workers:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                f"{len(self.active_workers)} download(s) in progress. Cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            for worker in list(self.active_workers.values()):
                worker.cancel()
                worker.wait(2000)

        self._save_history()
        self.settings.save()
        self.tray_icon.hide()
        event.accept()
