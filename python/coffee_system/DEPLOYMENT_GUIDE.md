# Coffee System - Production Deployment Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd coffee_system
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file in project root:
```bash
# Telegram Bot (get from @BotFather on Telegram)
BOT_TOKEN=<your-46-character-token>
CHAT_ID=<your-telegram-chat-or-channel-id>

# Click Payment (from Click merchant account)
CLICK_SECRET_KEY=<your-click-secret-key>

# Admin access (set a strong random password)
ADMIN_TOKEN=<generate-strong-token-32-chars-minimum>
```

**Generate strong ADMIN_TOKEN:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run the System
```bash
# Start FastAPI server + Telegram bot
python main.py
```

Expected output:
```
INFO - Starting Uvicorn server on http://localhost:8000
INFO - Telegram bot connected (chat: XXXXX)
INFO - Daily scheduler initialized (reports at 23:00 Tashkent time)
```

---

## Testing Before Production

### Test 1: Telegram Connection
```bash
# Check if bot is receiving messages
curl "http://localhost:8000/admin/today?token=YOUR_ADMIN_TOKEN"
# Should return today's stats (or empty dict)
```

### Test 2: Click Webhook
```bash
# Simulate Click payment (will fail signature but tests endpoint)
curl -X POST http://localhost:8000/click/webhook \
  -H "Content-Type: application/json" \
  -H "X-Click-Signature: test" \
  -d '{"order_id": "test-123", "payment_status": "paid"}'

# Expected response:
# {"status": "invalid_signature"}  <- returns 200, not error
```

### Test 3: Duplicate Protection
```bash
# Create same order twice (should detect duplicate)
python test_production.py
# This runs full test suite
```

---

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `BOT_TOKEN` | Yes | `123456789:ABCdef...` | Get from @BotFather |
| `CHAT_ID` | Yes | `1234567890` or `-100123...` | Group ID for notifications |
| `CLICK_SECRET_KEY` | Yes | `test-secret-key` | Provided by Click merchant |
| `ADMIN_TOKEN` | Yes | `random-strong-token-32+chars` | Generate new, keep secret |

---

## File Structure

```
coffee_system/
├── main.py                        # FastAPI app + scheduler entry point
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (NOT in git)
│
├── backend/
│   ├── main.py                   # FastAPI routes (hardened)
│   ├── security.py               # HMAC signature verification
│   ├── telegram.py               # Bot message/document sending (rate-limited)
│   ├── click_webhook.py          # Payment webhook processor (idempotent)
│   ├── storage.py                # JSON order storage (thread-safe)
│   ├── stats.py                  # Daily statistics (thread-safe)
│   ├── pdf.py                    # PDF receipt generation
│   ├── models.py                 # Pydantic data models
│   ├── scheduler.py              # APScheduler daily reports
│   └── bot.py                    # Aiogram bot handler
│
├── data/                         # Created automatically
│   ├── orders.json               # Order tracking (prevents duplicates)
│   ├── daily_stats.json          # Daily sales statistics
│   └── receipts/                 # PDF receipts
│
├── SECURITY_HARDENING_GUIDE.md   # Security audit & features
├── test_production.py            # Test suite
└── DEPLOYMENT_GUIDE.md           # This file
```

---

## Monitoring & Troubleshooting

### Check System Status
```bash
# Verify server is running
curl http://localhost:8000/admin/today?token=YOUR_TOKEN

# Check logs
tail -f logs.json | jq
```

### Common Issues

**Issue: "Telegram bot not responding"**
- Check BOT_TOKEN is correct (46 chars, from @BotFather)
- Verify CHAT_ID is numeric and bot is member of chat
- Run: `python -c "from backend.telegram import bot; print(bot.session)"`

**Issue: "Click webhook returns 403"**
- Verify signature is correct (HMAC-SHA256)
- Check CLICK_SECRET_KEY matches merchant account
- Webhook should return 200 even for invalid signatures (it does now)

**Issue: "Admin endpoint returns 403 on valid token"**
- Verify token is exactly as set in .env (no spaces)
- Token uses constant-time comparison (should never be timing-dependent)
- Try: `python -c "import hmac; print(hmac.compare_digest('token1', 'token2'))"`

**Issue: "PDF generation fails"**
- Check `data/receipts/` directory exists and is writable
- Verify reportlab is installed: `pip list | grep reportlab`
- PDF failures don't crash webhook (webhook returns 200)

**Issue: "Daily report doesn't send at 23:00"**
- Verify timezone is Asia/Tashkent: `python -c "from pytz import timezone; tz = timezone('Asia/Tashkent'); print(tz)"`
- Check scheduler is running: `tail -f logs.json | grep -i scheduler`
- Trigger manually: `python -c "from backend.scheduler import send_daily_report; asyncio.run(send_daily_report())"`

---

## Load Testing

### Stress Test: 100 Concurrent Requests
```bash
# Test with Apache Bench
ab -n 100 -c 10 \
  -H "X-Click-Signature: test" \
  -p payload.json \
  http://localhost:8000/click/webhook

# Expected: All return 200, no crashes
```

