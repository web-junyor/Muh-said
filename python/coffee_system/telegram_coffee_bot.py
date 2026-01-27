#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Telegram Coffee Shop Bot
Admin controls sales directly via bot commands
"""

import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from pytz import timezone

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TZ = timezone("Asia/Tashkent")

# Data storage
DATA_FILE = Path("coffee_data.json")


# FSM States
class SaleForm(StatesGroup):
    waiting_product = State()
    waiting_quantity = State()
    waiting_price = State()


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ==================== Data Management ====================
def load_data():
    """Load sales data from JSON file."""
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}


def save_data(data):
    """Save sales data to JSON file."""
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Save error: {e}")


def add_sale(product_name: str, quantity: int, price: int) -> str:
    """Add sale record."""
    try:
        today = str(date.today())
        data = load_data()

        if today not in data:
            data[today] = {"sales": [], "total": 0, "products": {}}

        # Add to sales list
        sale = {
            "product": product_name,
            "quantity": quantity,
            "price": price,
            "time": datetime.now(TZ).strftime("%H:%M:%S")
        }
        data[today]["sales"].append(sale)
        data[today]["total"] += price

        # Update product count
        if product_name not in data[today]["products"]:
            data[today]["products"][product_name] = 0
        data[today]["products"][product_name] += quantity

        save_data(data)

        return f"✅ {product_name} x{quantity} - {price:,} so'm qo'shildi"
    except Exception as e:
        logger.error(f"Add sale error: {e}")
        return f"❌ Xato: {e}"


def get_today_stats() -> str:
    """Get today's statistics."""
    today = str(date.today())
    data = load_data()

    if today not in data or not data[today]["sales"]:
        return "📊 Bugun sotilgan mahsulot yo'q"

    stats = data[today]
    message = f"📊 <b>BUG'UNGI STATISTIKA</b>\n\n"

    for product, qty in stats["products"].items():
        message += f"• {product}: {qty} ta\n"

    message += f"\n💰 <b>Jami:</b> {stats['total']:,} so'm"
    return message


# ==================== Keyboards ====================
def main_keyboard():
    """Main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☕ Sotilgan mahsulot")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="❓ Yordam")],
        ],
        resize_keyboard=True
    )


def quick_sales_keyboard():
    """Quick sales buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="☕ Qahva Latte"),
                KeyboardButton(text="🍵 Choy"),
            ],
            [
                KeyboardButton(text="🥤 Cappuccino"),
                KeyboardButton(text="☕ Americano"),
            ],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True
    )


# ==================== Handlers ====================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Sizning ruxsatingiz yo'q")
        return

    await message.answer(
        "☕ <b>Qahva Shop Bot</b>\n\n"
        "Admin panel ta'yyorlangan. Quyidagi buyruqlarni ishlatish mumkin:\n\n"
        "📌 <b>Buyruqlar:</b>\n"
        "/add - Sotilgan mahsulot qo'shish\n"
        "/stats - Bugungi statistika\n"
        "/all_stats - Barcha statistika\n"
        "/help - Yordam\n\n"
        "Yoki pastdagi tugmalardan foydalanish mumkin.",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text == "☕ Sotilgan mahsulot")
async def quick_add(message: types.Message):
    """Quick add menu."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    await message.answer(
        "☕ Mahsulot tanlang va miqdorni yozing\n"
        "Misol: Qahva Latte 2",
        reply_markup=quick_sales_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    """Add sale form."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    await state.set_state(SaleForm.waiting_product)
    await message.answer(
        "☕ Mahsulot nomini yozing:\n"
        "(Misol: Qahva Latte, Cappuccino, Choy...)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Qahva Latte")],
                [KeyboardButton(text="Cappuccino")],
                [KeyboardButton(text="Americano")],
                [KeyboardButton(text="Choy")],
            ],
            resize_keyboard=True
        )
    )


@dp.message(SaleForm.waiting_product)
async def process_product(message: types.Message, state: FSMContext):
    """Process product name."""
    await state.update_data(product=message.text)
    await state.set_state(SaleForm.waiting_quantity)
    await message.answer("📊 Miqdorni yozing (dona):")


