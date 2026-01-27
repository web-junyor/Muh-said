# QUICK START - SAID COFFEE SYSTEM

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
cd coffee_system
pip install -r requirements.txt
```

### Step 2: Configure Secrets (1 min)
```bash
cp .env.example .env
```

Edit `.env` with your values:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_ADMIN_CHAT_ID
CLICK_SECRET_KEY=YOUR_CLICK_API_SECRET
ADMIN_TOKEN=your_strong_random_admin_token
```

### Step 3: Initialize Data (30 sec)
```bash
mkdir -p data/receipts
```

### Step 4: Run Tests (30 sec)
```bash
python test_integration.py
```

Should show: "All tests passed! System is ready."

### Step 5: Start Server (instant)
```bash
python -m backend.main
```

Server runs on `http://localhost:8000`

---

## Verify It Works

### 1. Check Admin Endpoint
```bash
curl "http://localhost:8000/admin/today?token=YOUR_ADMIN_TOKEN"
```

Should return today's stats (even if empty):
```json
{}
```

### 2. Test Telegram Connection
Wait 10 seconds after starting server. If Telegram bot token is valid, you should see bot activity in logs.

### 3. Check File Permissions
```bash
ls -la data/
```

Should see:
```
orders.json         (processed order IDs)
daily_stats.json    (daily statistics)
receipts/           (PDF receipts directory)
```

---

## Next Steps

1. **Test with Click Gateway**
   - Point Click webhook to: `http://YOUR_SERVER:8000/click/webhook`
   - Set X-Click-Signature header with HMAC-SHA256(body + secret)

2. **Set Up Monitoring**
   - Monitor `/admin/today` endpoint hourly
   - Check `data/receipts/` directory size daily
   - Review logs for errors

3. **Configure Daily Reporting**
   - System automatically sends daily report at 23:00 Uzbekistan time
   - Check environment variable `TZ` is set correctly

4. **Production Deployment**
   - Read `PRODUCTION_GUIDE.md` for detailed instructions
   - Follow `DEPLOYMENT_CHECKLIST.txt` before going live

---

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt --upgrade
```

**Bot not sending messages:**
- Verify BOT_TOKEN is correct (ask @BotFather)
- Check CHAT_ID is not empty
- CHAT_ID should be negative for groups

**Webhook signature errors:**
- Verify CLICK_SECRET_KEY matches Click dashboard
- Check signature header is `X-Click-Signature`
- Signature = SHA256(body + secret_key)

**PDF generation fails:**
- Check `data/receipts/` directory exists: `mkdir -p data/receipts`
- Verify write permissions: `chmod 755 data/`
- Check disk space available

**Daily report not sent:**
- Verify system time is correct
- Check TZ environment variable is set
- Look for "Daily report sent successfully" in logs

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application & scheduler |
| `backend/click_webhook.py` | Handle Click payments |
| `backend/models.py` | Data contracts (Pydantic) |
| `backend/security.py` | Signature verification |
| `backend/storage.py` | Idempotency & order log |
| `backend/stats.py` | Daily statistics |
| `backend/pdf.py` | Receipt generation |
| `backend/telegram.py` | Bot notifications |
| `.env` | Secret configuration |
| `data/orders.json` | Processed order IDs |
| `data/daily_stats.json` | Daily sales data |
| `data/receipts/` | PDF receipt files |

---

## API Quick Reference

### Get Today's Statistics
```bash
GET /admin/today?token=YOUR_ADMIN_TOKEN

Response:
{
  "2026-01-27": {
    "products": {
      "Espresso": 5,
      "Mocha": 3
    },
    "total": 125000
  }
}
```

### Click Webhook (from Click gateway)
```bash
POST /click/webhook

Headers:
- X-Click-Signature: (HMAC-SHA256)
- Content-Type: application/json

Body:
{
  "order_id": "order_123",
  "merchant_trans_id": "mec_456",
  "payment_status": "paid",
  "items": [
    {
      "product_id": "p1",
      "product_name": "Espresso",
      "quantity": 2,
      "price": 12000,
      "total_price": 24000
    }
  ],
  "total_amount": 24000,
  "sign_string": "...",
  "sign_time": "2026-01-27 14:30:00"
}
```

---

## Common Commands

```bash
# Start server
python -m backend.main

# Run integration tests
python test_integration.py

# Check Python version
python --version

# Install packages
pip install -r requirements.txt

# View statistics
cat data/daily_stats.json | python -m json.tool

# View recent receipts
ls -lh data/receipts/ | tail -10

# Check running processes
ps aux | grep backend.main
```

---

## Support

For detailed documentation, see:
- `PRODUCTION_GUIDE.md` - Full production setup
- `ARCHITECTURE.md` - System design & data flow
- `DEPLOYMENT_CHECKLIST.txt` - Pre-production verification

For issues, check:
1. `.env` file is configured correctly
2. All dependencies installed: `pip install -r requirements.txt`
3. Data directory exists: `mkdir -p data/receipts`
4. Logs show no errors during startup

---

**Version:** 1.0.0
**Status:** Production Ready
**Ready to Deploy:** ✓
