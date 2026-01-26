#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coffee Shop Management System - Configuration
Loveble integratsiyasi bilan tugallangan konfiguratsiya
"""

import os
from datetime import datetime

# ==================== Telegram Bot Settings ====================
TELEGRAM_BOT_TOKEN = "8437143053:AAF0URL0zjjO4fK3dLz4MZWsIGka2dLouPI"
TELEGRAM_ADMIN_ID = 5995404792  # Bot egasining Telegram ID

# ==================== Loveble API Settings ====================
LOVEBLE_API_KEY = "sk_live_loveble_credentials"
LOVEBLE_API_URL = "https://api.loveble.com"
LOVEBLE_WEBHOOK_SECRET = "whsec_live_loveble_secret"
LOVEBLE_SHOP_ID = "said_coffee_shop"

# ==================== Database Settings ====================
DATABASE_NAME = "coffee.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# ==================== Coffee Products Inventory ====================
# 8 ta mahsulot, har birida 12 dona dastlabki qoldig'i
PRODUCTS = {
    "espresso": {
        "id": "1",
        "name": "Espresso",
        "initial_stock": 12,
        "price": 5000,  # som
        "loveble_id": "ded1_gahvaxona"
    },
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,
        "loveble_id": "prod_cappuccino"
    },
    "latte": {
        "id": "3",
        "name": "Latte",
        "initial_stock": 12,
        "price": 8000,
        "loveble_id": "product_latte"
    },
    "americano": {
        "id": "4",
        "name": "Americano",
        "initial_stock": 12,
        "price": 6000,
        "loveble_id": "prod_americano"
    },
    "flat_white": {
        "id": "5",
        "name": "Flat White",
        "initial_stock": 12,
        "price": 8500,
        "loveble_id": "mahaulot_tekis_oq"
    },
    "macchiato": {
        "id": "6",
        "name": "Macchiato",
        "initial_stock": 12,
        "price": 7500,
        "loveble_id": "prod_macchiato"
    },
    "mocha": {
        "id": "7",
        "name": "Mocha",
        "initial_stock": 12,
        "price": 9000,
        "loveble_id": "prod_mocha"
    },
    "affogato": {
        "id": "8",
        "name": "Affogato",
        "initial_stock": 12,
        "price": 8500,
        "loveble_id": "prod_affogato"
    },
}

# ==================== Diagnostics Schedule ====================
DAILY_DIAGNOSTIC_TIME = "23:00"  # Har kuni 23:00 da diagnostika
DAILY_DIAGNOSTIC_HOUR = 23
DAILY_DIAGNOSTIC_MINUTE = 0

WEEKLY_DIAGNOSTIC_DAY = "friday"  # Juma kuni haftalik hisobot
WEEKLY_DIAGNOSTIC_TIME = "23:05"

MONTHLY_DIAGNOSTIC_DAY = 1  # Oyning 1-quni oylik hisobot
MONTHLY_DIAGNOSTIC_TIME = "23:10"

# ==================== Stock Alert Settings ====================
LOW_STOCK_THRESHOLD = 3  # 3 ta yoki kamroq qolsa ogohlantirma berish
CRITICAL_STOCK_THRESHOLD = 1  # 1 ta qolsa kritik ogohlantirma

# ==================== Logging Settings ====================
LOG_FILE = "logs.json"
LOG_LEVEL = "INFO"
SALES_LOG_FILE = "sales.json"
DIAGNOSTICS_LOG_FILE = "diagnostics.json"

# ==================== Webhook Settings (Loveble uchun) ====================
WEBHOOK_PORT = 8443
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PATH = "/webhook/loveble"
WEBHOOK_URL = "https://yourdomain.com/webhook/loveble"

# ==================== Timezone Settings ====================
TIMEZONE = "Asia/Tashkent"

# ==================== Messages ====================
MESSAGES = {
    "sale_notification": "🛍️ *Yangi sotuvlar ayni damda!*\n\n{product_name}\n💰 Narxi: {price} som\n✅ Chek ID: {check_id}\n\nQoldig'i: {remaining_stock} dona",
    "daily_diagnostic": "📊 *Bugunlik Diagnostika - {date}*\n\n{report}",
    "weekly_diagnostic": "📈 *Haftalik Diagnostika - {week}*\n\n{report}",
    "monthly_diagnostic": "📅 *Oylik Diagnostika - {month}*\n\n{report}",
    "low_stock_alert": "⚠️ *Kam Qoldig'i Ogohlantirmasi!*\n\n{product_name}: {remaining_stock} dona qoldi!",
    "critical_stock_alert": "🚨 *Kritik Qoldig'i!*\n\n{product_name}: {remaining_stock} dona qoldi! Darhol qo'shimchasini toping!",
}

# ==================== API Retry Settings ====================
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ==================== Click (Pul o'tkazish) Settings ====================
CLICK_SECRET_KEY = "CLICK_SECRET"
CLICK_MERCHANT_ID = "YOUR_CLICK_MERCHANT_ID"

# ==================== Development Settings ====================
DEBUG = True
DEVELOPMENT_MODE = False  # True bo'lganda test ma'lumotlar ishlatiladi
