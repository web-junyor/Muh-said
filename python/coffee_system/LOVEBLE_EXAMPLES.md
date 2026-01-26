# Loveble Integration - Real Examples & Visuals
# Haqiqiy Misollar va Rasmlar

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOVEBLE POS SYSTEM                          │
│              (Sizning Kofey Do'koni Fiskali)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ When customer pays:
                          │ POST /webhook/loveble
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│               YOUR BOT FLASK SERVER                             │
│           (http://YOUR_IP:8443)                                │
│                                                                 │
│  1. Verify signature (HMAC-SHA256)                             │
│  2. Extract items, quantities, prices                          │
│  3. Save to SQLite database                                    │
│  4. Send to Telegram admin                                     │
│  5. Update stock levels                                        │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                  │
             ↓                                  ↓
    ┌────────────────┐            ┌─────────────────────┐
    │  SQLite DB     │            │  Telegram Admin     │
    │  (coffee.db)   │            │  (Message & Alert)  │
    │                │            │                     │
    │ - Cappuccino:2 │            │ "Cappuccino x2"     │
    │ - Espresso: 1  │            │ "Check ID: ..."     │
    │ - Total: 14000 │            │ "Revenue: 14000"    │
    └────────────────┘            └─────────────────────┘
```

---

## Real Webhook Examples

### Example 1: Single Product Sale

**What Loveble sends:**
```json
{
  "event_type": "order_paid",
  "order_id": "ORD-20260127-001",
  "shop_id": "shop_12345",
  "timestamp": "2026-01-27T14:30:45",
  "items": [
    {
      "product_id": "prod_cappuccino_uuid",
      "product_name": "Cappuccino",
      "quantity": 1,
      "price": 7000,
      "total_price": 7000
    }
  ],
  "total_amount": 7000,
  "payment_status": "paid",
  "payment_method": "card",
  "customer_phone": "+998901234567"
}
```

**Bot processes:**
1. ✅ Signature verified
2. ✅ Found product: "Cappuccino"
3. ✅ Registered sale: 1 unit, 7000 som
4. ✅ Updated stock: Cappuccino 12 → 11
5. ✅ Sent to Telegram admin:
   ```
   ☕ SOTUV HAQIDA XABAR

   📦 Cappuccino × 1
   💰 Narx: 7,000 som

   🧾 Chek ID: ORD-20260127-001
   ⏰ Vaqt: 14:30:45
   ```

**Database entry:**
```
ID: ORD-20260127-001_Cappuccino
Product: Cappuccino
Quantity: 1
Price: 7000
Total: 7000
Check: ORD-20260127-001
Status: completed
Timestamp: 2026-01-27T14:30:45
```

---

### Example 2: Multiple Products Sale

**What Loveble sends:**
```json
{
  "event_type": "order_paid",
  "order_id": "ORD-20260127-002",
  "shop_id": "shop_12345",
  "timestamp": "2026-01-27T15:45:22",
  "items": [
    {
      "product_id": "prod_cappuccino_uuid",
      "product_name": "Cappuccino",
      "quantity": 2,
      "price": 7000,
      "total_price": 14000
    },
    {
      "product_id": "prod_espresso_uuid",
      "product_name": "Espresso",
      "quantity": 1,
      "price": 5000,
      "total_price": 5000
    },
    {
      "product_id": "prod_latte_uuid",
      "product_name": "Latte",
      "quantity": 1,
      "price": 8000,
      "total_price": 8000
    }
  ],
  "total_amount": 27000,
  "payment_status": "paid",
  "payment_method": "cash",
  "customer_phone": null
}
```

**Bot processes:**
1. ✅ Verified signature
2. ✅ Found 3 products
3. ✅ Registered 3 sales
4. ✅ Updated stock:
   - Cappuccino: 11 → 9
   - Espresso: 12 → 11
   - Latte: 12 → 11
5. ✅ Sent to Telegram admin:
   ```
   ☕ SOTUV HAQIDA XABAR

   📦 Cappuccino × 2
   💰 Narx: 14,000 som

   📦 Espresso × 1
   💰 Narx: 5,000 som

   📦 Latte × 1
   💰 Narx: 8,000 som

   ━━━━━━━━━━━━━━━━━━━━━━━
   💵 JAMI: 27,000 som

   🧾 Chek ID: ORD-20260127-002
   ⏰ Vaqt: 15:45:22
   ```

**Database entries:**
```
Sale 1: Cappuccino × 2, 14000 som
Sale 2: Espresso × 1, 5000 som
Sale 3: Latte × 1, 8000 som
```

---

### Example 3: Wrong Product ID (Error Case)

**What Loveble sends (WRONG product_id):**
```json
{
  "event_type": "order_paid",
  "order_id": "ORD-20260127-003",
  "shop_id": "shop_12345",
  "items": [
    {
      "product_id": "prod_unknown_id",  // ❌ This doesn't match config.py!
      "product_name": "Unknown Coffee",
      "quantity": 1,
      "price": 5000,
      "total_price": 5000
    }
  ],
  "total_amount": 5000,
  "payment_status": "paid",
  "payment_method": "card"
}
```

**Bot processes:**
1. ❌ Can't find product with id "prod_unknown_id"
2. ❌ Still saves the sale (with product_name="Unknown Coffee")
3. ⚠️ Logs ERROR in coffee_bot.log:
   ```
   ERROR - Product not found: prod_unknown_id
   ```
4. ✅ Still notifies admin (to flag the issue)

**Fix:** Update config.py with correct loveble_id:
```python
"coffee_name": {
    "loveble_id": "prod_unknown_id"  # Now it matches!
}
```

---

## Config.py Setup Example

### Before (Template)
```python
# ==================== Loveble API Settings ====================
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY_HERE"
LOVEBLE_API_URL = "https://api.loveble.com"
LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET_HERE"
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID_HERE"

PRODUCTS = {
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,
        "loveble_id": "cappuccino_loveble_id"  # ❌ PLACEHOLDER!
    },
    # ...
}
```

### After (Real Setup)
```python
# ==================== Loveble API Settings ====================
LOVEBLE_API_KEY = "sk_live_abc123def456xyz789"  # From Loveble Settings
LOVEBLE_API_URL = "https://api.loveble.com"
LOVEBLE_WEBHOOK_SECRET = "whsec_live_12345abc789xyz"  # From Webhook Secret
LOVEBLE_SHOP_ID = "shop_987654321"  # Your Shop ID

PRODUCTS = {
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,
        "loveble_id": "prod_2a3b4c5d_cappuccino"  # ✅ Real Loveble ID!
    },
    "espresso": {
        "id": "1",
        "name": "Espresso",
        "initial_stock": 12,
        "price": 5000,
        "loveble_id": "prod_1x9y8z7w_espresso"  # ✅ Real Loveble ID!
    },
    # ... other products
}
```

---

## Telegram Notification Examples

### Single Item Sale
```
☕ SOTUV HAQIDA XABAR

