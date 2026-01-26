from aiogram import Router, types
from config import ADMIN_ID
from backend.database import get_today_sales, get_stock

router = Router()

@router.message(commands=["start"])
async def start_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "☕ Coffee Control Bot\n\n"
        "/today — bugungi sotuvlar\n"
        "/stock — ombordagi qoldiq"
    )


@router.message(commands=["today"])
async def today_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    sales = get_today_sales()
    text = "📊 Bugungi sotuvlar:\n\n"

    for product, qty in sales:
        left = get_stock(product)
        text += f"{product}: {qty} ta | Qoldi: {left}\n"

    await message.answer(text)


@router.message(commands=["stock"])
async def stock_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    products = [
        "Espresso","Cappuccino","Latte","Americano",
        "Flat White","Macchiato","Mocha","Affogato"
    ]

    text = "📦 Ombor holati:\n\n"
    for p in products:
        text += f"{p}: {get_stock(p)} ta\n"

    await message.answer(text)
