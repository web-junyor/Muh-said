# Loveble Integration - Quick Reference
# Tez Havolalar

## Configuration Checklist (30 sekund)

### Step 1: Get Credentials from Loveble
```
1. Login Loveble dashboard
2. Go to Settings → API Keys
3. Copy your API KEY
4. Go to Settings → Webhooks
5. Copy your WEBHOOK SECRET
6. Note your SHOP ID
```

### Step 2: Update config.py
```python
# Line 11-14 in config.py:
LOVEBLE_API_KEY = "YOUR_API_KEY_HERE"           # Paste from Loveble
LOVEBLE_WEBHOOK_SECRET = "YOUR_SECRET_HERE"     # Paste from Loveble
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID_HERE"           # Paste from Loveble
```

### Step 3: Map Products (Mahsulotlarni bog'lash)
```python
# Find your products' IDs in Loveble dashboard
# Update loveble_id for each product:

PRODUCTS = {
    "cappuccino": {
        "loveble_id": "CAPPUCCINO_ID_FROM_LOVEBLE"  # e.g., "prod_xyz123"
    },
    "espresso": {
        "loveble_id": "ESPRESSO_ID_FROM_LOVEBLE"
    },
    # ... update all 8 products
}
```

### Step 4: Set Webhook in Loveble
```
Loveble Settings → Webhooks → Add Webhook

URL: http://YOUR_SERVER_IP:8443/webhook/loveble
Secret: (paste your webhook secret)
Events: Select "order_paid" and "order_completed"
```

### Step 5: Test
```bash
cd coffee_system
python main.py

# In another terminal:
curl http://localhost:8443/health
# Should return: {"status":"ok","bot":"running"}
```

---

## Payload Format (What Loveble Sends)

```json
{
  "event_type": "order_paid",                    // ⚠️ Only process this!
  "order_id": "ORD-20260127-123",
  "shop_id": "your_shop_id",
  "timestamp": "2026-01-27T12:30:45",

  "items": [                                      // What was bought
    {
      "product_id": "prod_cappuccino",            // Must match loveble_id
      "product_name": "Cappuccino",
      "quantity": 2,
      "price": 7000,                              // Per unit (som)
      "total_price": 14000                        // quantity × price
    },
    {
      "product_id": "prod_espresso",
      "product_name": "Espresso",
      "quantity": 1,
      "price": 5000,
      "total_price": 5000
    }
  ],

  "total_amount": 19000,                          // Sum of all items
  "payment_status": "paid",
  "payment_method": "card",
  "customer_phone": "+998901234567"
}
```

---

## What Bot Does When Webhook Arrives

1. **Validates signature** - Checks if it's really from Loveble (HMAC-SHA256)
2. **Saves to database** - Registers each sale in coffee.db
3. **Sends Telegram notification** - Admin gets message with product names and check ID
4. **Updates stock** - Decreases product quantity by sold amount
5. **Logs event** - Records everything in coffee_bot.log

---

## Event Types

| Event | Bot Action | Description |
|-------|-----------|-------------|
| `order_paid` | ✅ Process | Customer paid - REGISTER SALE |
| `order_completed` | ✅ Process | Order delivered - REGISTER SALE |
| `order_created` | ❌ Ignore | Order just created - no payment yet |
| `order_cancelled` | ❌ Ignore | Order cancelled - don't count |
| `order_refunded` | ❌ Ignore | Money returned - don't count |

**IMPORTANT:** Only `order_paid` and `order_completed` register sales!

---

## Debugging Commands

### Check if bot is running
```bash
curl http://localhost:8443/health
# Expected: {"status":"ok","bot":"running"}
```

### Check stats/today's sales
```bash
curl http://localhost:8443/stats
# Expected: {"today_sales":5,"today_revenue":35000,"stock":{...}}
```

### Watch logs in real-time
```bash
tail -f coffee_bot.log
```

### Test webhook manually (curl)
```bash
# Generate signature first (openssl)
SECRET="your_webhook_secret"
PAYLOAD='{"event_type":"order_paid","order_id":"TEST","shop_id":"shop",...}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" -r | awk '{print $1}')

# Send test
curl -X POST http://localhost:8443/webhook/loveble \
  -H "Content-Type: application/json" \
  -H "X-Loveble-Signature: $SIGNATURE" \
  -d "$PAYLOAD"

# Expected: {"status":"ok","message":"Webhook processed"}
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **Invalid webhook signature** | Wrong secret | Double-check `LOVEBLE_WEBHOOK_SECRET` in config.py |
| **404 Not Found** | Wrong webhook URL | Set to `http://YOUR_IP:8443/webhook/loveble` |
| **Connection refused** | Bot not running | Run `python main.py` |
| **Product not found** | Wrong loveble_id | Update `loveble_id` in config.py to match Loveble |
| **Sales not appearing** | Wrong event type | Make sure Loveble sends `order_paid` events |

---

## File Locations

```
coffee_system/
├── main.py                  ← Main bot entry point
├── config.py                ← Edit these: LOVEBLE_*, products
├── coffee_bot.log           ← Bot logs
├── coffee.db                ← Database (auto-created)
├── LOVEBLE_INTEGRATION.md   ← Full guide (this file)
├── backend/
│   ├── loveble_api.py       ← Webhook processing
│   ├── database.py          ← Sales storage
│   └── scheduler.py         ← Daily/weekly/monthly reports
└── bot/
    ├── bot.py               ← Telegram bot
    └── handlers.py          ← Bot commands
```

---

## Quick Test Setup

### Option 1: Local Test (No Real Loveble)

```python
# save as test_webhook.py
import requests, json, hmac, hashlib

SECRET = "test_secret"
payload = {
    "event_type": "order_paid",
    "order_id": "TEST-001",
    "shop_id": "shop",
    "timestamp": "2026-01-27T12:00:00",
    "items": [{
        "product_id": "2",
        "product_name": "Cappuccino",
        "quantity": 1,
        "price": 7000,
        "total_price": 7000
    }],
    "total_amount": 7000,
    "payment_status": "paid",
    "payment_method": "card"
}

payload_str = json.dumps(payload)
sig = hmac.new(SECRET.encode(), payload_str.encode(), hashlib.sha256).hexdigest()

r = requests.post(
    "http://localhost:8443/webhook/loveble",
    data=payload_str,
    headers={"Content-Type": "application/json", "X-Loveble-Signature": sig}
)
print(f"Status: {r.status_code}, Response: {r.json()}")
```

Run:
```bash
python test_webhook.py
```

### Option 2: Real Loveble Test
1. In Loveble POS, make a test sale
2. Check bot logs: `tail -f coffee_bot.log`
3. Check Telegram for notification
4. Verify sale in database

---

## Success Indicators ✅

When everything is working:
- ✅ Bot starts without errors
- ✅ Flask listens on port 8443
- ✅ Webhook from Loveble returns 200 OK
- ✅ Admin gets Telegram notification within 5 seconds
- ✅ Sale appears in `/stats` endpoint
- ✅ Daily diagnostics run at 23:00
- ✅ No errors in coffee_bot.log

---

## Contact & Help

If something doesn't work:

1. **Check logs first:** `tail -f coffee_bot.log`
2. **Check config.py:** All credentials filled in?
3. **Check Loveble settings:** Webhook URL and secret correct?
4. **Check network:** Can Loveble reach your server on port 8443?
5. **Test manually:** Try sending test webhook with curl

---

**Last Updated:** January 27, 2026
**Bot Version:** 1.0.0
**Status:** ✅ Running and Operational
