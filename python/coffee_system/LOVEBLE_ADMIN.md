# Loveble Integration - Summary for Admin
# Loveble Integratsiyasining Xulosa

## 📋 What Your Bot Does When Loveble Sends Data

```
┌──────────────────────────────────────────────────────────┐
│  Loveble POS (Your Coffee Shop)                         │
│  └─ Customer pays for: Cappuccino × 2                   │
└────────────────────────┬─────────────────────────────────┘
                         │ Sends to bot:
                         ↓ POST /webhook/loveble
              ┌──────────────────────────┐
              │  Your Bot (Flask Server) │
              │  Verifies signature      │
              │  Saves to database       │
              │  Sends Telegram msg      │
              └──────────────┬───────────┘
                             ├─→ Database saves:
                             │   - Cappuccino × 2 sold
                             │   - Stock: 12 → 10
                             │   - Revenue: 14,000 som
                             │
                             └─→ You get Telegram message:
                                 ☕ Cappuccino × 2
                                 💰 14,000 som
                                 🧾 Check: ORD-123
                                 ⏰ Time: 14:30
```

---

## 🔧 What You Need to Do - 5 Steps

### Step 1: Get Info from Loveble (5 minutes)
Go to **Loveble Dashboard** and find:

| What | Where | Example |
|-----|-------|---------|
| **API Key** | Settings → API Keys | `sk_live_abc123...` |
| **Shop ID** | Settings → Shop Info | `shop_987654321` |
| **Webhook Secret** | Settings → Webhooks | `whsec_live_xyz...` |
| **Product IDs** | Products → Each product | `prod_2a3b4c5d_cappuccino` |

### Step 2: Update config.py (2 minutes)
Edit: `coffee_system/config.py`

Find lines 11-14:
```python
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY_HERE"
                     ↓ PASTE YOUR API KEY HERE
LOVEBLE_API_KEY = "sk_live_abc123def456xyz789"

LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET_HERE"
                             ↓ PASTE YOUR WEBHOOK SECRET HERE
LOVEBLE_WEBHOOK_SECRET = "whsec_live_12345abc789xyz"

LOVEBLE_SHOP_ID = "YOUR_SHOP_ID_HERE"
                      ↓ PASTE YOUR SHOP ID HERE
LOVEBLE_SHOP_ID = "shop_987654321"
```

Then find **PRODUCTS** section and update `loveble_id` for each coffee:
```python
PRODUCTS = {
    "cappuccino": {
        "loveble_id": "prod_2a3b4c5d_cappuccino"  # Update this!
    },
    "espresso": {
        "loveble_id": "prod_1x9y8z7w_espresso"    # Update this!
    },
    # ... update all 8 products
}
```

### Step 3: Configure Webhook in Loveble (3 minutes)
In **Loveble Dashboard**:

1. Go to **Settings → Webhooks**
2. Click **Add Webhook**
3. Enter:
   - **URL:** `http://YOUR_SERVER_IP:8443/webhook/loveble`
     - Replace `YOUR_SERVER_IP` with your server's IP address
     - Example: `http://192.168.1.100:8443/webhook/loveble`
     - Or if you have domain: `https://yourserver.com:8443/webhook/loveble`
   - **Secret:** Paste your webhook secret from Loveble
4. **Select Events:**
   - ✅ `order_paid` (Required!)
   - ✅ `order_completed` (Required!)
   - ❌ order_created (Optional)
5. Click **Save**

### Step 4: Start the Bot (1 minute)
```bash
cd coffee_system
python main.py
```

Wait for this message:
```
Running on http://0.0.0.0:8443
```

### Step 5: Test It Works (2 minutes)
**Option A: Test with real sale**
1. Make a test sale on Loveble POS
2. You should get Telegram notification within 2 seconds
3. Check `/stats` endpoint: `curl http://localhost:8443/stats`

**Option B: Test with fake webhook (advanced)**
See `LOVEBLE_QUICK_START.md` → "Test webhook manually"

---

## 📊 What Bot Tracks