📦 Cappuccino × 1
💰 Narx: 7,000 som

🧾 Chek ID: ORD-20260127-001
⏰ Vaqt: 2026-01-27 14:30:45
```

### Multi-Item Sale
```
☕ SOTUV HAQIDA XABAR

📦 Cappuccino × 2 = 14,000 som
📦 Espresso × 1 = 5,000 som
📦 Latte × 1 = 8,000 som

━━━━━━━━━━━━━━━━━━━━━━━━━
💵 JAMI DAROMAD: 27,000 som

🧾 Chek ID: ORD-20260127-002
⏰ Vaqt: 2026-01-27 15:45:22
🏪 To'lov usuli: Naqd pul
```

### Daily Diagnostic (23:00)
```
📊 KUNLIK DIAGNOSTIKA - 2026-01-27

📈 Bugun:
• Jami sotuvlar: 15 ta
• Daromad: 125,000 som

📦 Mahsulotlar:
• Cappuccino: 5 ta sotildi (qoldig'i: 7)
• Espresso: 3 ta sotildi (qoldig'i: 9)
• Latte: 4 ta sotildi (qoldig'i: 8)
• Americano: 2 ta sotildi (qoldig'i: 10)
• Mocha: 1 ta sotildi (qoldig'i: 11)
• Boshqalar: 0 ta

⚠️ KAM QOLDIG'I:
• Cappuccino: 7 ta (Threshold: 5)

⏰ Tekshirilgan: 2026-01-27 23:00:00
```

### Weekly Diagnostic (Friday 23:05)
```
📊 HAFTALIK DIAGNOSTIKA

📈 Bu hafta (27 Jan - 2 Feb):
• Jami sotuvlar: 87 ta
• Daromad: 612,500 som
• O'rtacha sotuv: 12.4 ta/kun

📦 Eng ko'p sotilganlar:
🥇 Cappuccino: 28 ta
🥈 Latte: 25 ta
🥉 Americano: 18 ta
```

---

## Webhook Signature Example

### How HMAC-SHA256 Signature Works

```python
import hmac
import hashlib
import json

# 1. Get payload from Loveble
payload = {
    "event_type": "order_paid",
    "order_id": "ORD-123",
    "items": [{"product_id": "2", "product_name": "Cappuccino", "quantity": 1}]
}

# 2. Convert to JSON string
payload_str = json.dumps(payload)
# Result: '{"event_type":"order_paid","order_id":"ORD-123",...}'

# 3. Get secret from Loveble
secret = "whsec_live_12345abc789xyz"

# 4. Calculate HMAC-SHA256
signature = hmac.new(
    secret.encode(),
    payload_str.encode(),
    hashlib.sha256
).hexdigest()
# Result: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"

# 5. Loveble sends this in header:
# X-Loveble-Signature: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# 6. Bot receives and verifies:
# ✅ If signature matches → Webhook is real from Loveble
# ❌ If signature doesn't match → Someone is faking it!
```

---

## Database Schema After Sale

```
TABLE: sales
┌─────────────────────────────────────────────────┐
│ id                                              │
├─────────────────────────────────────────────────┤
│ ORD-20260127-002_Cappuccino                    │
│ ORD-20260127-002_Espresso                      │
│ ORD-20260127-002_Latte                         │
└─────────────────────────────────────────────────┘

TABLE: products
┌─────────────────────────────────────────────────┐
│ product_id │ name      │ current_stock           │
├────────────┼───────────┼─────────────────────────┤
│ 1          │ Espresso  │ 11 (was 12, sold 1)     │
│ 2          │ Cappuccino│ 9  (was 12, sold 2)     │
│ 3          │ Latte     │ 11 (was 12, sold 1)     │
│ 4          │ Americano │ 12 (no sales)           │
│ ...        │ ...       │ ...                     │
└─────────────────────────────────────────────────┘

TABLE: daily_reports (auto-created at 23:00)
┌─────────────────────────────────────────────────┐
│ date  │ total_sales │ total_revenue │ ...      │
├───────┼─────────────┼───────────────┼──────────┤
│ 2026-01-27 │ 15 │ 125000 │ ... │
└─────────────────────────────────────────────────┘
```

---

## Flow Diagram: From Sale to Notification

```
1. Customer buys at Loveble POS
   ↓
2. Loveble processes payment
   ↓
3. Loveble sends webhook:
   POST http://YOUR_IP:8443/webhook/loveble
   {
     "event_type": "order_paid",
     "order_id": "ORD-123",
     "items": [...]
   }
   With signature header: X-Loveble-Signature: ...
   ↓
4. Your Flask server receives request
   ↓
5. @verify_webhook_signature decorator:
   - Recalculate HMAC with LOVEBLE_WEBHOOK_SECRET
   - Compare with X-Loveble-Signature header
   - If not match: return 401 Unauthorized
   ↓
6. loveble_webhook() handler:
   - Parse JSON payload
   - Call loveble_client.process_order_event()
   ↓
7. LovebleAPIClient.process_order_event():
   - Check if event_type is "order_paid" or "order_completed"
   - If yes: proceed (if no: ignore)
   ↓
8. For each item in order:
   - Create Sale object
   - db.register_sale(sale)
   - asyncio.create_task(send_sale_notification(sale))
   ↓
9. DatabaseManager.register_sale():
   - INSERT INTO sales (...)
   - UPDATE products SET current_stock = ...
   - COMMIT transaction
   ↓
10. send_sale_notification() (async):
    - await bot.send_message(ADMIN_ID, formatted_message)
    ↓
11. Telegram Admin receives notification:
    ☕ SOTUV HAQIDA XABAR
    📦 Cappuccino × 1
    💰 7,000 som
    ...
    ↓
12. Return response to Loveble:
    {"status": "ok", "message": "Webhook processed"}

TOTAL TIME: < 2 seconds
```

---

## Testing Checklist with Examples

### Test 1: Check Bot Running
```bash
$ curl http://localhost:8443/health
{"status":"ok","bot":"running"}  ✅
```

### Test 2: Check Stats
```bash
$ curl http://localhost:8443/stats
{
  "today_sales": 2,
  "today_revenue": 12000,
  "stock": {
    "Cappuccino": 10,
    "Espresso": 11,
    "Latte": 12,
    ...
  },
  "timestamp": "2026-01-27T15:45:22"
}  ✅
```

### Test 3: Send Fake Webhook
```bash
# 1. Create test payload
PAYLOAD='{"event_type":"order_paid","order_id":"TEST-001","shop_id":"shop","timestamp":"2026-01-27T12:00:00","items":[{"product_id":"2","product_name":"Cappuccino","quantity":1,"price":7000,"total_price":7000}],"total_amount":7000,"payment_status":"paid","payment_method":"card"}'

# 2. Calculate signature
SECRET="your_webhook_secret"
SIG=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" -r | awk '{print $1}')

# 3. Send webhook
curl -X POST http://localhost:8443/webhook/loveble \
  -H "Content-Type: application/json" \
  -H "X-Loveble-Signature: $SIG" \
  -d "$PAYLOAD"

# Expected response:
# {"status":"ok","message":"Webhook processed"}  ✅

# 4. Check logs
tail -f coffee_bot.log
# Should see: "Received Loveble webhook: order_paid"  ✅

# 5. Check Telegram
# Admin should receive notification in 1-2 seconds  ✅
```

---

## Production Deployment Checklist

```
[ ] All credentials in config.py filled
[ ] Webhook URL set in Loveble: http://YOUR_DOMAIN:8443/webhook/loveble
[ ] Webhook Secret set in Loveble and config.py (MATCH!)
[ ] All product loveble_ids correct
[ ] Database backup created
[ ] SSL certificate (if using domain)
[ ] Firewall allows port 8443
[ ] Bot auto-restart on crash (systemd)
[ ] Log rotation configured
[ ] Admin phone number verified
[ ] Test webhook sent and received
[ ] Daily diagnostic scheduled for 23:00
[ ] Weekly diagnostic scheduled for Friday 23:05
[ ] Monthly diagnostic scheduled for 1st day 23:10
```

---

**Need help?** Check coffee_bot.log for errors!
