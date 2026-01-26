# 🚀 Serverga Bot O'rnatish - To'liq Gid

## 📋 Talab

- **Server OS:** Linux (Ubuntu 20.04+)
- **SSH Access:** Root yoki sudo
- **Domain:** (opsional) HTTPS uchun

---

## 1️⃣ Serverga SSH Orqali Kirish

```bash
ssh root@YOUR_SERVER_IP
```

---

## 2️⃣ System Update

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git curl wget
```

---

## 3️⃣ Papka Yaratish va Code Yuklash

```bash
cd /home
mkdir -p coffee-bot
cd coffee-bot

# Yo'q bo'lsa, git bilan clone qiling
git clone <your-repo-url> .
# Yoki SCP bilan upload qiling
# scp -r /local/path/* root@SERVER_IP:/home/coffee-bot/
```

---

## 4️⃣ Python Virtual Environment

```bash
cd /home/coffee-bot/coffee_system

python3 -m venv venv
source venv/bin/activate

# Requirements o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5️⃣ Config Yangilash

```bash
nano config.py
```

**O'zgartirilishi kerak bo'lgan qismlar:**

```python
# Line 11-14:
LOVEBLE_API_KEY = "sk_live_..."  # Loveble dan olgan
LOVEBLE_WEBHOOK_SECRET = "whsec_live_..."  # Loveble dan olgan
LOVEBLE_SHOP_ID = "said_coffee_shop"  # Loveble dan olgan

# PRODUCTS seksiyasida - barcha loveble_id'larni yangilash
PRODUCTS = {
    "espresso": { "loveble_id": "ded1_gahvaxona" },
    "cappuccino": { "loveble_id": "prod_cappuccino" },
    # ... va hokazolar
}

# Webhook Port
WEBHOOK_PORT = 8443  # HTTPS uchun
WEBHOOK_HOST = "0.0.0.0"
```

---

## 6️⃣ SSL Sertifikat (HTTPS uchun)

### Option A: Let's Encrypt (Recommended)

```bash
apt install -y certbot

certbot certonly --standalone -d your-domain.com
```

Sertifikat joylashuvi:
- `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- `/etc/letsencrypt/live/your-domain.com/privkey.pem`

### Option B: Self-signed Sertifikat (Test)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

---

## 7️⃣ Systemd Service Yaratish

```bash
sudo nano /etc/systemd/system/coffee-bot.service
```

**Kodi:**

```ini
[Unit]
Description=Coffee Shop Bot with Loveble Integration
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/coffee-bot/coffee_system
ExecStart=/home/coffee-bot/coffee_system/venv/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/coffee-bot/coffee_bot.log
StandardError=append:/var/log/coffee-bot/coffee_bot.log

[Install]
WantedBy=multi-user.target
```

---

## 8️⃣ Logs Papkasini Yaratish

```bash
sudo mkdir -p /var/log/coffee-bot
sudo chmod 755 /var/log/coffee-bot
sudo chown root:root /var/log/coffee-bot
```

---

## 9️⃣ Service Ishga Tushirish

```bash
sudo systemctl daemon-reload
sudo systemctl enable coffee-bot
sudo systemctl start coffee-bot

# Status tekshirish
sudo systemctl status coffee-bot

# Logs ko'rish
sudo tail -f /var/log/coffee-bot/coffee_bot.log
```

---

## 🔟 Firewall Settings (UFW)

```bash
sudo ufw allow 8443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 1️⃣1️⃣ Webhook URL'ni Loveble'ga Qo'shish

Loveble Dashboard'da:

```
Webhook URL: https://YOUR_DOMAIN_OR_IP:8443/webhook/loveble
Events: order_paid, order_completed
Header: X-Loveble-Signature: <signature>
Secret: <LOVEBLE_WEBHOOK_SECRET>
```

---

## 1️⃣2️⃣ Test Qilish

### Terminal'da:

```bash
# Service ko'rish
sudo systemctl status coffee-bot

# Logs
sudo tail -100 /var/log/coffee-bot/coffee_bot.log

# Telegram bot @coffee_diagnostlar_bot ga /start yuboring
```

### Webhook Test:

```bash
curl -X POST https://YOUR_SERVER_IP:8443/webhook/loveble \
  -H "Content-Type: application/json" \
  -H "X-Loveble-Signature: test_signature" \
  -d '{
    "event_type": "order_paid",
    "order_id": "TEST-001",
    "shop_id": "said_coffee_shop",
    "items": [
      {
        "product_id": "prod_cappuccino",
        "product_name": "Cappuccino",
        "quantity": 1,
        "price": 7000,
        "total_price": 7000
      }
    ],
    "total_amount": 7000
  }'
```

---

## 🆘 Troubleshooting

### Bot ishlamayapti?

```bash
# Logs ko'rish
sudo journalctl -u coffee-bot -n 50

# Qo'l bilan ishga tushirish
source /home/coffee-bot/coffee_system/venv/bin/activate
python3 /home/coffee-bot/coffee_system/main.py
```

### Port ishlatilmoqda?

```bash
sudo lsof -i :8443
sudo kill -9 <PID>
```

### Database xatosi?

```bash
# Database qayta yaratish
rm /home/coffee-bot/coffee_system/coffee.db
python3 /home/coffee-bot/coffee_system/main.py
# CTRL+C bilan to'xtating
```

---

## ✅ Checklista - Serverga O'rnatish

- [ ] Server IP va SSH access tekshirildi
- [ ] Python 3 va pip o'rnatildi
- [ ] Code serverga yuklandi
- [ ] Virtual environment yaratildi
- [ ] requirements.txt o'rnatildi
- [ ] config.py bilan Loveble credentials qo'shildi
- [ ] SSL sertifikat o'rnatildi (HTTPS uchun)
- [ ] Systemd service yaratildi
- [ ] Service ishga tushdi (status OK)
- [ ] Logs ko'rildi (xatolar yo'q)
- [ ] Webhook URL Loveble'ga qo'shildi
- [ ] Test webhook yubordi
- [ ] Telegram bot javob beradi

---

## 📞 TEZDA QOLLAMALAR

**Service qayta ishga tushirish:**
```bash
sudo systemctl restart coffee-bot
```

**Logs follow qilish:**
```bash
sudo tail -f /var/log/coffee-bot/coffee_bot.log
```

**Service to'xtatish:**
```bash
sudo systemctl stop coffee-bot
```

---

**Tugallandi! 🎉 Bot serverda ishgan bo'lsa, siz tayyor!**
