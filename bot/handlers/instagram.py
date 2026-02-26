import re
import logging
from pathlib import Path

import yt_dlp
from aiogram import Router, F
from aiogram.types import Message

from bot.services.instagram_dl import download_instagram_media
from bot.utils.helpers import cleanup_files

logger = logging.getLogger(__name__)
router = Router()

INSTAGRAM_REGEX = r"(https?://)?(www\.)?instagram\.com/(p/|reel/|stories/)?[\w-]+"


@router.message(F.text.regexp(INSTAGRAM_REGEX))
async def handle_instagram_link(message: Message):
    url = message.text.strip()
    await message.answer("⏬ Скачиваю из Instagram...")

    try:
        result = await download_instagram_media(url)

        if not result:
            await message.answer("❌ Не удалось скачать контент")
            return

        files = result.get("files", [])
        title = result.get("title", "Instagram")

        if not files:
            await message.answer("❌ Не удалось найти медиафайлы")
            return

        if len(files) == 1:
            filepath = files[0]
            import os

            file_size = os.path.getsize(filepath)

            if file_size > 50 * 1024 * 1024:
                await message.answer(
                    f"📎 Файл слишком большой ({file_size // (1024 * 1024)}MB)\n"
                    f"Скачать: {filepath}"
                )
            else:
                if filepath.endswith((".jpg", ".jpeg", ".png")):
                    await message.answer_photo(
                        photo=open(filepath, "rb"), caption="✅ Загружено"
                    )
                else:
                    await message.answer_video(
                        video=open(filepath, "rb"), caption="✅ Загружено"
                    )
        else:
            media_group = []
            for f in files:
                if f.endswith((".jpg", ".jpeg", ".png")):
                    media_group.append({"type": "photo", "media": open(f, "rb")})
                else:
                    media_group.append({"type": "video", "media": open(f, "rb")})

            await message.answer_media_group(media_group)

        cleanup_files(*files)

    except Exception as e:
        logger.error(f"Instagram error: {e}")
        await message.answer("❌ Ошибка при скачивании из Instagram")
