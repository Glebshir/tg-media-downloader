import asyncio
import logging
import os
from typing import List, Dict, Optional

import yt_dlp
from bot.config import DOWNLOADS_DIR, YTDLP_COOKIEFILE

logger = logging.getLogger(__name__)

BASE_YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0",
    "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
}
if YTDLP_COOKIEFILE and os.path.isfile(YTDLP_COOKIEFILE):
    BASE_YDL_OPTS["cookiefile"] = YTDLP_COOKIEFILE


async def get_formats(url: str) -> List[Dict]:
    ydl_opts = {**BASE_YDL_OPTS, "format": "best"}

    loop = asyncio.get_event_loop()

    def _extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []

            if not info:
                return []

            seen_qualities = set()

            for f in info.get("formats", []):
                height = f.get("height")
                if height and height <= 1080:
                    quality = f"{height}p"
                    if quality not in seen_qualities:
                        seen_qualities.add(quality)
                        formats.append(
                            {
                                "format_id": f["format_id"],
                                "quality": quality,
                                "title": info.get("title", "Video"),
                            }
                        )

            audio_formats = [
                f
                for f in info.get("formats", [])
                if f.get("ext") == "m4a" and f.get("filesize")
            ]
            if audio_formats:
                formats.append(
                    {
                        "format_id": "bestaudio",
                        "quality": "🎵 Audio",
                        "title": info.get("title", "Video"),
                    }
                )

            return formats[:6]

    return await loop.run_in_executor(None, _extract)


async def download_video(
    url: str, format_id: str, quality: str = "best"
) -> Optional[str]:
    if format_id == "bestaudio":
        ydl_opts = {
            **BASE_YDL_OPTS,
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        }
    else:
        ydl_opts = {
            **BASE_YDL_OPTS,
            "format": f"{format_id}+bestaudio/best",
            "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    await loop.run_in_executor(None, _download)

    import glob

    files = glob.glob(f"{DOWNLOADS_DIR}/*")
    return files[0] if files else None
