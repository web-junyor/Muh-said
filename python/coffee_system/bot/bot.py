#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - Main Module
Loveble integratsiyasi bilan Coffee Shop Management Bot
"""

import logging
import asyncio
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID

from bot import handlers

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Handlerlarni ro'yxatga olish
dp.include_router(handlers.router)


async def notify_admin(message: str, parse_mode: str = "HTML"):
    """Admin foydalanuvchiga xabar berish"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_ID,
            text=message,
            parse_mode=parse_mode
        )
    except Exception as e:
        logger.error(f"Error sending message to admin: {e}")


async def start_bot():
    """Botni ishga tushirish"""
    try:
        logger.info("Starting Telegram Bot...")

        # Admin ga xabar berish
        await notify_admin(
            "✅ <b>Coffee Shop Bot ishga tushdi!</b>\n\n"
            "🔗 Loveble integratsiyasi faol\n"
            "📊 Kunlik, haftalik va oylik diagnostika sozlandi"
        )

        # Botni polling qilish
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()


async def stop_bot():
    """Botni to'xtatish"""
    try:
        from backend.scheduler import diagnostics_scheduler
        diagnostics_scheduler.shutdown()

        from backend.database import db
        db.close()

        logger.info("Bot stopped gracefully")
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")


async def setup_webhook():
    """Webhook o'rnatish (opsional - polling o'rniga)"""
    from config import WEBHOOK_URL, WEBHOOK_PATH
    try:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")


async def remove_webhook():
    """Webhookni o'chirish"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removed")
    except Exception as e:
        logger.error(f"Error removing webhook: {e}")


# Bot va Dispatcher export qilish
__all__ = ["bot", "dp", "start_bot", "stop_bot", "notify_admin", "setup_webhook", "remove_webhook"]
