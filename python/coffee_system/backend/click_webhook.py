import logging
from fastapi import Request, HTTPException
from datetime import datetime
from pytz import timezone
from backend.models import OrderPaid
from backend.security import verify_click_signature
from backend.storage import is_duplicate, save_order
from backend.stats import update_stats, get_today_stats
from backend.pdf import generate_pdf
from backend.telegram import send_message, send_document

logger = logging.getLogger(__name__)
TZ = timezone("Asia/Tashkent")


async def click_webhook(request: Request):
    """
    Handle Click payment webhook.

    Security & Reliability:
    - HMAC-SHA256 signature verification (required)
    - Idempotency protection via duplicate detection
    - Always returns 200 (stops Click retry loops on errors)
    - Concurrent safety via thread-safe storage module
    - PDF/Telegram failures don't crash webhook response

    Args:
        request: FastAPI request with body and headers

    Returns:
        JSON dict with status field (always 200 HTTP status)
    """
    try:
        raw_body = await request.body()
        signature = request.headers.get("X-Click-Signature", "")

        # Verify signature (return 200 to prevent Click retries)
        if not signature or not verify_click_signature(raw_body, signature):
            logger.warning(f"Invalid/missing signature from {request.client.host}")
            return {"status": "invalid_signature"}

        # Parse JSON (return 200 on invalid JSON - don't retry)
        try:
            data = OrderPaid.model_validate_json(raw_body.decode("utf-8"))
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return {"status": "invalid_json"}

        # Check payment status (return 200 for non-paid)
        if data.payment_status != "paid":
            logger.info(f"Order {data.order_id} status: {data.payment_status}")
            return {"status": "ignored"}

        # Idempotency check (return 200 for duplicates)
        if is_duplicate(data.order_id):
            logger.info(f"Duplicate order: {data.order_id}")
            return {"status": "duplicate"}

        # Save order to storage
        try:
            save_order(data.order_id)
        except Exception as e:
            logger.error(f"Order save failed: {e}")
            return {"status": "save_failed"}

        # Update statistics
        try:
            update_stats(data.items)
        except Exception as e:
            logger.error(f"Stats update failed: {e}")

        # Generate PDF (failure doesn't stop response)
        pdf_path = None
        try:
            pdf_path = generate_pdf(data.order_id, data.items, data.total_amount)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")

        # Send Telegram notifications (non-blocking, failures logged)
        try:
            # Get current time in Tashkent timezone
            current_time = datetime.now(TZ).strftime("%H:%M")

            # Send message for each item with nice format
            for item in data.items:
                message = (
                    f"☕ QAHVA SOTILDI!\n\n"
                    f"<b>{item.product_name}</b> - {item.quantity} dona\n"
                    f"Summa: {item.total_price:,} so'm\n"
                    f"Vaqti: {current_time}"
                )
                await send_message(message)

            # Send PDF chek
            if pdf_path:
                await send_document(pdf_path)

            # Send today's statistics summary
            today_stats = get_today_stats()
            stats_message = (
                f"📊 <b>BUG'UNGI STATISTIKA</b>\n\n"
                f"Jami sotilgan: {data.total_amount:,} so'm\n"
                f"Order ID: {data.order_id}"
            )

            if today_stats and "products" in today_stats:
                stats_message += "\n\n<b>Mahsulotlar:</b>\n"
                for product, qty in today_stats["products"].items():
                    stats_message += f"• {product}: {qty} ta\n"

            await send_message(stats_message)

        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")

        logger.info(f"Order {data.order_id} processed successfully")
        return {"status": "ok"}

    except Exception as e:
        # Catch-all: always return 200 with status field
        logger.error(f"Webhook error: {e}", exc_info=False)
        return {"status": "error"}
