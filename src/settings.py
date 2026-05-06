"""Application settings persistence using a JSON file."""

import json
import os
from typing import Any


class Settings:
    """Simple JSON-backed settings store."""

    def __init__(self, path: str = ""):
        config_dir = os.path.join(os.path.expanduser("~"), ".ytdlp_gui")
        self._path = path or os.path.join(config_dir, "settings.json")
        self._data: dict = {}
        self.last_error: str | None = None
        self._load()

    def _load(self):
        try:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            self.last_error = None
        except (json.JSONDecodeError, OSError) as exc:
            self._data = {}
            self.last_error = str(exc)

    def save(self):
        """Save settings to disk."""
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and persist to disk."""
        self._data[key] = value
        self.save()
