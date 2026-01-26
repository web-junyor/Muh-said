from telegram import Update
from telegram.ext import ContextTypes
from app.keyboards import language_keyboard
from app.services import kiril_lotin, fake_translate
from app.voice import text_to_voice
import os


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tilni tanlang 👇",
        reply_markup=language_keyboard()
    )


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang

    await query.edit_message_text(
        f"Tanlandi: {lang.upper()}\nEndi matn yuboring."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang")

    if not lang:
        await update.message.reply_text("Iltimos, avval tilni tanlang (/start).")
        return

    text = update.message.text

    if lang == "translit":
        result = kiril_lotin(text)
        voice_lang = "ru"
    else:
        result = fake_translate(text, lang)
        voice_lang = lang

    await update.message.reply_text(result)

    voice_file = text_to_voice(result, voice_lang)
    with open(voice_file, "rb") as audio:
        await update.message.reply_voice(audio)

    os.remove(voice_file)
