#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot Handlers for Sales Notifications and Diagnostics
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    TELEGRAM_ADMIN_ID,
    PRODUCTS,
    LOW_STOCK_THRESHOLD,
    CRITICAL_STOCK_THRESHOLD,
    MESSAGES
)
from backend.database import db
from backend.models import Sale
from backend.loveble_api import loveble_client

logger = logging.getLogger(__name__)

# Router yaratish
router = Router()


class AdminStates(StatesGroup):
    """Bot adminining holatlari"""
    waiting_for_product = State()
    waiting_for_quantity = State()
    waiting_for_manual_sale = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasini qayta ishlash"""
    user_id = message.from_user.id

    # Faqat admin uchun
    if user_id != TELEGRAM_ADMIN_ID:
        await message.answer("❌ Siz ushbu botdan foydalanish huquqiga ega emassiz!")
        return

    await state.clear()

    welcome_text = """
👋 Assalomu alekum! Coffee Shop Management Bot ishga tushdi!

🤖 Bot quyidagilar bilan ishleydi:
1️⃣ Loveble integratsiyasi orqali sotuvlarni avtomatik qaydda olish
2️⃣ Har kuni 23:00 da kunlik diagnostika
3️⃣ Juma kuni haftalik hisobot
4️⃣ Oyning 1-quni oylik hisobot
5️⃣ Kam qoldig'i mahsulotlar haqida ogohlantirma

📊 Bugungi savdo statistikasi:
"""

    # Bugungi sotuvlar
    from datetime import date
    today_sales = db.get_sales_by_date(date.today())
    total_revenue = sum(sale.total_price for sale in today_sales)

    welcome_text += f"""
• Jami sotuvlar: {len(today_sales)} ta
• Jami daromad: {total_revenue} som

📦 Qoldig'i ma'lumoti:
"""

    stock_levels = db.get_all_stock_levels()
    for product_name, quantity in stock_levels.items():
        welcome_text += f"\n• {product_name}: {quantity} dona"

    # Inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Kunlik Hisobot", callback_data="daily_report")],
        [InlineKeyboardButton(text="📈 Haftalik Hisobot", callback_data="weekly_report")],
        [InlineKeyboardButton(text="📅 Oylik Hisobot", callback_data="monthly_report")],
        [InlineKeyboardButton(text="📦 Qoldig'i", callback_data="stock_status")],
        [InlineKeyboardButton(text="⚠️ Kam Qoldig'i", callback_data="low_stock")],
        [InlineKeyboardButton(text="🆘 Yordamga", callback_data="help")],
    ])

    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "daily_report")
async def show_daily_report(query: CallbackQuery):
    """Kunlik hisobotni ko'rsatish"""
    user_id = query.from_user.id

    if user_id != TELEGRAM_ADMIN_ID:
        await query.answer("❌ Sizning huquqingiz yo'q!", show_alert=True)
        return

    from datetime import date
    today_sales = db.get_sales_by_date(date.today())
    stock_levels = db.get_all_stock_levels()
    low_stock = db.get_low_stock_products(LOW_STOCK_THRESHOLD)

    total_sales = len(today_sales)
    total_revenue = sum(sale.total_price for sale in today_sales)

    products_sold = {}
    for sale in today_sales:
        if sale.product_name not in products_sold:
            products_sold[sale.product_name] = 0
        products_sold[sale.product_name] += sale.quantity

    report_text = f"""
📊 <b>KUNLIK DIAGNOSTIKA - {date.today().strftime('%d.%m.%Y')}</b>

📈 <b>Umumiy ma'lumot:</b>
• Sotuvlar soni: {total_sales} ta
• Jami daromad: {total_revenue:,} som

🛍️ <b>Sotilgan mahsulotlar:</b>
"""

    if products_sold:
        for product_name, quantity in products_sold.items():
            product = db.get_product(product_name)
            if product:
                report_text += f"\n• {product_name}: {quantity} dona ({quantity * product.price:,} som)"
    else:
        report_text += "\nBugun sotuvlar yo'q"

    report_text += f"\n\n📦 <b>Qoldig'i holatı:</b>\n"
    for product_name, quantity in stock_levels.items():
        icon = "⚠️" if quantity <= LOW_STOCK_THRESHOLD else "✅"
        report_text += f"{icon} {product_name}: {quantity} dona\n"

    if low_stock:
        report_text += f"\n🚨 <b>Kam qoldig'i mahsulotlar:</b>\n"
        for product_name in low_stock:
            quantity = stock_levels.get(product_name, 0)
            report_text += f"• {product_name}: {quantity} dona\n"

    await query.message.answer(report_text, parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "stock_status")
