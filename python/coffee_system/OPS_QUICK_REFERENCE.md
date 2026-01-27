# Coffee System - Operations Quick Reference

**TL;DR: See commands section below**

---

## Commands Reference

### Start System
```bash
# Development (auto-reload enabled)
python main.py

# Production (no auto-reload)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Test System
```bash
# Run full test suite
python test_production.py

# Test webhook only
curl -X POST http://localhost:8000/click/webhook \
  -H "X-Click-Signature: invalid" \
  -d '{}'
# Expected: {"status": "invalid_signature"}

# Test admin endpoint
curl "http://localhost:8000/admin/today?token=YOUR_ADMIN_TOKEN"
# Expected: {"products": {...}, "total": 12345}
```

### View Logs
```bash
# All logs
tail -f logs.json | jq

# Errors only
tail -f logs.json | jq 'select(.level == "ERROR")'

# Warnings only
tail -f logs.json | jq 'select(.level == "WARNING")'

# Security issues
tail -f logs.json | jq 'select(.message | contains("Unauthorized") or contains("Invalid"))'
```

### Backup Data
```bash
# Backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf backup-20240115.tar.gz
```

---

## Common Issues

### "Webhook returns 403"
```
❌ Problem: Signature verification failing
✅ Solution:
1. Verify CLICK_SECRET_KEY in .env
2. Check payload is not modified
3. Run: python -c "import hmac; print(hmac.compare_digest('a', 'b'))"
```

### "Admin endpoint returns 403"
```
❌ Problem: Token rejected
✅ Solution:
1. Verify ADMIN_TOKEN in .env (exact match, no spaces)
2. Check token is 32+ characters
3. Wait 500ms - first attempt has brute-force delay
```

### "Telegram not responding"
```
❌ Problem: Messages not reaching chat
✅ Solution:
1. Verify BOT_TOKEN (46 chars, from @BotFather)
2. Verify CHAT_ID (numeric, bot is member)
3. Test: python -c "from backend.telegram import send_message; ..."
4. Check Semaphore(5) - queue might be full, retry in 1s
```

### "PDF generation fails"
```
❌ Problem: Receipts not created
✅ Solution:
1. Check data/receipts/ exists and is writable
2. Verify reportlab installed: pip list | grep reportlab
3. PDF failures don't crash webhook (webhook returns 200 anyway)
```

---

## Monitoring Dashboard

### Health Check
```bash
# All green?
curl "http://localhost:8000/admin/today?token=YOUR_TOKEN" && echo "✓ System OK"
```

### Performance Metrics
```bash
# Request count today
tail -f logs.json | jq 'select(.message | contains("processed successfully"))' | wc -l

# Error count
tail -f logs.json | jq 'select(.level == "ERROR")' | wc -l

# Average response time (if logged)
# Check logs.json for timing information
```

### Load Status
```bash
# Active processes
ps aux | grep main.py

# Memory usage
free -h

# Disk usage
df -h data/
```

---

## Configuration

### .env Template
```bash
# Telegram
BOT_TOKEN=<from @BotFather>
CHAT_ID=<your chat ID>

# Click
CLICK_SECRET_KEY=<from merchant account>

# Admin
ADMIN_TOKEN=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
```

### Required Permissions
```bash
# Directory permissions
mkdir -p data/receipts
chmod 755 data
chmod 755 data/receipts

# File permissions (automatic)
# logs.json - 644 (created by logging module)
# .env - 600 (never readable by world)
```

---

## Performance Tuning

### For Low Traffic (< 100 orders/day)
```bash
# Default settings are fine
# Run single worker
python -m uvicorn backend.main:app --workers 1
```

### For Medium Traffic (100-1000 orders/day)
```bash
# Use 2 workers
python -m uvicorn backend.main:app --workers 2
```

### For High Traffic (> 1000 orders/day)
```bash
# Use 4 workers and consider upgrading storage
python -m uvicorn backend.main:app --workers 4
# Recommendation: Migrate to PostgreSQL
```

### Telegram Rate Limiting
```python
# In backend/telegram.py
_message_semaphore = asyncio.Semaphore(10)  # Default is 5

# Increase if getting rate limit errors
# Decrease if want to be more conservative
```

---

## Troubleshooting Tree

```
System not starting?
├── ImportError?
│   └── pip install -r requirements.txt
├── ADMIN_TOKEN not set?
│   └── Create .env file with ADMIN_TOKEN
└── Port 8000 in use?
    └── lsof -i :8000 and kill process

System running but webhook fails?
├── Returns 403?
│   └── Check CLICK_SECRET_KEY matches Click account
├── Returns 500?
│   └── Check logs.json for details
└── Telegram not notifying?
    └── Check BOT_TOKEN and CHAT_ID in .env

Admin endpoint not working?
├── Returns 403?
│   └── Wait 500ms (brute-force protection)
│   └── Check ADMIN_TOKEN is exact match
└── Returns 500?
    └── Check stats.json is readable

Data not persisting?
├── Orders missing?
│   └── Check data/orders.json exists
├── Stats missing?
│   └── Check data/daily_stats.json exists
└── Both missing?
    └── Check data/ directory has write permissions
```

---

## Security Checks (Weekly)

```bash
# Check for unauthorized access attempts
grep "Unauthorized admin access" logs.json | wc -l

# Check for invalid signatures
grep "Invalid signature" logs.json | wc -l

# Check for JSON corruption
grep "JSON corruption" logs.json | wc -l

# Check for errors
grep "ERROR" logs.json | tail -20
```

---

## Backup & Disaster Recovery

### Daily Backup
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/coffee-system"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup-$DATE.tar.gz data/ .env logs.json

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Install in crontab:
```bash
0 2 * * * /home/user/coffee-system/backup.sh
```

### Emergency Restore
```bash
# Stop system
systemctl stop coffee-system

# Restore backup
tar -xzf backup-20240115.tar.gz

# Restart system
systemctl start coffee-system
```

---

## Deployment Checklist (Before Going Live)

- [ ] .env file created with all variables
- [ ] BOT_TOKEN verified (test with Telegram)
- [ ] CLICK_SECRET_KEY verified (test with Click)
- [ ] ADMIN_TOKEN generated and stored securely
- [ ] test_production.py passes all tests
- [ ] logs.json is empty/clean
- [ ] data/ directory exists and is writable
- [ ] Backup script scheduled
- [ ] Monitoring configured
- [ ] Team trained on operations

---

## Help & Support

### Debug Mode
```python
# Add to main.py temporarily
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Generate Test Data
```python
# Create test order
from backend.storage import save_order
save_order("test-order-123")

# Verify storage
from pathlib import Path
print(Path("data/orders.json").read_text())
```

### Manual Report Trigger
```bash
# Send daily report immediately (without waiting for 23:00)
python -c "
import asyncio
from backend.scheduler import send_daily_report
asyncio.run(send_daily_report())
"
```

---

**Remember:**
- Always backup before any changes
- Monitor logs daily for errors
- Test changes in development first
- Keep ADMIN_TOKEN and CLICK_SECRET_KEY secure
- Report bugs with full logs and reproduction steps
