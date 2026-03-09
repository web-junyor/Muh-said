# -*- coding: utf-8 -*-
"""Bot tugmalari — asosiy menyu va inline tugmalar."""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Ketma-ketlik: Buyruqlar, Hamma buyruqlar, O'rgatish, Bot yop
MAIN_MENU_BUTTONS = [
    [KeyboardButton("📋 Buyruqlar"), KeyboardButton("📜 Hamma buyruqlar")],
    [KeyboardButton("📚 O'rgatish"), KeyboardButton("🔒 Bot yop")],
]
MAIN_MENU = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)


def kb_buyruqlar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Buyruqlar bajarish", callback_data="cmd_mode")],
        [InlineKeyboardButton("💬 Suhbatlashish", callback_data="chat_mode")],
    ])


def kb_orgatish():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Suhbatlashishni o'rgatish", callback_data="teach_chat")],
        [InlineKeyboardButton("➕ Buyruq qo'shish (och/yop)", callback_data="teach_cmd")],
    ])


def kb_bot_yop():
    """Bot yop bo'limida: faqat Bot yop tugmasi (parol so'rab qulflaydi)."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Bot yop", callback_data="bot_yop")],
    ])


def kb_suhbat():
    """Suhbat bo'limida: Bilim ol — faqat o'rgatilgan javoblar."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💡 Bilim ol", callback_data="chat_bilim_ol")],
    ])


def kb_cmd_row(cmd_id: int):
    """Bitta buyruq uchun: Buyruq tahrirlash, Buyruq o'chirish."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_cmd_{cmd_id}"),
            InlineKeyboardButton("🗑️ O'chirish", callback_data=f"del_cmd_{cmd_id}"),
        ],
    ])


def kb_builtin_cmd_row(index: int):
    """Standart (eski) buyruq uchun ham Tahrirlash / O'chirish tugmalari (bosilganda standart ekani aytiladi)."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_builtin_{index}"),
            InlineKeyboardButton("🗑️ O'chirish", callback_data=f"del_builtin_{index}"),
        ],
    ])
