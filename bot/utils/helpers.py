import re
import os
import glob
from urllib.parse import urlparse, parse_qs
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


def youtube_cache_key(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    video_id = None
    if host == "youtu.be" and path:
        video_id = path.split("/")[0]
    elif host in YOUTUBE_HOSTS:
        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = path.split("/")
            if parts and parts[0] in {"shorts", "embed", "live"} and len(parts) > 1:
                video_id = parts[1]

    if video_id:
        return f"yt:{video_id}"

    normalized = f"{parsed.scheme}://{host}/{path}".rstrip("/")
    return f"yt:{normalized}"


def instagram_cache_key(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = [p for p in path.split("/") if p]

    if parts:
        if parts[0] in {"p", "reel", "reels", "tv", "stories"} and len(parts) > 1:
            return f"ig:{parts[1]}"
        if len(parts) > 2 and parts[1] in {"p", "reel", "reels", "tv", "stories"}:
            return f"ig:{parts[2]}"

    host = parsed.netloc.lower()
    normalized = f"{parsed.scheme}://{host}/{path}".rstrip("/")
    return f"ig:{normalized}"


def cleanup_files(*files):
    for filepath in files:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass


def get_downloads_dir():
    return "downloads"
