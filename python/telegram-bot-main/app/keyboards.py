from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def language_keyboard():
    keyboard = [
        [InlineKeyboardButton("🇬🇧 ENG", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 RUS", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇿 UZ", callback_data="lang_uz")],
        [InlineKeyboardButton("🔄 Kiril ↔ Lotin", callback_data="lang_translit")],
    ]
    return InlineKeyboardMarkup(keyboard)
