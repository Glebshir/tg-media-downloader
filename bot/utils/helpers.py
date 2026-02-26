import re
import os
import glob
from typing import List


YOUTUBE_REGEX = (
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|shorts/)?[\w-]+"
)
INSTAGRAM_REGEX = r"(https?://)?(www\.)?instagram\.com/(p/|reel/|stories/)?[\w-]+"


def is_youtube_url(text: str) -> bool:
    return bool(re.match(YOUTUBE_REGEX, text))


def is_instagram_url(text: str) -> bool:
    return bool(re.match(INSTAGRAM_REGEX, text))


def cleanup_files(*files):
    for filepath in files:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass


def get_downloads_dir():
    return "downloads"
