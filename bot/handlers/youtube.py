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
    FSInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.services.youtube_dl import get_formats, download_video
from bot.utils.helpers import extract_youtube_url, cleanup_files
from bot.config import MAX_FILE_SIZE

logger = logging.getLogger(__name__)
router = Router()

class YouTubeStates(StatesGroup):
    waiting_for_quality = State()


@router.message(F.text.func(lambda text: bool(extract_youtube_url(text))))
async def handle_youtube_link(message: Message, state: FSMContext):
    url = extract_youtube_url(message.text or "")
    if not url:
        return

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
        await state.update_data(url=url)

    except Exception as e:
        logger.error(f"YouTube error: {e}")
        await message.answer("❌ Ошибка при получении информации о видео")


@router.callback_query(F.data.startswith("yt_"))
async def process_youtube_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("⏬ Скачиваю видео...")

    format_id = callback.data.replace("yt_", "")
    state_data = await state.get_data()
    url = state_data.get("url")

    if not url:
        await callback.message.answer("❌ Не удалось получить ссылку на видео")
        await callback.answer()
        return

    try:
        filepath = await download_video(url, format_id)

        if not filepath:
            await callback.message.answer("❌ Ошибка при скачивании видео")
            return

        import os

        file_size = os.path.getsize(filepath)

        if file_size > MAX_FILE_SIZE:
            await callback.message.answer(
                f"📎 Файл слишком большой ({file_size // (1024 * 1024)}MB)\n"
                f"Скачать можно по ссылке: {filepath}"
            )
        else:
            await callback.message.answer_video(
                video=FSInputFile(filepath), caption="✅ Видео загружено"
            )

        cleanup_files(filepath)
        await state.clear()

    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        await callback.message.answer("❌ Ошибка при скачивании видео")

    await callback.answer()
