# -*- coding: utf-8 -*-
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN
from handlers import start, handle_text


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Tarjimon bot ishga tushdi!!!. To'xtatish uchun Ctrl+C")
    app.run_polling()


if __name__ == "__main__":
    main()
