# 🚀 SETUP INSTRUQIYALARI - Coffee Shop Bot Loveble Integration

## 📋 Shartlar

- Python 3.9 yoki undan yuqori
- Telegram Bot Token (BotFather dan)
- Loveble API credentials
- Linux/Windows/Mac server

---

## 1️⃣ STEP 1: Repository Download va Setup

```bash
# Repository klonlash
git clone <your-repo-url>
cd coffee_system

# Virtual environment yaratish
python -m venv venv

# Activation
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2️⃣ STEP 2: Configuration

### config.py ni tahrirlash:

```bash
# config.py ochish
nano config.py  # Linux/Mac
# yoki
notepad config.py  # Windows
```

**O'zgartirilishi kerak bo'lgan qisimlar:**

```python
# 🔴 REQUIRED - HOZIR QAYTA KIRITISH KERAK:

# 1. Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
# BotFather dan oling: https://t.me/BotFather
# /newbot -> nomi -> username -> TOKEN olish

# 2. Admin Telegram ID
TELEGRAM_ADMIN_ID = 123456789
# @userinfobot ga xabar bering, ID olish

# 3. Loveble API Key
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY"
# Loveble Dashboard -> Settings -> API

# 4. Loveble Shop ID
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID"
# Loveble Dashboard da topiladi

# 5. Webhook Secret (Signature verification)
LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET"
# Loveble Dashboard -> Webhooks da yaratish

# 🟡 OPTIONAL (Production uchun):

# Webhook URL (domain kerak)
WEBHOOK_URL = "https://yourdomain.com/webhook/loveble"

# Webhook Port
WEBHOOK_PORT = 8443
```

### .env fayli yaratish (TALAB EMAS, lekin tavsiya etiladi):

```bash
# .env fayl yaratish
cat > .env << EOF
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_ADMIN_ID=YOUR_ID_HERE
LOVEBLE_API_KEY=YOUR_LOVEBLE_KEY
LOVEBLE_SHOP_ID=YOUR_SHOP_ID
LOVEBLE_WEBHOOK_SECRET=YOUR_SECRET
WEBHOOK_URL=https://yourdomain.com/webhook/loveble
EOF
```

---

## 3️⃣ STEP 3: Database Preparation

```bash
# Database avtomatik yaratiladi, lekin test qilish:
python -c "from backend.database import db; products = db.get_all_products(); print(f'✅ {len(products)} mahsulot topildi')"

# Output bo'lishi kerak:
# ✅ 8 mahsulot topildi
```

---

## 4️⃣ STEP 4: Test Run (Development Mode)

```bash
# Botni ishga tushirish (polling mode)
python main.py

# Kutish va xabarlar:
# INFO - Database initialized successfully
# INFO - Diagnostics scheduler started successfully
# INFO - Starting Telegram Bot...
# INFO - Bot started!
```

### Test qilish:
1. Telegram da botga `/start` buyrug'ini yuboring
2. Buttons ko'rinishi kerak
3. Logs okno da ma'lumotlar chiqishi kerak

---

## 5️⃣ STEP 5: Loveble Webhook Registration

### A. Localhost Test (tunneling bilan):

```bash
# Ngrok o'rnatish (test uchun)
# https://ngrok.com dan download qiling

# Terminal 1: Flask server ishga tushirish
python main.py

# Terminal 2: Ngrok tunnel yaratish
ngrok http 8443
# Javob: https://xyz.ngrok.io

# Loveble Dashboard ga URL kiritish:
# https://xyz.ngrok.io/webhook/loveble
```

### B. Production Server (Real Domain):

1. **Loveble Dashboard ga kirish** - Settings -> Webhooks
2. **Webhook URL kiritish:**
   ```
   https://yourdomain.com/webhook/loveble
   ```
3. **Secret key kiritish** - config.py dan copy
4. **Test qilish:**
   ```bash
   curl -X POST https://yourdomain.com/webhook/loveble \
     -H "Content-Type: application/json" \
     -H "X-Loveble-Signature: test" \
     -d '{"event_type":"order_paid","order_id":"test123"}'
   ```

---

## 6️⃣ STEP 6: Production Deployment

### Option A: Gunicorn (Tavsiya etilgan)

```bash
# Gunicorn o'rnatish (requirements.txt da bor)
pip install gunicorn

# Ishga tushirish
gunicorn --workers 4 \
         --worker-class gevent \
         --bind 0.0.0.0:8443 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
         main:app

