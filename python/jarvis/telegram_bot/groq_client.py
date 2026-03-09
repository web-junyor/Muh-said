# -*- coding: utf-8 -*-
"""Groq orqali Jarvis javobini olish. Kerak: pip install groq.
   Eslatma: get_jarvis_reply chaqilganda user_text va history Groq API ga yuboriladi (tashqi server).
   Ma'lumot chiqmasin deyilsa: config da JARVIS_GROQ_ALLOWED=false qiling."""
from groq import Groq  # type: ignore[import-untyped]

from config import GROQ_API_KEY
from prompt import JARVIS_SYSTEM_PROMPT

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10  # oxirgi shuncha xabar kontekstga kiritiladi


def get_jarvis_reply(user_text: str, history: list[dict]) -> str:
    """
    Foydalanuvchi matni va tarix bo'yicha Jarvis javobini qaytaradi.
    Ma'lumot Groq (tashqi) serveriga yuboriladi. Tashqariga yuborishni o'chirish: JARVIS_GROQ_ALLOWED=false
    history: [{"role": "user"|"assistant", "content": "..."}, ...]
    """
    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=1024,
    )
    return (completion.choices[0].message.content or "").strip()