### Automatic Daily Tracking
At **23:00 every day**, bot sends:
```
📊 KUNLIK DIAGNOSTIKA

📈 Today's Stats:
  • Total sales: 15 products
  • Revenue: 125,000 som

📦 Products sold:
  • Cappuccino: 5 × 7,000 = 35,000 som
  • Espresso: 3 × 5,000 = 15,000 som
  • Latte: 4 × 8,000 = 32,000 som
  • Americano: 2 × 6,000 = 12,000 som
  • Mocha: 1 × 9,000 = 9,000 som

📦 Current stock:
  • Cappuccino: 7 left
  • Espresso: 9 left
  • Latte: 8 left
  • Americano: 10 left
  • Mocha: 11 left

⚠️ LOW STOCK:
  • Cappuccino: only 7 left (alert when < 5)
```

### Weekly Report (Friday 23:05)
- Total sales for the week
- Best sellers
- Revenue summary

### Monthly Report (1st day 23:10)
- Full month statistics
- Trends
- Total revenue

### On-Demand Reports (Commands)
```
/daily   - Today's sales
/weekly  - This week's sales
/monthly - This month's sales
/stock   - Current inventory
/help    - Command list
```

---

## 🔐 Security Features

### 1. Webhook Signature Verification (HMAC-SHA256)
```
Loveble sends:
  Payload: {"order_id": "123", "items": [...]}
  Signature: "abc123def456..." (calculated with secret)

Bot verifies:
  1. Recalculate signature using WEBHOOK_SECRET
  2. Compare with received signature
  3. ✅ If match → Webhook is really from Loveble
  4. ❌ If no match → REJECT (someone is faking it!)
```

### 2. Admin ID Verification
Only admin (specified in config) gets notifications

### 3. Database Transaction Safety
If any error occurs:
- Changes are ROLLED BACK
- Sale is NOT recorded
- Error is logged
- Admin is notified

---

## 📱 Telegram Commands

Send these in Telegram chat with bot:

```
/start              - Start bot & see menu
/daily              - Today's sales summary
/weekly             - This week's stats
/monthly            - This month's stats
/stock              - Current inventory levels
/low_stock          - Products with low stock
/help               - Command list
```

Buttons in bot:
```
[📊 Daily Report]  [📈 Weekly Report]
[📅 Monthly Report] [📦 Stock Status]
[⚠️ Low Stock]     [❓ Help]
```

---

## 🚨 Troubleshooting

### Bot Not Receiving Webhooks

**Check 1: Is bot running?**
```bash
curl http://localhost:8443/health
# Should return: {"status":"ok","bot":"running"}
```

**Check 2: Is webhook URL correct in Loveble?**
```
Should be: http://YOUR_IP:8443/webhook/loveble
```

**Check 3: Is firewall blocking port 8443?**
```bash
# Windows: Check Windows Defender Firewall
# Linux: sudo ufw status
```

**Check 4: Are credentials correct?**
```python
# config.py line 14-15:
LOVEBLE_WEBHOOK_SECRET = "..."  # Must EXACTLY match Loveble secret!
```

### Signature Error: "Invalid webhook signature"

**Solution:**
1. Copy exact webhook secret from Loveble
2. Paste into config.py: `LOVEBLE_WEBHOOK_SECRET = "..."`
3. Restart bot: `python main.py`

### Product Not Found in Database

**Problem:** Bot logs "Product not found: prod_xyz"

**Solution:**
1. Go to Loveble: Products section
2. Find the product ID
3. Update config.py with correct `loveble_id`:
```python
PRODUCTS = {
    "cappuccino": {
        "loveble_id": "prod_2a3b4c5d_cappuccino"  # Correct ID!
    }
}
```

### Bot Crashes on Startup

**Check logs:**
```bash
tail -f coffee_bot.log
```

**Common reasons:**
- Missing dependency: Run `pip install -r requirements.txt`
- Wrong config: Check LOVEBLE_* values in config.py
- Port 8443 in use: Change port in config.py and Loveble webhook

---

## 📁 Important Files

