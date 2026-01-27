from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.pdfgen import canvas
from pathlib import Path
import qrcode
import io
import logging

logger = logging.getLogger(__name__)


def generate_pdf(order_id: str, items, total_amount: int) -> Path:
    """Generate professional PDF receipt with embedded QR code"""
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
