"""Helpers for serializing and retaining download history."""

import time


def download_item_to_history_entry(item) -> dict:
    return {
        "title": item.title,
        "url": item.url,
        "completed_at": item.completed_at or time.time(),
        "audio_only": item.audio_only,
        "audio_format": item.audio_format,
        "quality": item.quality,
        "output_dir": item.output_dir,
        "output_path": item.output_path,
        "status": item.status.value,
    }


def clamp_history(entries: list, limit: int = 200) -> list:
    return list(entries)[-limit:]
