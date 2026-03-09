# -*- coding: utf-8 -*-
"""Jarvis Telegram bot — ishga tushirish.
   Terminal: cd jarvis/telegram_bot && python main.py
   Birinchi parol so'raladi (sukurt: 197o), keyin bot ishga tushadi.
"""
import sys
import getpass
from pathlib import Path

# Terminal qulfi: parol to'g'ri bo'lsagina bot ishga tushadi
def _check_terminal_password():
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)
    import os
    expected = os.getenv("JARVIS_BOT_PASSWORD", "197o").strip()
    try:
        p = getpass.getpass("Parol: ")
        if p.strip() != expected:
            print("Parol noto'g'ri. Dastur to'xtatildi.")
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nBekor qilindi.")
        sys.exit(1)


from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.request import HTTPXRequest

from config import BOT_TOKEN
from handlers import start, handle_text, handle_callback

# Telegram API ga ulanish vaqtini oshirish (sekin tarmoq yoki bloklangan muhitda)
REQUEST = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0)


async def _error_handler(update, context):
    """Xatolik yuz berganda bot to'xtab qolmasin, foydalanuvchiga xabar yuboriladi."""
    import logging
    logging.exception("Handler xatosi")
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text("❌ Ichki xato. Qayta urinib ko'ring.")
        except Exception:
            pass


def main():
    _check_terminal_password()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(REQUEST)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(_error_handler)

    print("Jarvis Telegram bot ishga tushmoqda... (Telegram API ga ulanish)")
    print("To'xtatish: Ctrl+C")
    # Ulanish muvaffaqiyatsiz bo'lsa 5 marta qayta urinadi
    app.run_polling(bootstrap_retries=5, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
