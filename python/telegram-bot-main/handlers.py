# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes
import os

from keyboards import til_tanlash_matni, TIL_TUGMALARI
from services import kiril_lotin, translate_text
from voice import text_to_voice


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lang"] = None
    await update.message.reply_text(
        "Salom! Tarjimon bot.\n\n" + til_tanlash_matni()
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    text_lower = text.lower()

    # Til tanlash — faqat matn (ENG, RUS, 1, 2, ...), hech qanday link/tugma yo'q
    if text_lower in TIL_TUGMALARI:
        lang = TIL_TUGMALARI[text_lower]
        context.user_data["lang"] = lang
        til_nomi = {"en": "Ingliz", "ru": "Rus", "uz": "O'zbek", "translit": "Kiril ↔ Lotin"}.get(lang, lang)
        await update.message.reply_text(
            f"✅ Tanlandi: {til_nomi}\n\nEndi tarjima qilmoqchi bo'lgan matnni yuboring."
        )
        return

    # Til tanlanmagan bo'lsa
    lang = context.user_data.get("lang")
    if not lang:
        await update.message.reply_text(
            "Iltimos, avval tilni tanlang.\n\n" + til_tanlash_matni()
        )
        return

    # Bo'sh xabar
    if not text:
        await update.message.reply_text("Matn yuboring, tarjima qilaman.")
        return

    # Tarjima / translit
    if lang == "translit":
        result = kiril_lotin(text)
        voice_lang = "ru"
    else:
        result = translate_text(text, lang)
        voice_lang = "ru" if lang == "uz" else lang

    await update.message.reply_text(result)

    voice_file = text_to_voice(result, voice_lang)
    if voice_file and os.path.exists(voice_file):
        try:
            with open(voice_file, "rb") as audio:
                await update.message.reply_voice(audio)
        finally:
            try:
                os.remove(voice_file)
            except Exception:
                pass