async def show_stock_status(query: CallbackQuery):
    """Qoldig'i holatini ko'rsatish"""
    user_id = query.from_user.id

    if user_id != TELEGRAM_ADMIN_ID:
        await query.answer("❌ Sizning huquqingiz yo'q!", show_alert=True)
        return

    stock_levels = db.get_all_stock_levels()

    status_text = "📦 <b>QOLDIG'I HOLATI</b>\n\n"

    total_items = 0
    low_items = 0

    for product_name, quantity in sorted(stock_levels.items()):
        total_items += quantity

        if quantity <= CRITICAL_STOCK_THRESHOLD:
            icon = "🔴"
            low_items += quantity
        elif quantity <= LOW_STOCK_THRESHOLD:
            icon = "🟡"
            low_items += quantity
        else:
            icon = "🟢"

        initial = 12
        percentage = (quantity / initial) * 100
        status_text += f"{icon} <b>{product_name}</b>: {quantity}/{initial} ({percentage:.0f}%)\n"

    status_text += f"\n📊 Jami: {total_items}/96 dona"

    if low_items > 0:
        status_text += f"\n⚠️ Kam qoldig'i: {low_items} dona"

    await query.message.answer(status_text, parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "low_stock")
async def show_low_stock(query: CallbackQuery):
    """Kam qoldig'i mahsulotlarni ko'rsatish"""
    user_id = query.from_user.id

    if user_id != TELEGRAM_ADMIN_ID:
        await query.answer("❌ Sizning huquqingiz yo'q!", show_alert=True)
        return

    low_stock = db.get_low_stock_products(LOW_STOCK_THRESHOLD)
    stock_levels = db.get_all_stock_levels()

    if not low_stock:
        await query.message.answer("✅ Barcha mahsulotlar etarli miqdorda mavjud!")
        await query.answer()
        return

    alert_text = "⚠️ <b>KAM QOLDIG'I MAHSULOTLAR</b>\n\n"

    for product_name in low_stock:
        quantity = stock_levels.get(product_name, 0)

        if quantity <= CRITICAL_STOCK_THRESHOLD:
            alert_text += f"🚨 <b>{product_name}: {quantity} dona</b> - KRITIK!\n"
        else:
            alert_text += f"⚠️ <b>{product_name}: {quantity} dona</b>\n"

    await query.message.answer(alert_text, parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "help")
async def show_help(query: CallbackQuery):
    """Yordamni ko'rsatish"""
    help_text = """
🆘 <b>YORDAMGA</b>

<b>Bot imkoniyatlari:</b>

1️⃣ <b>Avtomatik Loveble integratsiyasi</b>
   - Mahsulot sotilsa, bot avtomatik qaydda oladi
   - Mahsulot nomi va chekni yuboradi

2️⃣ <b>Kunlik Diagnostika (23:00)</b>
   - Shu kungi sotuvlar statistikasi
   - Qoldig'i holatı
   - Kam qoldig'i mahsulotlar

3️⃣ <b>Haftalik Hisobot (Juma 23:05)</b>
   - Hafta davomida jami sotuvlar
   - Eng ko'p sotilgan mahsulot
   - Eng kam sotilgan mahsulot

4️⃣ <b>Oylik Hisobot (1-quni 23:10)</b>
   - Oy davomida jami sotuvlar va daromad
   - Eng foydali mahsulot
   - O'zgarish foizi

<b>Ma'lumot:</b>
• 🟢 Yashil: Etarli qoldig'i
• 🟡 Sariq: Kam qoldig'i ({LOW_STOCK_THRESHOLD} ta yoki kamroq)
• 🔴 Qizil: Kritik ({CRITICAL_STOCK_THRESHOLD} ta yoki kamroq)
"""

    await query.message.answer(help_text, parse_mode="HTML")
    await query.answer()


async def send_sale_notification(sale: Sale):
    """Sotuvlar haqida xabar berish"""
    try:
        notification_text = f"""
🛍️ <b>YANGI SOTUVLAR</b>

📦 Mahsulot: <b>{sale.product_name}</b>
📊 Miqdori: <b>{sale.quantity}</b> dona
💰 Narxi: <b>{sale.total_price:,}</b> som
🧾 Chek ID: <code>{sale.check_id}</code>
⏰ Vaqt: {datetime.now().strftime('%H:%M:%S')}

📉 Qoldig'i: <b>{db.get_stock_level(sale.product_name)} dona</b>
"""

        # Cam qoldig'i haqida ogohlantirishni tekshirish
        remaining = db.get_stock_level(sale.product_name)
        if remaining is not None and remaining <= CRITICAL_STOCK_THRESHOLD:
            notification_text += f"\n🚨 <b>KRITIK: {sale.product_name} atigi {remaining} dona qoldi!</b>"
        elif remaining is not None and remaining <= LOW_STOCK_THRESHOLD:
            notification_text += f"\n⚠️ <b>OGOHLANTIRMA: {sale.product_name} {remaining} dona qoldi!</b>"

        from bot.bot import bot
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_ID,
            text=notification_text,
            parse_mode="HTML"
        )

        logger.info(f"Sale notification sent for {sale.product_name}")

    except Exception as e:
        logger.error(f"Error sending sale notification: {e}")


