import re
import logging
from pathlib import Path

import yt_dlp
from aiogram import Router, F
from aiogram.types import (
    Message,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo,
)

from bot.services.instagram_dl import download_instagram_media
from bot.services.file_id_cache import FileIdCache
from bot.utils.helpers import extract_instagram_url, cleanup_files, instagram_cache_key
from bot.config import MAX_FILE_SIZE, FILE_ID_CACHE_SIZE

logger = logging.getLogger(__name__)
router = Router()
instagram_file_cache = FileIdCache(max_entries=FILE_ID_CACHE_SIZE)

@router.message(F.text.func(lambda text: bool(extract_instagram_url(text))))
async def handle_instagram_link(message: Message):
    url = extract_instagram_url(message.text or "")
    if not url:
        return

    cache_key = instagram_cache_key(url)
    cached_file_id = instagram_file_cache.get(cache_key)
    if cached_file_id:
        try:
            await message.answer_video(video=cached_file_id, caption="✅ Видео из кэша")
            return
        except Exception:
            instagram_file_cache.delete(cache_key)

    await message.answer("⏬ Скачиваю из Instagram...")

    try:
        result = await download_instagram_media(url)

        if not result:
            await message.answer("❌ Не удалось скачать контент")
            return
        if result.get("direct_url"):
            try:
                sent_message = await message.answer_video(
                    video=result["direct_url"], caption="✅ Загружено"
                )
                if sent_message.video:
                    instagram_file_cache.set(cache_key, sent_message.video.file_id)
                return
            except Exception:
                result = await download_instagram_media(url, use_preflight=False)
                if not result:
                    await message.answer("❌ Не удалось скачать контент")
                    return
        if result.get("error"):
            error_text = result.get("error", "").lower()
            if "login required" in error_text or "rate-limit" in error_text:
                await message.answer(
                    "❌ Instagram требует авторизацию. Добавьте cookies.txt "
                    "или INSTAGRAM_USERNAME/INSTAGRAM_PASSWORD."
                )
            else:
                await message.answer("❌ Ошибка при скачивании из Instagram")
            return

        files = result.get("files", [])
        if not files:
            await message.answer("❌ Не удалось найти медиафайлы")
            return

        if len(files) == 1:
            filepath = files[0]
            import os

            file_size = os.path.getsize(filepath)

            if file_size > MAX_FILE_SIZE:
                await message.answer(
                    f"📎 Файл слишком большой ({file_size // (1024 * 1024)}MB)\n"
                    f"Скачать: {filepath}"
                )
            else:
                if filepath.endswith((".jpg", ".jpeg", ".png")):
                    await message.answer_photo(
                        photo=FSInputFile(filepath), caption="✅ Загружено"
                    )
                else:
                    sent_message = await message.answer_video(
                        video=FSInputFile(filepath), caption="✅ Загружено"
                    )
                    if sent_message.video:
                        instagram_file_cache.set(cache_key, sent_message.video.file_id)
        else:
            media_group = []
            for f in files:
                if f.endswith((".jpg", ".jpeg", ".png")):
                    media_group.append(InputMediaPhoto(media=FSInputFile(f)))
                else:
                    media_group.append(InputMediaVideo(media=FSInputFile(f)))

            await message.answer_media_group(media_group)

        cleanup_files(*files)

    except Exception as e:
        logger.error(f"Instagram error: {e}")
        await message.answer("❌ Ошибка при скачивании из Instagram")
