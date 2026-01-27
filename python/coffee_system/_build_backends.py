import os
import sys
import json
from datetime import datetime

# Change to correct directory
os.chdir("c:\\Users\\Пользователь\\OneDrive\\Documents\\GitHub\\Muh-said\\python\\coffee_system")

# ==== STATS.PY ====
stats_code = """import json
from datetime import date
from pathlib import Path
from threading import Lock

FILE = Path("data/daily_stats.json")
FILE.parent.mkdir(exist_ok=True)
_lock = Lock()


def update_stats(items):
    \"\"\"Thread-safe daily stats update\"\"\"
    with _lock:
        today = str(date.today())
        stats = json.loads(FILE.read_text()) if FILE.exists() else {}
        if today not in stats:
            stats[today] = {"products": {}, "total": 0}

        for item in items:
            pname = item.product_name
            stats[today]["products"][pname] = stats[today]["products"].get(pname, 0) + item.quantity
            stats[today]["total"] += item.total_price

        FILE.write_text(json.dumps(stats, indent=2))


def get_today_stats():
    \"\"\"Get today's sales summary\"\"\"
    today = str(date.today())
    if not FILE.exists():
        return {"products": {}, "total": 0}
    all_stats = json.loads(FILE.read_text())
    return all_stats.get(today, {"products": {}, "total": 0})


def get_all_stats():
    \"\"\"Get all historical stats\"\"\"
    if not FILE.exists():
        return {}
    return json.loads(FILE.read_text())
"""

with open("backend/stats.py", "w", encoding="utf-8") as f:
    f.write(stats_code)
print("[OK] stats.py")

# ==== SECURITY.PY ====
security_code = """import hashlib
import hmac
import os

CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")


def verify_click_signature(raw_body: bytes, received_sign: str) -> bool:
    \"\"\"Verify Click webhook signature using HMAC-SHA256\"\"\"
    if not CLICK_SECRET_KEY:
        raise RuntimeError("CLICK_SECRET_KEY environment variable not set")

    computed = hashlib.sha256(raw_body + CLICK_SECRET_KEY.encode()).hexdigest()
    return hmac.compare_digest(computed, received_sign)
"""

with open("backend/security.py", "w", encoding="utf-8") as f:
    f.write(security_code)
print("[OK] security.py")

# ==== TELEGRAM.PY ====
telegram_code = """import os
import logging
from aiogram import Bot
from pathlib import Path

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None


async def send_message(text: str):
    \"\"\"Send text message to admin chat\"\"\"
    if not bot:
        logger.error("Bot not initialized")
        return
    try:
        await bot.send_message(chat_id=int(CHAT_ID), text=text)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


async def send_document(file_path):
    \"\"\"Send PDF receipt to admin chat\"\"\"
    if not bot:
        return
    try:
        path = Path(file_path)
        if path.exists():
            with open(path, "rb") as f:
                await bot.send_document(chat_id=int(CHAT_ID), document=f)
    except Exception as e:
        logger.error(f"Failed to send document: {e}")
"""

with open("backend/telegram.py", "w", encoding="utf-8") as f:
    f.write(telegram_code)
print("[OK] telegram.py")

# ==== PDF.PY ====
pdf_code = """from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.pdfgen import canvas
from pathlib import Path
import qrcode
import io
import logging

logger = logging.getLogger(__name__)


def generate_pdf(order_id: str, items, total_amount: int) -> Path:
    \"\"\"Generate professional PDF receipt with embedded QR code\"\"\"
    pdf_dir = Path("data/receipts")
    pdf_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = pdf_dir / f"{order_id}.pdf"

    try:
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4

        # Header brown background
        header_color = HexColor("#8B4513")
        c.setFillColor(header_color)
        c.rect(0, height - 2*cm, width, 2*cm, fill=1)

        # Title
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1*cm, height - 1.2*cm, "☕ SAID COFFEE")

        # Order details
        y = height - 3.5*cm
        c.setFont("Helvetica", 10)
        c.drawString(1*cm, y, f"Order ID: {order_id}")
        c.drawString(1*cm, y - 0.4*cm, f"Total: {total_amount:,} UZS")

        # Items
        y -= 1*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*cm, y, "Items:")

        y -= 0.5*cm
        c.setFont("Helvetica", 10)
        for item in items:
            line = f"• {item.product_name} x{item.quantity} = {item.total_price:,} UZS"
            c.drawString(1.5*cm, y, line)
            y -= 0.4*cm

        # QR Code embedded in PDF
        qr_data = f"Order:{order_id}|Amount:{total_amount}"
        qr = qrcode.QRCode(version=1, box_size=5, border=1)
        qr.add_data(qr_data)
        qr.make()

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_size = 3*cm
        c.drawImage(qr_buffer, width - qr_size - 1*cm, 1*cm, width=qr_size, height=qr_size)

        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(1*cm, 0.5*cm, "Thank you for your purchase!")

        c.showPage()
        c.save()

        logger.info(f"PDF: {pdf_path}")
        return pdf_path

    except Exception as e:
        logger.error(f"PDF error: {e}")
        raise
"""

with open("backend/pdf.py", "w", encoding="utf-8") as f:
    f.write(pdf_code)
print("[OK] pdf.py")

print("\n[DONE] All backend modules created successfully")
