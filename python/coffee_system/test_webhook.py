#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loveble Webhook Test Script
Webhook'ni test qilish uchun
"""

import requests
import json
import hmac
import hashlib
from datetime import datetime
import sys

# Config
WEBHOOK_URL = "http://localhost:8443/webhook/loveble"  # Serverga qo'yingizda: https://your-server-ip:8443/webhook/loveble
WEBHOOK_SECRET = "whsec_live_loveble_secret"  # config.py dan oling

# Test payloads
TEST_PAYLOADS = {
    "order_paid": {
        "event_type": "order_paid",
        "order_id": f"ORD-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "shop_id": "said_coffee_shop",
        "timestamp": datetime.now().isoformat(),
        "items": [
            {
                "product_id": "prod_cappuccino",
                "product_name": "Cappuccino",
                "quantity": 2,
                "price": 7000,
                "total_price": 14000
            },
            {
                "product_id": "ded1_gahvaxona",
                "product_name": "Espresso",
                "quantity": 1,
                "price": 5000,
                "total_price": 5000
            }
        ],
        "total_amount": 19000,
        "payment_status": "paid",
        "payment_method": "card"
    },

    "order_completed": {
        "event_type": "order_completed",
        "order_id": f"ORD-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "shop_id": "said_coffee_shop",
        "timestamp": datetime.now().isoformat(),
        "items": [
            {
                "product_id": "product_latte",
                "product_name": "Latte",
                "quantity": 1,
                "price": 8000,
                "total_price": 8000
            }
        ],
        "total_amount": 8000,
        "payment_status": "completed",
        "payment_method": "cash"
    },

    "cappuccino_single": {
        "event_type": "order_paid",
        "order_id": f"CAPPUCCINO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "shop_id": "said_coffee_shop",
        "timestamp": datetime.now().isoformat(),
        "items": [
            {
                "product_id": "prod_cappuccino",
                "product_name": "Cappuccino",
                "quantity": 1,
                "price": 7000,
                "total_price": 7000
            }
        ],
        "total_amount": 7000,
        "payment_status": "paid",
        "payment_method": "card"
    }
}


def create_signature(payload_str: str, secret: str) -> str:
    """Webhook signature yaratish (HMAC-SHA256)"""
    return hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()


def send_webhook(payload: dict, test_name: str = "Test") -> None:
    """Webhook yuborish"""
    try:
        payload_str = json.dumps(payload)
        signature = create_signature(payload_str, WEBHOOK_SECRET)

        headers = {
            "Content-Type": "application/json",
            "X-Loveble-Signature": signature
        }

        print(f"\n{'='*60}")
        print(f"🔄 Webhook yuborilmoqda: {test_name}")
        print(f"{'='*60}")
        print(f"📍 URL: {WEBHOOK_URL}")
        print(f"📦 Event: {payload.get('event_type')}")
        print(f"🔑 Order ID: {payload.get('order_id')}")
        print(f"📊 Items: {len(payload.get('items', []))} ta")
        print(f"💰 Total: {payload.get('total_amount'):,} so'm")
        print(f"🔐 Signature: {signature[:20]}...")

        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            verify=False,  # Self-signed sertifikat uchun
            timeout=10
        )

        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📝 Response: {response.text[:200]}")

        if response.status_code == 200:
            print("✅ SUCCESS - Webhook qabul qilindi!")
        else:
            print(f"⚠️ WARNING - Status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Server bilan ulanib bo'lmadi!")
        print(f"   Tekshiring: {WEBHOOK_URL} mavjud va ishlamoqda?")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║        🍵 LOVEBLE WEBHOOK TEST SCRIPT 🍵                  ║
╚════════════════════════════════════════════════════════════╝
""")

    # Webhook URL'ni tekshirish
    print(f"📌 Webhook URL: {WEBHOOK_URL}")
    print(f"🔐 Secret (oxirgi 10 char): ...{WEBHOOK_SECRET[-10:]}")

    print(f"\n📋 Test turləri:")
    for i, test_name in enumerate(TEST_PAYLOADS.keys(), 1):
        print(f"   {i}. {test_name}")
    print(f"   4. Barcha testlar")
    print(f"   0. Chiqish")

    while True:
        choice = input("\n🎯 Tanlang (0-4): ").strip()

        if choice == "0":
            print("\n👋 Xayr!")
            sys.exit(0)
        elif choice == "4":
            for test_name, payload in TEST_PAYLOADS.items():
                send_webhook(payload, test_name)
                input("\n⏸️  Enter bilan davom qiling...")
        elif choice in ["1", "2", "3"]:
            idx = int(choice) - 1
            test_name = list(TEST_PAYLOADS.keys())[idx]
            payload = TEST_PAYLOADS[test_name]
            send_webhook(payload, test_name)
        else:
            print("❌ Noto'g'ri tanlov!")


if __name__ == "__main__":
    main()