@dp.message(SaleForm.waiting_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    """Process quantity."""
    try:
        qty = int(message.text)
        await state.update_data(quantity=qty)
        await state.set_state(SaleForm.waiting_price)
        await message.answer("💰 Narxni yozing (so'm):")
    except ValueError:
        await message.answer("❌ Raqam yozing!")


@dp.message(SaleForm.waiting_price)
async def process_price(message: types.Message, state: FSMContext):
    """Process price and save."""
    try:
        price = int(message.text)
        data = await state.get_data()

        result = add_sale(data["product"], data["quantity"], price)

        # Send confirmation
        current_time = datetime.now(TZ).strftime("%H:%M")
        notification = (
            f"☕ QAHVA SOTILDI!\n\n"
            f"<b>{data['product']}</b> - {data['quantity']} dona\n"
            f"Summa: {price:,} so'm\n"
            f"Vaqti: {current_time}"
        )

        await message.answer(result, reply_markup=main_keyboard())
        await message.answer(notification, parse_mode="HTML")

        await state.clear()
    except ValueError:
        await message.answer("❌ Raqam yozing!")


@dp.message(F.text == "📊 Statistika")
async def cmd_stats(message: types.Message):
    """Show today's stats."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    stats = get_today_stats()
    await message.answer(stats, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(Command("stats"))
async def cmd_stats_command(message: types.Message):
    """Show today's stats."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    stats = get_today_stats()
    await message.answer(stats, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(Command("all_stats"))
async def cmd_all_stats(message: types.Message):
    """Show all statistics."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    data = load_data()
    if not data:
        await message.answer("📊 Ma'lumot yo'q")
        return

    message_text = "📊 <b>BARCHA STATISTIKA</b>\n\n"
    for day, stats in data.items():
        message_text += f"📅 {day}\n"
        for product, qty in stats["products"].items():
            message_text += f"  • {product}: {qty} ta\n"
        message_text += f"  💰 Jami: {stats['total']:,} so'm\n\n"

    await message.answer(message_text, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(F.text == "❓ Yordam")
async def cmd_help(message: types.Message):
    """Help command."""
    await message.answer(
        "❓ <b>Yordam</b>\n\n"
        "/add - Sotilgan mahsulot qo'shish\n"
        "/stats - Bugungi statistika\n"
        "/all_stats - Barcha statistika\n"
        "/start - Bosh menyusi\n\n"
        "🤖 Bot admin tomonidan boshqariladi",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


@dp.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message, state: FSMContext):
    """Go back to main menu."""
    await state.clear()
    await cmd_start(message)


@dp.message()
async def echo(message: types.Message):
    """Default handler."""
    await message.answer("❓ Noxush buyruq. /help yozing.")


# ==================== Main ====================
async def main():
    """Start bot."""
    logger.info("☕ Coffee Bot Starting...")

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN o'rnatilmagan!")
        return

    if ADMIN_ID == 0:
        logger.error("❌ ADMIN_ID o'rnatilmagan!")
        return

    logger.info(f"✅ Admin ID: {ADMIN_ID}")
    logger.info("✅ Bot ishga tushdi...")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtattildi")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Telegram Coffee Shop Bot
Admin controls sales directly via bot commands
"""

import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from pytz import timezone

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TZ = timezone("Asia/Tashkent")

# Data storage
DATA_FILE = Path("coffee_data.json")


# FSM States
class SaleForm(StatesGroup):
    waiting_product = State()
    waiting_quantity = State()
    waiting_price = State()


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ==================== Data Management ====================
def load_data():
    """Load sales data from JSON file."""
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}


def save_data(data):
    """Save sales data to JSON file."""
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Save error: {e}")


def add_sale(product_name: str, quantity: int, price: int) -> str:
    """Add sale record."""
    try:
        today = str(date.today())
        data = load_data()

        if today not in data:
            data[today] = {"sales": [], "total": 0, "products": {}}

        # Add to sales list
        sale = {
            "product": product_name,
            "quantity": quantity,
            "price": price,
            "time": datetime.now(TZ).strftime("%H:%M:%S")
        }
        data[today]["sales"].append(sale)
        data[today]["total"] += price

        # Update product count
        if product_name not in data[today]["products"]:
            data[today]["products"][product_name] = 0
        data[today]["products"][product_name] += quantity

        save_data(data)

        return f"✅ {product_name} x{quantity} - {price:,} so'm qo'shildi"
    except Exception as e:
        logger.error(f"Add sale error: {e}")
        return f"❌ Xato: {e}"


def get_today_stats() -> str:
    """Get today's statistics."""
    today = str(date.today())
    data = load_data()

    if today not in data or not data[today]["sales"]:
        return "📊 Bugun sotilgan mahsulot yo'q"

    stats = data[today]
    message = f"📊 <b>BUG'UNGI STATISTIKA</b>\n\n"

    for product, qty in stats["products"].items():
        message += f"• {product}: {qty} ta\n"

    message += f"\n💰 <b>Jami:</b> {stats['total']:,} so'm"
    return message


# ==================== Keyboards ====================
def main_keyboard():
    """Main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☕ Sotilgan mahsulot")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="❓ Yordam")],
        ],
        resize_keyboard=True
    )


def quick_sales_keyboard():
    """Quick sales buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="☕ Qahva Latte"),
                KeyboardButton(text="🍵 Choy"),
            ],
            [
                KeyboardButton(text="🥤 Cappuccino"),
                KeyboardButton(text="☕ Americano"),
            ],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True
    )


