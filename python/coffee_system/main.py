#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coffee Shop Management System with Loveble Integration
Asosiy entry point
"""

import asyncio
import logging
import sys
from pathlib import Path

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coffee_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Imports
from flask import Flask, request, jsonify
from functools import wraps
import json

from config import (
    TELEGRAM_ADMIN_ID,
    WEBHOOK_PORT,
    WEBHOOK_HOST,
    WEBHOOK_PATH,
    LOVEBLE_WEBHOOK_SECRET
)
from bot.bot import start_bot, stop_bot, bot, dp, notify_admin
from backend.database import db
from backend.scheduler import diagnostics_scheduler
from backend.loveble_api import loveble_client
from backend.models import Sale
from bot.handlers import send_sale_notification
import uuid
from datetime import datetime


# Flask app yaratish (Loveble webhooklar uchun)
app = Flask(__name__)


def verify_webhook_signature(f):
    """Loveble webhook signaturani tekshirish"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            signature = request.headers.get('X-Loveble-Signature', '')
            payload = request.get_data(as_text=True)

            # Signaturani tekshirish
            if not loveble_client.verify_webhook_signature(payload, signature):
                logger.warning("Invalid Loveble webhook signature")
                return jsonify({"error": "Invalid signature"}), 401

            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return jsonify({"error": str(e)}), 400

    return decorated_function


@app.route(WEBHOOK_PATH, methods=['POST'])
@verify_webhook_signature
def loveble_webhook():
    """Loveble webhookni qabul qilish"""
    try:
        payload = request.get_json()
        logger.info(f"Received Loveble webhook: {payload.get('event_type')}")

        # Webhookni qayta ishlash
        success = loveble_client.process_order_event(payload)

        if success:
            # Sotuvlar haqida xabar berish
            items = payload.get('items', [])
            for item in items:
                try:
                    sale = Sale(
                        id=f"{payload.get('order_id')}_{item.get('product_id')}",
                        product_id=item.get('product_id'),
                        product_name=item.get('product_name'),
                        quantity=item.get('quantity'),
                        price=item.get('price'),
                        total_price=item.get('total_price'),
                        check_id=payload.get('order_id'),
                        loveble_order_id=payload.get('order_id'),
                        payment_method=payload.get('payment_method', 'cash'),
                        status='completed',
                        timestamp=datetime.now().isoformat()
                    )

                    # Notification yuborish (task sifatida)
                    asyncio.create_task(send_sale_notification(sale))

                except Exception as e:
                    logger.error(f"Error processing sale: {e}")

            return jsonify({"status": "ok", "message": "Webhook processed"}), 200
        else:
            return jsonify({"status": "skipped", "message": "Order not processed"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "bot": "running"}), 200


@app.route('/stats', methods=['GET'])
def get_stats():
    """Bot statistikasi"""
    try:
        from datetime import date

        today_sales = db.get_sales_by_date(date.today())
        stock_levels = db.get_all_stock_levels()

        return jsonify({
            "today_sales": len(today_sales),
            "today_revenue": sum(s.total_price for s in today_sales),
            "stock": stock_levels,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


async def run_telegram_bot():
    """Telegram botni ishga tushirish"""
    try:
        logger.info("Starting Telegram bot...")
        await start_bot()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")
    finally:
        await stop_bot()


async def main():
    """Asosiy async funksiya"""
    try:
        # Diagnostics schedulerini setup qilish
        logger.info("Setting up diagnostics scheduler...")

        # Bot classiga scheduler callbackni qo'shish
        from bot.handlers import send_diagnostic_report
        diagnostics_scheduler.add_diagnostic_callback(send_diagnostic_report)

        # Scheduler ni start qilish
        diagnostics_scheduler.start()
        logger.info("Diagnostics scheduler started")

        # Telegram botini separate taskda ishga tushirish
        bot_task = asyncio.create_task(run_telegram_bot())

        # Flask appni run qilish (non-blocking)
        logger.info(f"Starting Flask server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")

        # Flask appni separate thread da ishga tushirish
        import threading
        flask_thread = threading.Thread(
            target=lambda: app.run(
                host=WEBHOOK_HOST,
                port=WEBHOOK_PORT,
                debug=False,
                use_reloader=False,
                threaded=True
            ),
            daemon=True
        )
        flask_thread.start()

        # Bot taskni kutish
        await bot_task

    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await stop_bot()


if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("Coffee Shop Bot Starting")
        logger.info("=" * 50)

        # Database ni tekshirish
        products = db.get_all_products()
        logger.info(f"Database loaded with {len(products)} products")

        # Async event loopda ishga tushirish
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
