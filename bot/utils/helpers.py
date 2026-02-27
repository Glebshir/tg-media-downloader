import re
import os
import glob
from urllib.parse import urlparse
from typing import Optional


URL_REGEX = r"(https?://[^\s]+|www\.[^\s]+)"
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
INSTAGRAM_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}


def is_youtube_url(text: str) -> bool:
    return extract_youtube_url(text) is not None


def is_instagram_url(text: str) -> bool:
    return extract_instagram_url(text) is not None


def _normalize_url(raw_url: str) -> str:
    return raw_url if raw_url.startswith(("http://", "https://")) else f"https://{raw_url}"


def _extract_first_url(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(URL_REGEX, text.strip())
    if not match:
        return None
    return _normalize_url(match.group(1).rstrip(").,]}>\"'"))


def extract_youtube_url(text: str) -> Optional[str]:
    url = _extract_first_url(text)
    if not url:
        return None

    host = urlparse(url).netloc.lower()
    if host in YOUTUBE_HOSTS:
        return url
    return None


def extract_instagram_url(text: str) -> Optional[str]:
    url = _extract_first_url(text)
    if not url:
        return None

    host = urlparse(url).netloc.lower()
    if host in INSTAGRAM_HOSTS:
        return url
    return None


def cleanup_files(*files):
    for filepath in files:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass


def get_downloads_dir():
    return "downloads"