# Background da ishga tushirish
nohup gunicorn --workers 4 --worker-class gevent --bind 0.0.0.0:8443 main:app > bot.log 2>&1 &
```

### Option B: Systemd Service (Linux)

```bash
# /etc/systemd/system/coffee-bot.service yaratish
sudo nano /etc/systemd/system/coffee-bot.service
```

**Fayl content:**
```ini
[Unit]
Description=Coffee Shop Bot with Loveble Integration
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/coffee_system
ExecStart=/var/www/coffee_system/venv/bin/gunicorn --workers 4 --worker-class gevent --bind 0.0.0.0:8443 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable qilish:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable coffee-bot
sudo systemctl start coffee-bot
sudo systemctl status coffee-bot
```

### Option C: Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8443

CMD ["gunicorn", "--workers", "4", "--worker-class", "gevent", "--bind", "0.0.0.0:8443", "main:app"]
```

**Ishga tushirish:**
```bash
docker build -t coffee-bot .
docker run -d -p 8443:8443 -v $(pwd)/coffee.db:/app/coffee.db coffee-bot
```

---

## 7️⃣ STEP 7: Nginx Configuration (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout sozlamalar
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Reload Nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 8️⃣ STEP 8: SSL Certificate (HTTPS)

```bash
# Let's Encrypt bilan SSL
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Certificate olish
sudo certbot certonly --nginx -d yourdomain.com

# Nginx config update:
sudo certbot --nginx
```

---

## 9️⃣ STEP 9: Logs va Monitoring

### Logs ko'rish:

```bash
# Real-time logs
tail -f coffee_bot.log

# Loveble webhook logs
tail -f coffee_bot.log | grep webhook

# Database logglar
sqlite3 coffee.db "SELECT * FROM loveble_webhooks LIMIT 5;"

# Sales logglar
sqlite3 coffee.db "SELECT product_name, quantity, total_price FROM sales ORDER BY timestamp DESC LIMIT 10;"
```

### Health Check:

```bash
# Bot status
curl http://localhost:8443/health

# Stats
curl http://localhost:8443/stats
```

---

## 🔟 STEP 10: Backup va Recovery

### Automatic Backup Script:

```bash
# backup.sh yaratish
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

DATE=$(date +%Y%m%d_%H%M%S)
cp coffee.db $BACKUP_DIR/coffee_db_$DATE.db
tar -czf $BACKUP_DIR/coffee_system_$DATE.tar.gz \
    --exclude=venv \
    --exclude=.git \
    --exclude=__pycache__ \
    .

# Eski backuplarni o'chirish (30 kundan eski)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
./backup.sh
```

### Cron Job (kuniga bir bor):

```bash
# Crontab tahriri
crontab -e

# Qo'shish:
0 2 * * * /var/www/coffee_system/backup.sh
```

---

## ✅ Verification Checklist

```bash
# 1. Dependencies installed
pip list | grep -E "aiogram|Flask|requests|APScheduler|pydantic"

# 2. Config setup
python -c "from config import *; print('✅ Config loaded')"

# 3. Database OK
python -c "from backend.database import db; print(f'✅ {len(db.get_all_products())} products')"

# 4. Loveble client OK
python -c "from backend.loveble_api import loveble_client; print('✅ Loveble client ready')"

# 5. Bot token valid
python -c "from bot.bot import bot; print('✅ Bot initialized')"

# 6. Scheduler OK
python -c "from backend.scheduler import diagnostics_scheduler; print('✅ Scheduler ready')"

# 7. Run test
python main.py &
sleep 5
curl http://localhost:8443/health
kill %1
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **ModuleNotFoundError** | `pip install -r requirements.txt` qayta ishga tushiring |
| **Database locked** | `ps aux \| grep main` -> kill process -> restart |
| **Bot not responding** | Token va Admin ID tekshiring |
| **Webhook not receiving** | Loveble dashboard da URL tekshiring, logs ko'ring |
| **Port 8443 busy** | `sudo lsof -i :8443` -> kill process |
| **Permission denied** | `chmod +x main.py` yoki `sudo` bilan ishga tushiring |

---

## 📞 Quick Support

**Logs ko'rish:**
```bash
tail -f coffee_bot.log | head -50
```

**Database reset (daxiyat!):**
```bash
rm coffee.db
python main.py  # Database qayta yaratiladi
```

**Bot restart:**
```bash
pkill -f "python main.py"
sleep 2
python main.py &
```

---

## ✨ Bajarildi!

Bot hozir:
- ✅ Loveble bilan integratsiya qilgan
- ✅ Real-time sotuvlar qaydda olaydi
- ✅ Kunlik 23:00 da diagnostika yuboradi
- ✅ Haftalik va oylik hisobotlarni yaratadi
- ✅ Kam qoldig'i haqida ogohlantirma beradi
- ✅ SQLite bazada ma'lumotlarni saqlaydi
- ✅ Admin panelni Telegram orqali taqdim etadi

**Happy Selling! ☕**
