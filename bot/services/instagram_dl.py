import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path

import yt_dlp
from bot.config import DOWNLOADS_DIR

logger = logging.getLogger(__name__)


async def download_instagram_media(url: str) -> Optional[Dict]:
    ydl_opts = {
        "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "format": "best",
    }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    try:
        info = await loop.run_in_executor(None, _download)

        if not info:
            return None

        import glob

        files = glob.glob(f"{DOWNLOADS_DIR}/*")
        files = [f for f in files if Path(f).stat().st_size > 0]

        return {
            "files": files,
            "title": info.get("title", "Instagram"),
            "type": info.get("type", "video"),
        }

    except Exception as e:
        logger.error(f"Instagram download error: {e}")
        return None
