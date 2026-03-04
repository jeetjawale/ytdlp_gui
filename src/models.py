"""Data models for the YT-DLP GUI application."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
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
    audio_format: str = "mp3"
    audio_quality: str = "192"
    output_dir: str = ""

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


def format_timestamp(ts: float) -> str:
    """Format a Unix timestamp into a readable date/time string."""
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