```
coffee_system/
├── main.py                      ← Start bot: python main.py
├── config.py                    ← ⚙️ EDIT THIS! Put your credentials here
├── coffee_bot.log               ← Check this for errors
├── coffee.db                    ← SQLite database (auto-created)
├── requirements.txt             ← Python packages
├── LOVEBLE_INTEGRATION.md       ← Full detailed guide
├── LOVEBLE_QUICK_START.md       ← Quick reference
├── LOVEBLE_EXAMPLES.md          ← Real examples & diagrams
├── backend/
│   ├── loveble_api.py           ← Processes Loveble webhooks
│   ├── database.py              ← Saves sales to database
│   ├── scheduler.py             ← Daily/weekly/monthly reports
│   └── models.py                ← Data structures
└── bot/
    ├── bot.py                   ← Telegram bot setup
    └── handlers.py              ← Bot commands & responses
```

---

## ✅ Checklist Before Going Live

- [ ] All 4 Loveble credentials copied to config.py
- [ ] All 8 product loveble_ids updated in config.py
- [ ] Webhook URL set in Loveble: `http://YOUR_IP:8443/webhook/loveble`
- [ ] Webhook secret set in Loveble (matches config.py)
- [ ] Bot starts without errors: `python main.py`
- [ ] Test webhook returns 200 OK
- [ ] Telegram admin receives test notification
- [ ] Bot commands work: /start, /daily, etc.
- [ ] Daily diagnostic runs at 23:00
- [ ] Database shows sales: check `/stats` endpoint
- [ ] Log file shows no errors: `coffee_bot.log`

---

## 📞 Quick Reference

| Component | Status | What to do |
|-----------|--------|-----------|
| **Loveble Connection** | ⚠️ Setup needed | Get API key, shop ID, webhook secret |
| **Credentials** | ⚠️ Setup needed | Fill config.py with Loveble info |
| **Webhook** | ⚠️ Setup needed | Set URL in Loveble: port 8443 |
| **Products** | ⚠️ Setup needed | Update loveble_ids in config.py |
| **Bot** | ✅ Ready | Run: `python main.py` |
| **Database** | ✅ Ready | Auto-creates coffee.db |
| **Notifications** | ✅ Ready | Sends Telegram messages |
| **Reports** | ✅ Ready | Daily/weekly/monthly auto-generated |

---

## 🎯 Success = When This Happens

1. **You make a sale on Loveble POS**
2. **Within 2 seconds**, you get Telegram message:
   ```
   ☕ SOTUV HAQIDA XABAR
   📦 Cappuccino × 2
   💰 14,000 som
   🧾 Check ID: ORD-123
   ```
3. **Bot logs show:** `Order ORD-123 processed successfully`
4. **Database updated:** Stock decreased, sale recorded
5. **At 23:00**, you get daily diagnostic

**If all this happens = ✅ WORKING PERFECTLY!**

---

## 🔗 Additional Resources

- **Full Guide:** See `LOVEBLE_INTEGRATION.md`
- **Quick Start:** See `LOVEBLE_QUICK_START.md`
- **Examples:** See `LOVEBLE_EXAMPLES.md`
- **Bot Logs:** Check `coffee_bot.log`
- **Health Check:** `curl http://localhost:8443/health`

---

## 🆘 Still Having Issues?

1. **Check coffee_bot.log:**
   ```bash
   tail -f coffee_bot.log
   ```

2. **Check config.py:**
   - Are all Loveble credentials filled?
   - Are all product loveble_ids correct?

3. **Check Loveble settings:**
   - Is webhook URL correct?
   - Is webhook secret correct?
   - Are order_paid and order_completed events enabled?

4. **Check network:**
   - Can you ping Loveble API?
   - Is port 8443 open?
   - Is firewall blocking anything?

5. **Test webhook manually:**
   - See `LOVEBLE_QUICK_START.md` → "Debugging Commands"

---

**Last Update:** January 27, 2026
**Bot Status:** ✅ Running and Operational
**Version:** 1.0.0
