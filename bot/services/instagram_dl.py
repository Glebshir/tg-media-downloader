import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
import os
import re

import requests
import yt_dlp
from bot.config import (
    DOWNLOADS_DIR,
    YTDLP_COOKIEFILE,
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    INSTAGRAM_USER_AGENT,
    INSTAGRAM_X_IG_APP_ID,
    INSTAGRAM_COOKIES,
)

logger = logging.getLogger(__name__)


def _parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    if not cookie_string:
        return cookies
    for chunk in cookie_string.split(";"):
        item = chunk.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        if key:
            cookies[key] = value.strip()
    return cookies


def _extract_shortcode(url: str) -> Optional[str]:
    match = re.search(
        r"instagram\.com/(?:[A-Za-z0-9_.]+/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)",
        url,
    )
    if match:
        return match.group(1)
    return None


def _extract_video_url_from_json(payload: Dict) -> Optional[str]:
    items = payload.get("items")
    if isinstance(items, list) and items:
        versions = items[0].get("video_versions")
        if isinstance(versions, list) and versions:
            url = versions[0].get("url")
            if isinstance(url, str) and url:
                return url

    graphql_media = payload.get("graphql", {}).get("shortcode_media", {})
    gql_video_url = graphql_media.get("video_url")
    if isinstance(gql_video_url, str) and gql_video_url:
        return gql_video_url

    xdt_media = payload.get("data", {}).get("xdt_shortcode_media", {})
    xdt_video_url = xdt_media.get("video_url")
    if isinstance(xdt_video_url, str) and xdt_video_url:
        return xdt_video_url

    return None


def _preflight_instagram_video_url(url: str) -> Optional[str]:
    headers = {
        "User-Agent": INSTAGRAM_USER_AGENT
        or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.instagram.com/",
    }
    if INSTAGRAM_X_IG_APP_ID:
        headers["X-IG-App-ID"] = INSTAGRAM_X_IG_APP_ID

    cookies = _parse_cookie_string(INSTAGRAM_COOKIES)
    shortcode = _extract_shortcode(url)

    candidates = [url.rstrip("/")]
    if shortcode:
        candidates.extend(
            [
                f"https://www.instagram.com/p/{shortcode}",
                f"https://www.instagram.com/reel/{shortcode}",
            ]
        )

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)

        try:
            response = requests.get(
                candidate,
                params={"__a": "1", "__d": "dis"},
                headers=headers,
                cookies=cookies,
                timeout=15,
            )
            if response.status_code >= 400:
                continue
            payload = response.json()
            video_url = _extract_video_url_from_json(payload)
            if video_url:
                return video_url
        except Exception:
            continue

    return None


async def download_instagram_media(url: str, use_preflight: bool = True) -> Optional[Dict]:
    if use_preflight:
        loop = asyncio.get_event_loop()
        direct_url = await loop.run_in_executor(None, _preflight_instagram_video_url, url)
        if direct_url:
            return {
                "direct_url": direct_url,
                "files": [],
                "title": "Instagram",
                "type": "video",
            }

    ydl_opts = {
        "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "source_address": "0.0.0.0",
    }
    if YTDLP_COOKIEFILE and os.path.isfile(YTDLP_COOKIEFILE):
        ydl_opts["cookiefile"] = YTDLP_COOKIEFILE
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        ydl_opts["username"] = INSTAGRAM_USERNAME
        ydl_opts["password"] = INSTAGRAM_PASSWORD

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
        return {"error": str(e), "files": []}
