import re
import logging
from typing import Optional

import yt_dlp
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.services.youtube_dl import get_formats, download_video
from bot.utils.helpers import is_youtube_url, is_instagram_url, cleanup_files

logger = logging.getLogger(__name__)
router = Router()

YOUTUBE_REGEX = (
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|shorts/)?[\w-]+"
)


class YouTubeStates(StatesGroup):
    waiting_for_quality = State()


@router.message(F.text.regexp(YOUTUBE_REGEX))
async def handle_youtube_link(message: Message, state: FSMContext):
    url = message.text.strip()
    await message.answer("🔍 Получаю информацию о видео...")

    try:
        formats = await get_formats(url)

        if not formats:
            await message.answer("❌ Не удалось получить информацию о видео")
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"🎬 {fmt['quality']}",
                        callback_data=f"yt_{fmt['format_id']}",
                    )
                ]
                for fmt in formats[:6]
            ]
        )

        await message.answer(
            f"📹 <b>{formats[0].get('title', 'YouTube Video')}</b>\n\nВыберите качество:",
            reply_markup=keyboard,
        )
        await state.set_state(YouTubeStates.waiting_for_quality)

    except Exception as e:
        logger.error(f"YouTube error: {e}")
        await message.answer("❌ Ошибка при получении информации о видео")


@router.callback_query(F.data.startswith("yt_"))
async def process_youtube_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("⏬ Скачиваю видео...")

    format_id = callback.data.replace("yt_", "")
    url = callback.message.text.split("\n")[0].replace("📹 <b>", "").replace("</b>", "")

    try:
        filepath = await download_video(url, format_id)

        if not filepath:
            await callback.message.answer("❌ Ошибка при скачивании видео")
            return

        import os

        file_size = os.path.getsize(filepath)

        if file_size > 50 * 1024 * 1024:
            await callback.message.answer(
                f"📎 Файл слишком большой ({file_size // (1024 * 1024)}MB)\n"
                f"Скачать можно по ссылке: {filepath}"
            )
        else:
            await callback.message.answer_video(
                video=open(filepath, "rb"), caption="✅ Видео загружено"
            )

        cleanup_files(filepath)

    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        await callback.message.answer("❌ Ошибка при скачивании видео")

    await callback.answer()
