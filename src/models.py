"""Data models for the YT-DLP GUI application."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import time
import uuid


class DownloadStatus(Enum):
    """Status of a download item."""
    QUEUED = "Queued"
    DOWNLOADING = "Downloading"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    ERROR = "Error"
    CANCELLED = "Cancelled"


@dataclass
class FormatInfo:
    """A single available format from yt-dlp."""
    format_id: str = ""
    ext: str = ""
    resolution: str = ""
    fps: Optional[int] = None
    vcodec: str = ""
    acodec: str = ""
    filesize: Optional[int] = None
    tbr: Optional[float] = None  # total bitrate
    note: str = ""

    @property
    def type_label(self) -> str:
        has_video = self.vcodec and self.vcodec != "none"
        has_audio = self.acodec and self.acodec != "none"
        if has_video and has_audio:
            return "Video+Audio"
        elif has_video:
            return "Video Only"
        elif has_audio:
            return "Audio Only"
        return "Unknown"

    @property
    def filesize_str(self) -> str:
        if not self.filesize:
            return "N/A"
        if self.filesize < 1024 * 1024:
            return f"{self.filesize / 1024:.0f} KB"
        elif self.filesize < 1024 * 1024 * 1024:
            return f"{self.filesize / (1024 * 1024):.1f} MB"
        return f"{self.filesize / (1024 * 1024 * 1024):.2f} GB"


@dataclass
class DownloadItem:
    """Represents a single download in the queue."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    url: str = ""
    title: str = "Unknown"
    duration: int = 0
    uploader: str = ""
    thumbnail_url: str = ""
    is_playlist: bool = False
    playlist_count: int = 0

    # Download options
    audio_only: bool = False
    quality: str = "best"
    ext: str = ""
    codec: str = ""
    audio_format: str = "mp3"
    audio_quality: str = "192"
    output_dir: str = ""
    filename_template: str = "%(title)s.%(ext)s"
    format_id: str = ""  # manual format selection from format browser

    # Subtitle options
    write_subs: bool = False
    embed_subs: bool = False
    subtitle_langs: str = "en"

    # Speed limit (bytes/sec, 0 = unlimited)
    speed_limit: int = 0

    # Cookie browser (empty = no cookies)
    cookie_browser: str = ""

    # SponsorBlock
    sponsorblock: bool = False

    # Runtime state
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    filesize: str = ""
    error_message: str = ""
    current_video_index: int = 0
    total_videos: int = 0
    current_video_title: str = ""

    # Timestamps
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    output_path: str = ""


def format_duration(seconds: Optional[int]) -> str:
    """Format seconds into a human-readable duration string."""
    if not seconds:
        return "Unknown"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_filesize(size_bytes: Optional[int]) -> str:
    """Format bytes into human-readable file size."""
    if not size_bytes:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.0f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_timestamp(ts: float) -> str:
    """Format a Unix timestamp into a readable date/time string."""
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
