#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lovable buyurtmalar uchun Telegram bot (polling)
- Yangi buyurtma bo'lsa admin ga xabar va chek yuboradi
- Statistika har kun/hafta/oy admin ga yuboriladi
"""

import os
import asyncio
import logging
import aiohttp
from datetime import datetime, date
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import json

# Load .env
load_dotenv()


# .env fayldan token va id ni o'qish
BOT_TOKEN = os.getenv("token") or os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("id") or os.getenv("ADMIN_ID") or 0)
TZ = os.getenv("TZ", "Asia/Tashkent")
# Ganimadeb endpoint
LOVABLE_ORDERS_URL = "https://muhammad17.lovable.app/ganimadeb"

# Statistika uchun fayl
DATA_FILE = Path("lovable_orders.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== Statistika yordamchi ====================
def load_orders():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}

def save_orders(data):
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Save error: {e}")

def add_order(order):
    today = str(date.today())
    data = load_orders()
    if today not in data:
        data[today] = []
    data[today].append(order)
    save_orders(data)

def get_stats(period="day"):
    data = load_orders()
    now = date.today()
    result = []
    if period == "day":
        key = str(now)
        result = data.get(key, [])
    elif period == "week":
        for i in range(7):
            d = str(now)
            result += data.get(d, [])
            now = now.fromordinal(now.toordinal() - 1)
    elif period == "month":
        for k in data:
            if k[:7] == str(date.today())[:7]:
                result += data[k]
    return result

# ==================== Polling Lovable Orders ====================
async def fetch_orders():
    async with aiohttp.ClientSession() as session:
        async with session.get(LOVABLE_ORDERS_URL) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

async def fetch_check_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, "wb") as f:
                    f.write(await resp.read())
                return filename
    return None

async def notify_admin(order):
    # Xabar format
    text = (
        f"☕ <b>Yangi buyurtma!</b>\n"
        f"Mahsulot: <b>{order.get('mahsulot')}</b>\n"
        f"Narxi: <b>{order.get('narx')}</b> so'm\n"
        f"Vaqti: {order.get('vaqt')}\n"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    # Chek faylini yuborish (agar bo'lsa)
    if order.get('chek_url'):
        filename = f"chek_{order.get('id', 'unknown')}.pdf"
        file_path = await fetch_check_file(order['chek_url'], filename)
        if file_path:
            await bot.send_document(chat_id=ADMIN_ID, document=InputFile(file_path))
            os.remove(file_path)

async def poll_lovable():
    logger.info("Lovable buyurtmalarni polling boshladi...")
    last_ids = set()
    while True:
        try:
            orders = await fetch_orders()
            # Har bir buyurtma uchun id bo'lishi kerak
            new_orders = []
            for order in orders:
                oid = str(order.get('id'))
                if oid and oid not in last_ids:
                    new_orders.append(order)
                    last_ids.add(oid)
                    add_order(order)
            for order in new_orders:
                await notify_admin(order)
        except Exception as e:
            logger.error(f"Polling error: {e}")
        await asyncio.sleep(60)  # 1 daqiqada bir tekshiradi

# ==================== Statistika komandalar ====================
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return
    orders = get_stats("day")
    if not orders:
        await message.answer("📊 Bugun buyurtma yo'q")
        return
    text = "📊 <b>Bugungi buyurtmalar:</b>\n\n"
    for o in orders:
        text += f"• {o.get('mahsulot')} - {o.get('narx')} so'm\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("week"))
async def cmd_week(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return
    orders = get_stats("week")
    if not orders:
        await message.answer("📊 Bu hafta buyurtma yo'q")
        return
    text = "📊 <b>Haftalik buyurtmalar:</b>\n\n"
    for o in orders:
        text += f"• {o.get('mahsulot')} - {o.get('narx')} so'm\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("month"))
async def cmd_month(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return
    orders = get_stats("month")
    if not orders:
        await message.answer("📊 Bu oy buyurtma yo'q")
        return
    text = "📊 <b>Oylik buyurtmalar:</b>\n\n"
    for o in orders:
        text += f"• {o.get('mahsulot')} - {o.get('narx')} so'm\n"
    await message.answer(text, parse_mode="HTML")

# ==================== Botni ishga tushirish ====================
async def main():
    logger.info("Bot ishga tushdi!")
    asyncio.create_task(poll_lovable())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
