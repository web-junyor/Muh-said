from aiogram import Bot
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(BOT_TOKEN)

async def notify_admin(product, qty, amount, receipt):
    text = (
        f"☕ Yangi sotuv (Click)\n\n"
        f"Mahsulot: {product}\n"
        f"Soni: {qty}\n"
        f"Summa: {amount} so'm\n\n"
        f"🧾 Chek:\n{receipt}"
    )
    await bot.send_message(ADMIN_ID, text)


async def send_report():
    from backend.reports import build_daily_report
    report = build_daily_report()
    await bot.send_message(ADMIN_ID, report)