# ==================== Handlers ====================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Sizning ruxsatingiz yo'q")
        return

    await message.answer(
        "☕ <b>Qahva Shop Bot</b>\n\n"
        "Admin panel ta'yyorlangan. Quyidagi buyruqlarni ishlatish mumkin:\n\n"
        "📌 <b>Buyruqlar:</b>\n"
        "/add - Sotilgan mahsulot qo'shish\n"
        "/stats - Bugungi statistika\n"
        "/all_stats - Barcha statistika\n"
        "/help - Yordam\n\n"
        "Yoki pastdagi tugmalardan foydalanish mumkin.",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text == "☕ Sotilgan mahsulot")
async def quick_add(message: types.Message):
    """Quick add menu."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    await message.answer(
        "☕ Mahsulot tanlang va miqdorni yozing\n"
        "Misol: Qahva Latte 2",
        reply_markup=quick_sales_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    """Add sale form."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    await state.set_state(SaleForm.waiting_product)
    await message.answer(
        "☕ Mahsulot nomini yozing:\n"
        "(Misol: Qahva Latte, Cappuccino, Choy...)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Qahva Latte")],
                [KeyboardButton(text="Cappuccino")],
                [KeyboardButton(text="Americano")],
                [KeyboardButton(text="Choy")],
            ],
            resize_keyboard=True
        )
    )


@dp.message(SaleForm.waiting_product)
async def process_product(message: types.Message, state: FSMContext):
    """Process product name."""
    await state.update_data(product=message.text)
    await state.set_state(SaleForm.waiting_quantity)
    await message.answer("📊 Miqdorni yozing (dona):")


@dp.message(SaleForm.waiting_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    """Process quantity."""
    try:
        qty = int(message.text)
        await state.update_data(quantity=qty)
        await state.set_state(SaleForm.waiting_price)
        await message.answer("💰 Narxni yozing (so'm):")
    except ValueError:
        await message.answer("❌ Raqam yozing!")


@dp.message(SaleForm.waiting_price)
async def process_price(message: types.Message, state: FSMContext):
    """Process price and save."""
    try:
        price = int(message.text)
        data = await state.get_data()

        result = add_sale(data["product"], data["quantity"], price)

        # Send confirmation
        current_time = datetime.now(TZ).strftime("%H:%M")
        notification = (
            f"☕ QAHVA SOTILDI!\n\n"
            f"<b>{data['product']}</b> - {data['quantity']} dona\n"
            f"Summa: {price:,} so'm\n"
            f"Vaqti: {current_time}"
        )

        await message.answer(result, reply_markup=main_keyboard())
        await message.answer(notification, parse_mode="HTML")

        await state.clear()
    except ValueError:
        await message.answer("❌ Raqam yozing!")


@dp.message(F.text == "📊 Statistika")
async def cmd_stats(message: types.Message):
    """Show today's stats."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    stats = get_today_stats()
    await message.answer(stats, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(Command("stats"))
async def cmd_stats_command(message: types.Message):
    """Show today's stats."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    stats = get_today_stats()
    await message.answer(stats, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(Command("all_stats"))
async def cmd_all_stats(message: types.Message):
    """Show all statistics."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q")
        return

    data = load_data()
    if not data:
        await message.answer("📊 Ma'lumot yo'q")
        return

    message_text = "📊 <b>BARCHA STATISTIKA</b>\n\n"
    for day, stats in data.items():
        message_text += f"📅 {day}\n"
        for product, qty in stats["products"].items():
            message_text += f"  • {product}: {qty} ta\n"
        message_text += f"  💰 Jami: {stats['total']:,} so'm\n\n"

    await message.answer(message_text, parse_mode="HTML", reply_markup=main_keyboard())


@dp.message(F.text == "❓ Yordam")
async def cmd_help(message: types.Message):
    """Help command."""
    await message.answer(
        "❓ <b>Yordam</b>\n\n"
        "/add - Sotilgan mahsulot qo'shish\n"
        "/stats - Bugungi statistika\n"
        "/all_stats - Barcha statistika\n"
        "/start - Bosh menyusi\n\n"
        "🤖 Bot admin tomonidan boshqariladi",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


@dp.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message, state: FSMContext):
    """Go back to main menu."""
    await state.clear()
    await cmd_start(message)


@dp.message()
async def echo(message: types.Message):
    """Default handler."""
    await message.answer("❓ Noxush buyruq. /help yozing.")


# ==================== Main ====================
async def main():
    """Start bot."""
    logger.info("☕ Coffee Bot Starting...")

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN o'rnatilmagan!")
        return

    if ADMIN_ID == 0:
        logger.error("❌ ADMIN_ID o'rnatilmagan!")
        return

    logger.info(f"✅ Admin ID: {ADMIN_ID}")
    logger.info("✅ Bot ishga tushdi...")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtattildi")
