# -*- coding: utf-8 -*-
# Hech qanday link yoki inline tugma yo'q — faqat matn orqali til tanlash

# Foydalanuvchi shu so'zlarni yozadi (katta/kichik harf farqi yo'q)
TIL_TUGMALARI = {
    "eng": "en",
    "en": "en",
    "1": "en",
    "rus": "ru",
    "ru": "ru",
    "2": "ru",
    "uz": "uz",
    "uzbek": "uz",
    "3": "uz",
    "lotin": "translit",
    "kiril": "translit",
    "translit": "translit",
    "4": "translit",
}


def til_tanlash_matni():
    """Til tanlash bo'yicha oddiy yo'riqnoma — tugma yo'q, faqat yozish."""
    return (
        "Tilni tanlang (quyidagilardan birini yozing):\n\n"
        "• ENG yoki 1 — Inglizcha\n"
        "• RUS yoki 2 — Ruscha\n"
        "• UZ yoki 3 — O'zbekcha\n"
        "• LOTIN yoki 4 — Kiril ↔ Lotin"
    )
