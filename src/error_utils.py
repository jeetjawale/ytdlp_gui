"""Helpers for classifying raw error strings into user-facing categories."""


def classify_error(raw: str) -> tuple[str, str]:
    text = raw.lower()
    if "ffmpeg" in text:
        return "ffmpeg", "FFmpeg is required for this operation."
    if "network" in text or "connection" in text or "name resolution" in text:
        return "network", "Network error occurred. Check your connection and try again."
    if "cookie" in text or "browser" in text:
        return "cookies", "Cookie import failed. Check the selected browser and try again."
    return "generic", raw