### Stress Test: Duplicate Order Handling
```bash
# Send same order 10 times (tests idempotency)
for i in {1..10}; do
  curl -X POST http://localhost:8000/click/webhook \
    -H "X-Click-Signature: <valid-sig>" \
    -d '{"order_id": "stress-1", ...}'
done

# Expected: First = "ok", rest = "duplicate"
```

---

## Security Checklist

Before deploying to production:

- [ ] Set ADMIN_TOKEN to strong random value (32+ chars)
- [ ] CLICK_SECRET_KEY is correct and never committed to git
- [ ] BOT_TOKEN is valid (test with @BotFather)
- [ ] CHAT_ID exists and bot is member of that chat
- [ ] `.env` file is in `.gitignore` (never commit secrets)
- [ ] HTTPS/TLS is enabled at deployment platform level
- [ ] Firewall allows only necessary ports (8000 for FastAPI)
- [ ] Database backups scheduled (for data/receipts/ and data/daily_stats.json)
- [ ] Log rotation configured (logs.json will grow large)
- [ ] Monitor logs for "ERROR" or "WARNING" messages
- [ ] Test Click webhook signature verification
- [ ] Test duplicate order detection (send same order twice)
- [ ] Test admin access with wrong token (should delay 500ms)

---

## Production Commands

### Start Production Server
```bash
# With Uvicorn (auto-reload disabled for production)
python -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --no-access-log

# Or use systemd (recommended)
# See systemd-service.conf below
```

### Systemd Service (Linux)
Create `/etc/systemd/system/coffee-system.service`:
```ini
[Unit]
Description=Coffee System - FastAPI + Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/coffee_system
Environment="PATH=/home/user/venv/bin"
ExecStart=/home/user/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable coffee-system
sudo systemctl start coffee-system
sudo systemctl status coffee-system
```

### Docker (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
```

Run:
```bash
docker build -t coffee-system .
docker run \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  coffee-system
```

---

## Backup Strategy

### Daily Backups
```bash
#!/bin/bash
# backup.sh
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/
# Upload to cloud storage (S3, Azure Blob, etc)
```

Run daily:
```bash
0 2 * * * /home/user/coffee_system/backup.sh
```

### What to Backup
- `data/orders.json` - Order tracking (prevents duplicates)
- `data/daily_stats.json` - Sales statistics
- `data/receipts/` - PDF receipts
- `.env` file (keep secure!)

---

## Performance Tips

### For Low Traffic (< 100 requests/day)
- Single Uvicorn worker is fine
- No need for load balancer
- JSON file storage is adequate

### For High Traffic (> 1000 requests/day)
- Increase Uvicorn workers: `--workers 4`
- Consider Redis for rate limiting
- Migrate to PostgreSQL for concurrent writes
- Use CDN for static assets

### Telegram Rate Limiting
Current implementation uses Semaphore(5):
- Limits to 5 concurrent Telegram API calls
- Excess calls queue automatically
- Prevents hitting Telegram rate limits

To adjust:
```python
# In backend/telegram.py
_message_semaphore = asyncio.Semaphore(10)  # Increase if needed
```

---

## Logs

Logs are written to `logs.json` in JSON format:
```json
{
  "timestamp": "2024-01-15T14:30:45.123Z",
  "level": "INFO",
  "message": "Order 123 processed successfully",
  "source": "backend.click_webhook"
}
```

View logs:
```bash
# Pretty print
tail -f logs.json | jq

# Filter by level
tail -f logs.json | jq 'select(.level == "ERROR")'

# Watch for security issues
tail -f logs.json | jq 'select(.message | contains("Unauthorized") or contains("Invalid"))'
```

---

## Upgrade Process

To deploy new code:

1. **Backup current system**
   ```bash
   cp -r data data.backup
   ```

2. **Pull new code**
   ```bash
   git pull
   pip install -r requirements.txt
   ```

3. **Test new code**
   ```bash
   python test_production.py
   ```

4. **Restart service**
   ```bash
   sudo systemctl restart coffee-system
   ```

5. **Verify**
   ```bash
   curl "http://localhost:8000/admin/today?token=YOUR_TOKEN"
   tail -f logs.json
   ```

---

## Support & Debugging

### Enable Debug Logging
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Click Signature
```python
import hmac
import hashlib

payload = '{"order_id": "123"}'
secret = "your-secret-key"
signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

print(f"Expected signature: {signature}")
# Compare with X-Click-Signature header
```

### Debug Telegram
```python
import asyncio
from backend.telegram import send_message

async def test():
    await send_message("Test message from Python")

asyncio.run(test())
```

---

## Summary

**Production Ready:** ✅
- Security hardened (constant-time comparison, brute-force protection)
- Reliable (idempotency, error isolation, atomic writes)
- Observable (comprehensive logging)
- Scalable (Telegram queue, thread-safe storage)

**Next Steps:**
1. Set environment variables in `.env`
2. Run `test_production.py` to verify setup
3. Deploy to production
4. Monitor logs for 24 hours
5. Set up automated backups
