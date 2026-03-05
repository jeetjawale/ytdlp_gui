"""Custom Qt widgets for the YT-DLP GUI application."""

import os
import time
import subprocess
import sys
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .models import DownloadItem, DownloadStatus, FormatInfo, format_duration, format_timestamp


# ─────────────────────────────────────────────
# Video Info Card
# ─────────────────────────────────────────────

class VideoInfoCard(QFrame):
    """Displays video/playlist metadata after fetching info."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("infoCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(110)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        # Thumbnail
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(160, 90)
        self.thumbnail.setObjectName("thumbnail")
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setText("No Preview")
        self.thumbnail.setScaledContents(False)
        layout.addWidget(self.thumbnail)

        # Info column
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        self.title_label = QLabel("Title")
        self.title_label.setObjectName("videoTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self.details_label = QLabel("")
        self.details_label.setObjectName("videoDetails")

        self.type_badge = QLabel("VIDEO")
        self.type_badge.setFixedHeight(22)
        self.type_badge.setMaximumWidth(100)
        self.type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.details_label)
        info_layout.addWidget(self.type_badge)
        info_layout.addStretch()

        layout.addLayout(info_layout, 1)

    def update_info(self, info: dict):
        """Update card with video/playlist metadata."""
        title = info.get("title", "Unknown")
        self.title_label.setText(title)

        is_playlist = info.get("_type") == "playlist"

        if is_playlist:
            entries = info.get("entries", [])
            count = len(entries)
            uploader = info.get("uploader", "") or info.get("channel", "") or ""
            details = f"{count} video{'s' if count != 1 else ''}"
            if uploader:
                details += f"  \u2022  {uploader}"
            self.details_label.setText(details)
            self.type_badge.setText("PLAYLIST")
            self.type_badge.setStyleSheet(
                "background-color: #f59e0b; color: #1e293b; border-radius: 4px; "
                "padding: 2px 10px; font-size: 11px; font-weight: bold;"
            )
        else:
            duration = format_duration(info.get("duration"))
            uploader = (
                info.get("uploader", "") or info.get("channel", "") or "Unknown"
            )
            self.details_label.setText(f"\u23f1 {duration}  \u2022  {uploader}")
            self.type_badge.setText("VIDEO")
            self.type_badge.setStyleSheet(
                "background-color: #6366f1; color: white; border-radius: 4px; "
                "padding: 2px 10px; font-size: 11px; font-weight: bold;"
            )

        self.thumbnail.setText("Loading...")

    def set_thumbnail(self, pixmap: QPixmap):
        """Display the fetched thumbnail."""
        scaled = pixmap.scaled(
            160, 90,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail.setPixmap(scaled)


# ─────────────────────────────────────────────
# Format Selection Panel
# ─────────────────────────────────────────────

class FormatPanel(QFrame):
    """Format, quality, and output directory selection."""

    browse_formats_clicked = pyqtSignal()

    def __init__(self, default_output_dir: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("formatPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Row 1: Audio-only toggle, quality, audio format/bitrate, browse formats btn
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        self.audio_only_check = QCheckBox("Audio Only")
        self.audio_only_check.toggled.connect(self._on_audio_only_toggled)
        row1.addWidget(self.audio_only_check)

        # Video quality
        self.quality_label = QLabel("Quality:")
        self.quality_label.setObjectName("formatLabel")
        self.quality_combo = QComboBox()
        self._populate_video_qualities()
        row1.addWidget(self.quality_label)
        row1.addWidget(self.quality_combo)

        # Audio format (visible only when audio-only)
        self.audio_format_label = QLabel("Format:")
        self.audio_format_label.setObjectName("formatLabel")
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "m4a", "opus", "flac", "wav"])
        self.audio_format_label.hide()
        self.audio_format_combo.hide()
        row1.addWidget(self.audio_format_label)
        row1.addWidget(self.audio_format_combo)

        # Audio bitrate (visible only when audio-only)
        self.audio_quality_label = QLabel("Bitrate:")
        self.audio_quality_label.setObjectName("formatLabel")
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320k", "256k", "192k", "128k", "96k"])
        self.audio_quality_combo.setCurrentIndex(2)  # 192k default
        self.audio_quality_label.hide()
        self.audio_quality_combo.hide()
        row1.addWidget(self.audio_quality_label)
        row1.addWidget(self.audio_quality_combo)

        # Browse formats button
        self.browse_formats_btn = QPushButton("\U0001f4ca Browse Formats")
        self.browse_formats_btn.setObjectName("browseFormatsBtn")
        self.browse_formats_btn.setToolTip("Show all available formats for manual selection")
        self.browse_formats_btn.clicked.connect(self.browse_formats_clicked.emit)
        self.browse_formats_btn.hide()  # shown only after info fetch
        row1.addWidget(self.browse_formats_btn)

        row1.addStretch()
        layout.addLayout(row1)

        # Selected format label (when manually chosen from browser)
        self.selected_format_label = QLabel("")
        self.selected_format_label.setObjectName("formatLabel")
        self.selected_format_label.hide()
        layout.addWidget(self.selected_format_label)

        # Row 2: Output directory + filename template
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        output_label = QLabel("Save to:")
        output_label.setObjectName("formatLabel")
        row2.addWidget(output_label)

        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Output directory...")
        default = default_output_dir or os.path.expanduser("~/Downloads")
        self.output_dir.setText(default)
        row2.addWidget(self.output_dir, 1)

        self.browse_btn = QPushButton("\U0001f4c1 Browse")
        self.browse_btn.setObjectName("browseBtn")
        row2.addWidget(self.browse_btn)

        layout.addLayout(row2)

        # Row 3: Filename template
        row3 = QHBoxLayout()
        row3.setSpacing(8)

        template_label = QLabel("Filename:")
        template_label.setObjectName("formatLabel")
        row3.addWidget(template_label)

        self.filename_template = QLineEdit()
        self.filename_template.setPlaceholderText("%(title)s.%(ext)s")
        self.filename_template.setText("%(title)s.%(ext)s")
        self.filename_template.setToolTip(
            "yt-dlp output template. Variables: %(title)s, %(id)s, "
            "%(ext)s, %(uploader)s, %(upload_date)s, etc."
        )
        row3.addWidget(self.filename_template, 1)

        layout.addLayout(row3)

        # Internal state for manual format override
        self._selected_format_id: str = ""

    def _populate_video_qualities(self):
        self.quality_combo.clear()
        self.quality_combo.addItems([
            "Best",
            "2160p (4K)",
            "1440p (2K)",
            "1080p (Full HD)",
            "720p (HD)",
            "480p",
            "360p",
            "Worst",
        ])

    def _on_audio_only_toggled(self, checked: bool):
        self.quality_label.setVisible(not checked)
        self.quality_combo.setVisible(not checked)
        self.audio_format_label.setVisible(checked)
        self.audio_format_combo.setVisible(checked)
        self.audio_quality_label.setVisible(checked)
        self.audio_quality_combo.setVisible(checked)
        # Clear manual format selection when toggling audio-only
        if checked:
            self.clear_manual_format()

    def get_quality(self) -> str:
        text = self.quality_combo.currentText()
        if text in ("Best", "Worst"):
            return text.lower()
        return text.split("p")[0].strip() + "p"

    def get_audio_format(self) -> str:
        return self.audio_format_combo.currentText()

    def get_audio_quality(self) -> str:
        return self.audio_quality_combo.currentText().replace("k", "")

    def get_filename_template(self) -> str:
        tmpl = self.filename_template.text().strip()
        return tmpl if tmpl else "%(title)s.%(ext)s"

    def get_selected_format_id(self) -> str:
        return self._selected_format_id

    def set_manual_format(self, format_id: str, description: str):
        """Set a manually-selected format from the format browser."""
        self._selected_format_id = format_id
        self.selected_format_label.setText(f"\u2714 Manual format: {description}")
        self.selected_format_label.show()
        # Disable auto quality selection
        self.quality_combo.setEnabled(False)

    def clear_manual_format(self):
        self._selected_format_id = ""
        self.selected_format_label.hide()
        self.quality_combo.setEnabled(True)


# ─────────────────────────────────────────────
# Advanced Settings Panel (Subtitles, Speed, Cookies, SponsorBlock)
# ─────────────────────────────────────────────

class AdvancedSettingsPanel(QFrame):
    """Advanced download options: subtitles, speed limit, cookies, SponsorBlock."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("settingsPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Row 1: Subtitles + SponsorBlock
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        self.write_subs_check = QCheckBox("Download Subtitles")
        self.write_subs_check.toggled.connect(self._on_subs_toggled)
        row1.addWidget(self.write_subs_check)

        self.embed_subs_check = QCheckBox("Embed in Video")
        self.embed_subs_check.setToolTip("Embed subtitles into the video file (mp4/mkv)")
        self.embed_subs_check.setEnabled(False)
        row1.addWidget(self.embed_subs_check)

        self.sub_langs_label = QLabel("Languages:")
        self.sub_langs_label.setObjectName("formatLabel")
        self.sub_langs_input = QLineEdit()
        self.sub_langs_input.setText("en")
        self.sub_langs_input.setPlaceholderText("en, es, fr, ...")
        self.sub_langs_input.setMaximumWidth(150)
        self.sub_langs_input.setToolTip(
            "Comma-separated language codes. Use 'all' for every available language."
        )
        self.sub_langs_label.setEnabled(False)
        self.sub_langs_input.setEnabled(False)
        row1.addWidget(self.sub_langs_label)
        row1.addWidget(self.sub_langs_input)

        row1.addSpacing(20)

        self.sponsorblock_check = QCheckBox("SponsorBlock")
        self.sponsorblock_check.setToolTip(
            "Remove sponsor segments, intros, outros (YouTube only)"
        )
        row1.addWidget(self.sponsorblock_check)

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Speed limit + Cookies
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        speed_label = QLabel("Speed Limit:")
        speed_label.setObjectName("formatLabel")
        row2.addWidget(speed_label)

        self.speed_limit_combo = QComboBox()
        self.speed_limit_combo.addItems([
            "Unlimited",
            "500 KB/s",
            "1 MB/s",
            "2 MB/s",
            "5 MB/s",
            "10 MB/s",
        ])
        self.speed_limit_combo.setToolTip("Limit download bandwidth")
        row2.addWidget(self.speed_limit_combo)

        row2.addSpacing(20)

        cookie_label = QLabel("Cookies from:")
        cookie_label.setObjectName("formatLabel")
        row2.addWidget(cookie_label)

        self.cookie_combo = QComboBox()
        self.cookie_combo.addItems([
            "None",
            "chrome",
            "firefox",
            "edge",
            "safari",
            "opera",
            "brave",
            "vivaldi",
        ])
        self.cookie_combo.setToolTip(
            "Import cookies from browser for age-restricted / member-only content"
        )
        row2.addWidget(self.cookie_combo)

        row2.addStretch()
        layout.addLayout(row2)

    def _on_subs_toggled(self, checked: bool):
        self.embed_subs_check.setEnabled(checked)
        self.sub_langs_label.setEnabled(checked)
        self.sub_langs_input.setEnabled(checked)
        if not checked:
            self.embed_subs_check.setChecked(False)

    # Getters
    def get_write_subs(self) -> bool:
        return self.write_subs_check.isChecked()

    def get_embed_subs(self) -> bool:
        return self.embed_subs_check.isChecked()

    def get_subtitle_langs(self) -> str:
        return self.sub_langs_input.text().strip() or "en"

    def get_sponsorblock(self) -> bool:
        return self.sponsorblock_check.isChecked()

    def get_speed_limit(self) -> int:
        """Return speed limit in bytes/sec, 0 for unlimited."""
        text = self.speed_limit_combo.currentText()
        if text == "Unlimited":
            return 0
        # Parse "500 KB/s" -> 500 * 1024, "1 MB/s" -> 1 * 1024 * 1024
        parts = text.replace("/s", "").strip().split()
        value = float(parts[0])
        unit = parts[1]
        if unit == "KB":
            return int(value * 1024)
        elif unit == "MB":
            return int(value * 1024 * 1024)
        return 0

    def get_cookie_browser(self) -> str:
        text = self.cookie_combo.currentText()
        return "" if text == "None" else text