async def send_diagnostic_report(report_type: str, report_data: Dict):
    """Diagnostika hisobotini yuborish"""
    try:
        if report_type == "daily":
            report_text = format_daily_report(report_data)
        elif report_type == "weekly":
            report_text = format_weekly_report(report_data)
        elif report_type == "monthly":
            report_text = format_monthly_report(report_data)
        else:
            return

        from bot.bot import bot
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_ID,
            text=report_text,
            parse_mode="HTML"
        )

        logger.info(f"Diagnostic report sent: {report_type}")

    except Exception as e:
        logger.error(f"Error sending diagnostic report: {e}")


def format_daily_report(report: Dict) -> str:
    """Kunlik hisobotni formatlash"""
    date_str = report.get("date", "N/A")
    total_sales = report.get("total_sales", 0)
    total_revenue = report.get("total_revenue", 0)
    products_sold = report.get("products_sold", {})
    stock_levels = report.get("stock_levels", {})
    low_stock_products = report.get("low_stock_products", [])

    text = f"""
📊 <b>KUNLIK DIAGNOSTIKA</b>
📅 Sana: <b>{date_str}</b>

📈 <b>Umumiy:</b>
• Jami sotuvlar: {total_sales} ta
• Jami daromad: {total_revenue:,} som

🛍️ <b>Sotilgan mahsulotlar:</b>
"""

    if products_sold:
        for product_name, quantity in products_sold.items():
            text += f"\n• {product_name}: {quantity} dona"
    else:
        text += "\n• Sotuvlar yo'q"

    text += f"\n\n📦 <b>Qoldig'i:</b>\n"
    for product_name in sorted(stock_levels.keys()):
        quantity = stock_levels[product_name]
        icon = "⚠️" if quantity <= LOW_STOCK_THRESHOLD else "✅"
        text += f"{icon} {product_name}: {quantity} dona\n"

    if low_stock_products:
        text += f"\n🚨 <b>Kam qoldig'i:</b>\n"
        for product_name in low_stock_products:
            text += f"• {product_name}\n"

    return text


def format_weekly_report(report: Dict) -> str:
    """Haftalik hisobotni formatlash"""
    week = report.get("week_number", "N/A")
    year = report.get("year", "N/A")
    total_sales = report.get("total_sales", 0)
    total_revenue = report.get("total_revenue", 0)
    best_selling = report.get("best_selling_product", "N/A")
    worst_selling = report.get("worst_selling_product", "N/A")
    average_daily = report.get("average_daily_sales", 0)

    text = f"""
📈 <b>HAFTALIK HISOBOT</b>
📅 Haftasi: <b>{week}/{year}</b>

📊 <b>Umumiy:</b>
• Jami sotuvlar: {total_sales} ta
• Jami daromad: {total_revenue:,} som
• O'rtacha kunlik: {average_daily:.1f} dona

🏆 <b>Eng ko'p sotilgan:</b> {best_selling}
📉 <b>Eng kam sotilgan:</b> {worst_selling}
"""

    return text


def format_monthly_report(report: Dict) -> str:
    """Oylik hisobotni formatlash"""
    month = report.get("month", "N/A")
    year = report.get("year", "N/A")
    total_sales = report.get("total_sales", 0)
    total_revenue = report.get("total_revenue", 0)
    best_selling = report.get("best_selling_product", "N/A")
    most_profitable = report.get("most_profitable_product", "N/A")
    average_daily = report.get("average_daily_sales", 0)

    month_names = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avqust", 9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    month_name = month_names.get(month, str(month))

    text = f"""
📅 <b>OYLIK HISOBOT</b>
📆 Oyi: <b>{month_name} {year}</b>

📊 <b>Umumiy:</b>
• Jami sotuvlar: {total_sales} ta
• Jami daromad: {total_revenue:,} som
• O'rtacha kunlik: {average_daily:.1f} dona

🏆 <b>Eng ko'p sotilgan:</b> {best_selling}
💰 <b>Eng foydali:</b> {most_profitable}
"""

    return text
