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
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .models import DownloadItem, DownloadStatus, format_duration, format_timestamp


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

    def __init__(self, default_output_dir: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("formatPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Row 1: Audio-only toggle, quality, audio format/bitrate
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

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Output directory
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

    def get_quality(self) -> str:
        text = self.quality_combo.currentText()
        if text in ("Best", "Worst"):
            return text.lower()
        # Extract e.g. "1080" from "1080p (Full HD)"
        return text.split("p")[0].strip() + "p"

    def get_audio_format(self) -> str:
        return self.audio_format_combo.currentText()

    def get_audio_quality(self) -> str:
        return self.audio_quality_combo.currentText().replace("k", "")


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

        # Progress bar color override for terminal states
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
            self.details_label.setText("  \u2022  ".join(parts) if parts else "Starting...")
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

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(8, 8, 8, 8)

        # Empty state
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
        # Insert before the stretch at the end
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

        # Info column
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

        # Open folder button
        output_dir = data.get("output_dir", "")
        if output_dir and os.path.isdir(output_dir):
            open_btn = QPushButton("\U0001f4c2 Open Folder")
            open_btn.setObjectName("openFolderBtn")
            open_btn.clicked.connect(lambda: self._open_folder(output_dir))
            layout.addWidget(open_btn)

        # Status
        status = QLabel("\u2714 Completed")
        status.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 12px;")
        layout.addWidget(status)

    @staticmethod
    def _open_folder(path: str):
        """Open a folder in the system file manager."""
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

        # Top bar with clear button
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(8, 0, 8, 0)
        top_bar.addStretch()
        self.clear_btn = QPushButton("\U0001f5d1 Clear History")
        self.clear_btn.setObjectName("clearHistoryBtn")
        self.clear_btn.clicked.connect(self._clear_all)
        top_bar.addWidget(self.clear_btn)
        layout.addLayout(top_bar)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(8, 8, 8, 8)

        # Empty state
        self.empty_label = QLabel("No download history yet.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("emptyLabel")
        self.container_layout.addWidget(self.empty_label)

        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        layout.addWidget(scroll)

        self._entries: List[dict] = []

    def add_item(self, item: DownloadItem):
        """Add a completed DownloadItem to history."""
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
        """Add a pre-existing history entry (loaded from settings)."""
        self._entries.append(entry)
        self._add_entry_widget(entry)

    def _add_entry_widget(self, entry: dict):
        self.empty_label.hide()
        widget = HistoryItemWidget(entry)
        # Insert at top (newest first), before empty_label and stretch
        self.container_layout.insertWidget(0, widget)

    def count(self) -> int:
        return len(self._entries)

    def get_entries(self) -> List[dict]:
        return list(self._entries)

    def _clear_all(self):
        self._entries.clear()
        # Remove all widgets except stretch (last item)
        while self.container_layout.count() > 1:
            child = self.container_layout.takeAt(0)
            w = child.widget()
            if w and w is not self.empty_label:
                w.deleteLater()
            elif w is self.empty_label:
                # Re-add it
                self.container_layout.insertWidget(0, self.empty_label)
                self.empty_label.show()
                break

        # Ensure empty label is visible
        if not self.empty_label.isVisible():
            self.container_layout.insertWidget(0, self.empty_label)
            self.empty_label.show()

        self.history_cleared.emit()
