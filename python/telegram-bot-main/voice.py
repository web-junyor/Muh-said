# -*- coding: utf-8 -*-
from gtts import gTTS
import uuid
import os

# Ovoz fayllari uchun papka (Windows/Linux uchun)
VOICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_voice")


def text_to_voice(text: str, lang: str):
    """
    Matnni ovozga aylantiradi. Muvaffaqiyatda fayl yo'lini, xatoda None qaytaradi.
    """
    if not text or not str(text).strip():
        return None
    text = str(text).strip()
    # gTTS uchun juda uzun matnni qisqartirish (xato oldini olish)
    if len(text) > 3000:
        text = text[:3000]
    # gTTS qo'llab quvvatlaydigan tillar
    if lang not in ("en", "ru", "uz"):
        lang = "ru"
    if lang == "uz":
        lang = "ru"  # gTTS da o'zbekcha yo'q, ruscha ishlatamiz

    try:
        os.makedirs(VOICE_DIR, exist_ok=True)
        filename = os.path.join(VOICE_DIR, f"voice_{uuid.uuid4().hex}.mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        return filename
    except Exception:
        return None