# ─────────────────────────────────────────────
# Format Browser Dialog
# ─────────────────────────────────────────────

class FormatBrowserDialog(QDialog):
    """Dialog showing all available formats in a table for manual selection."""

    format_selected = pyqtSignal(str, str)  # format_id, description

    def __init__(self, formats: List[FormatInfo], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("formatBrowserDialog")
        self.setWindowTitle("Available Formats")
        self.setMinimumSize(750, 450)
        self.resize(850, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel(f"Showing {len(formats)} available formats  \u2014  click a row and select")
        header.setStyleSheet("font-size: 13px; padding: 4px;")
        layout.addWidget(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Ext", "Resolution", "FPS", "Video Codec", "Audio Codec",
            "Size", "Type",
        ])
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setRowCount(len(formats))
        self._formats = formats

        for row, f in enumerate(formats):
            self.table.setItem(row, 0, QTableWidgetItem(f.format_id))
            self.table.setItem(row, 1, QTableWidgetItem(f.ext))
            self.table.setItem(row, 2, QTableWidgetItem(f.resolution))
            self.table.setItem(
                row, 3, QTableWidgetItem(str(f.fps) if f.fps else "-")
            )
            self.table.setItem(row, 4, QTableWidgetItem(f.vcodec if f.vcodec != "none" else "-"))
            self.table.setItem(row, 5, QTableWidgetItem(f.acodec if f.acodec != "none" else "-"))
            self.table.setItem(row, 6, QTableWidgetItem(f.filesize_str))
            self.table.setItem(row, 7, QTableWidgetItem(f.type_label))

        layout.addWidget(self.table, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.select_btn = QPushButton("Use Selected Format")
        self.select_btn.setObjectName("selectFormatBtn")
        self.select_btn.clicked.connect(self._on_select)
        btn_layout.addWidget(self.select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("loadFileBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _on_select(self):
        row = self.table.currentRow()
        if row < 0:
            return
        f = self._formats[row]
        desc = f"{f.format_id} ({f.ext}, {f.resolution}, {f.type_label})"
        self.format_selected.emit(f.format_id, desc)
        self.accept()


# ─────────────────────────────────────────────
# Batch Import Dialog
# ─────────────────────────────────────────────

class BatchImportDialog(QDialog):
    """Dialog for pasting or loading multiple URLs at once."""

    urls_ready = pyqtSignal(list)  # list of URL strings

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("batchDialog")
        self.setWindowTitle("Batch Import URLs")
        self.setMinimumSize(550, 380)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Enter one URL per line, or load from a text file:")
        header.setStyleSheet("font-size: 13px; padding: 4px;")
        layout.addWidget(header)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "https://www.youtube.com/watch?v=...\n"
            "https://www.youtube.com/watch?v=...\n"
            "https://vimeo.com/..."
        )
        layout.addWidget(self.text_edit, 1)

        btn_layout = QHBoxLayout()

        load_btn = QPushButton("\U0001f4c4 Load from File")
        load_btn.setObjectName("loadFileBtn")
        load_btn.clicked.connect(self._load_file)
        btn_layout.addWidget(load_btn)

        btn_layout.addStretch()

        count_label = QLabel("")
        self._count_label = count_label
        btn_layout.addWidget(count_label)

        add_btn = QPushButton("\U0001f4e5 Add All")
        add_btn.setObjectName("batchAddBtn")
        add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(add_btn)

        layout.addLayout(btn_layout)

        self.text_edit.textChanged.connect(self._update_count)

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load URLs from File", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())
            except OSError:
                pass

    def _update_count(self):
        urls = self._parse_urls()
        self._count_label.setText(f"{len(urls)} URL{'s' if len(urls) != 1 else ''}")

    def _parse_urls(self) -> List[str]:
        text = self.text_edit.toPlainText()
        urls = []
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
        return urls

    def _on_add(self):
        urls = self._parse_urls()
        if urls:
            self.urls_ready.emit(urls)
            self.accept()


# ─────────────────────────────────────────────
# Download Item Widget (queue entry)
# ─────────────────────────────────────────────

class DownloadItemWidget(QFrame):
    """Displays a single download's progress in the queue."""

    cancel_clicked = pyqtSignal()

    def __init__(self, item: DownloadItem, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.item = item
        self.setObjectName("downloadItem")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        # Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        self.title_label = QLabel(item.title)
        self.title_label.setObjectName("downloadTitle")
        self.title_label.setWordWrap(True)
        title_row.addWidget(self.title_label, 1)

        self.status_label = QLabel(item.status.value)
        self.status_label.setObjectName("statusLabel")
        title_row.addWidget(self.status_label)

        self.cancel_btn = QPushButton("\u2715")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedSize(28, 28)
        self.cancel_btn.setToolTip("Cancel download")
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        title_row.addWidget(self.cancel_btn)

        layout.addLayout(title_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        # Details row
        self.details_label = QLabel("")
        self.details_label.setObjectName("downloadDetails")
        layout.addWidget(self.details_label)

        self._apply_initial_state()

    def _apply_initial_state(self):
        item = self.item
        mode = "Audio" if item.audio_only else f"Video ({item.quality})"
        self.details_label.setText(f"Waiting in queue  \u2022  {mode}")
        self.status_label.setStyleSheet("color: #94a3b8; font-weight: bold;")

    def update_from_item(self, item: DownloadItem):
        """Refresh widget display from updated DownloadItem."""
        self.item = item
        status = item.status

        # Title
        title_text = item.title
        if item.is_playlist and item.current_video_title:
            title_text = f"{item.title}\n\u25b8 {item.current_video_title}"
        self.title_label.setText(title_text)

        # Progress bar value
        self.progress_bar.setValue(int(item.progress * 10))

        # Status label text + color
        self.status_label.setText(status.value)
        status_colors = {
            DownloadStatus.QUEUED: "#94a3b8",
            DownloadStatus.DOWNLOADING: "#6366f1",
            DownloadStatus.PROCESSING: "#f59e0b",
            DownloadStatus.COMPLETED: "#22c55e",
            DownloadStatus.ERROR: "#ef4444",
            DownloadStatus.CANCELLED: "#64748b",
        }
        color = status_colors.get(status, "#94a3b8")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Progress bar color override
        if status == DownloadStatus.COMPLETED:
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #22c55e; border-radius: 3px; }"
            )
        elif status == DownloadStatus.ERROR:
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #ef4444; border-radius: 3px; }"
            )
        else:
            self.progress_bar.setStyleSheet("")

        # Details text
        if status == DownloadStatus.DOWNLOADING:
            parts = []
            if item.progress > 0:
                parts.append(f"{item.progress:.1f}%")
            if item.speed:
                parts.append(item.speed)
            if item.eta and item.eta != "N/A":
                parts.append(f"ETA {item.eta}")
            if item.filesize:
                parts.append(item.filesize)
            if item.is_playlist and item.total_videos > 1:
                parts.append(
                    f"Video {item.current_video_index}/{item.total_videos}"
                )
            self.details_label.setText(
                "  \u2022  ".join(parts) if parts else "Starting..."
            )
            self.details_label.setStyleSheet("color: #94a3b8;")

        elif status == DownloadStatus.PROCESSING:
            self.details_label.setText("Post-processing...")
            self.details_label.setStyleSheet("color: #f59e0b;")

        elif status == DownloadStatus.COMPLETED:
            self.details_label.setText("Download complete \u2714")
            self.details_label.setStyleSheet("color: #22c55e;")
            self.cancel_btn.hide()

        elif status == DownloadStatus.ERROR:
            msg = item.error_message or "Unknown error"
            self.details_label.setText(f"Error: {msg}")
            self.details_label.setStyleSheet("color: #ef4444;")
            self.cancel_btn.hide()

        elif status == DownloadStatus.CANCELLED:
            self.details_label.setText("Cancelled")
            self.details_label.setStyleSheet("color: #64748b;")
            self.cancel_btn.hide()

        elif status == DownloadStatus.QUEUED:
            mode = "Audio" if item.audio_only else f"Video ({item.quality})"
            self.details_label.setText(f"Waiting in queue  \u2022  {mode}")
            self.details_label.setStyleSheet("color: #94a3b8;")


# ─────────────────────────────────────────────
# Queue Panel
# ─────────────────────────────────────────────

class QueuePanel(QWidget):
    """Scrollable panel containing active and queued downloads."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(8, 8, 8, 8)

        self.empty_label = QLabel(
            "No downloads yet.\nEnter a URL above to get started."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("emptyLabel")
        self.container_layout.addWidget(self.empty_label)

        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        layout.addWidget(scroll)

        self.item_widgets: Dict[str, DownloadItemWidget] = {}

    def add_item(self, item: DownloadItem) -> DownloadItemWidget:
        """Add a new download item widget to the queue."""
        self.empty_label.hide()
        widget = DownloadItemWidget(item)
        idx = self.container_layout.count() - 1
        self.container_layout.insertWidget(idx, widget)
        self.item_widgets[item.id] = widget
        return widget

    def update_item(self, item: DownloadItem):
        """Update an existing download item's widget."""
        widget = self.item_widgets.get(item.id)
        if widget:
            widget.update_from_item(item)


# ─────────────────────────────────────────────
# History Item Widget
# ─────────────────────────────────────────────

class HistoryItemWidget(QFrame):
    """Displays a single completed download in the history panel."""

    def __init__(self, data: dict, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.data = data
        self.setObjectName("historyItem")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        title = QLabel(data.get("title", "Unknown"))
        title.setObjectName("historyTitle")
        title.setWordWrap(True)
        info_layout.addWidget(title)

        details_parts = []
        if data.get("completed_at"):
            details_parts.append(format_timestamp(data["completed_at"]))
        if data.get("audio_only"):
            fmt = data.get("audio_format", "mp3")
            details_parts.append(f"Audio ({fmt})")
        else:
            q = data.get("quality", "best")
            details_parts.append(f"Video ({q})")

        details = QLabel("  \u2022  ".join(details_parts))
        details.setObjectName("historyDetails")
        info_layout.addWidget(details)

        layout.addLayout(info_layout, 1)

        output_dir = data.get("output_dir", "")
        if output_dir and os.path.isdir(output_dir):
            open_btn = QPushButton("\U0001f4c2 Open Folder")
            open_btn.setObjectName("openFolderBtn")
            open_btn.clicked.connect(lambda: self._open_folder(output_dir))
            layout.addWidget(open_btn)

        status = QLabel("\u2714 Completed")
        status.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 12px;")
        layout.addWidget(status)

    @staticmethod
    def _open_folder(path: str):
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", path])


# ─────────────────────────────────────────────
# History Panel
# ─────────────────────────────────────────────

class HistoryPanel(QWidget):
    """Scrollable panel containing completed download history."""

    history_cleared = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(8, 0, 8, 0)
        top_bar.addStretch()
        self.clear_btn = QPushButton("\U0001f5d1 Clear History")
        self.clear_btn.setObjectName("clearHistoryBtn")
        self.clear_btn.clicked.connect(self._clear_all)
        top_bar.addWidget(self.clear_btn)
        layout.addLayout(top_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(8, 8, 8, 8)

        self.empty_label = QLabel("No download history yet.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("emptyLabel")
        self.container_layout.addWidget(self.empty_label)

        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        layout.addWidget(scroll)

        self._entries: List[dict] = []

    def add_item(self, item: DownloadItem):
        entry = {
            "title": item.title,
            "url": item.url,
            "completed_at": item.completed_at or time.time(),
            "audio_only": item.audio_only,
            "audio_format": item.audio_format,
            "quality": item.quality,
            "output_dir": item.output_dir,
        }
        self._entries.append(entry)
        self._add_entry_widget(entry)

    def add_history_entry(self, entry: dict):
        self._entries.append(entry)
        self._add_entry_widget(entry)

    def _add_entry_widget(self, entry: dict):
        self.empty_label.hide()
        widget = HistoryItemWidget(entry)
        self.container_layout.insertWidget(0, widget)

    def count(self) -> int:
        return len(self._entries)

    def get_entries(self) -> List[dict]:
        return list(self._entries)

    def _clear_all(self):
        self._entries.clear()
        while self.container_layout.count() > 1:
            child = self.container_layout.takeAt(0)
            w = child.widget()
            if w and w is not self.empty_label:
                w.deleteLater()
            elif w is self.empty_label:
                self.container_layout.insertWidget(0, self.empty_label)
                self.empty_label.show()
                break

        if not self.empty_label.isVisible():
            self.container_layout.insertWidget(0, self.empty_label)
            self.empty_label.show()

        self.history_cleared.emit()
