# ☕ Coffee Shop Management Bot with Loveble Integration

**Production-ready Telegram bot** kahva do'konida Loveble POS tizimi bilan integratsiya uchun.

---

## 🎯 Xususiyatlar

✅ **Real-time Sales Notifications** - Har bir sotuv bo'lganda Telegram'ga xabar (2 sekundda)
✅ **Daily Diagnostics** - Har kuni soat 23:00 da tafsildli hisobot
✅ **Weekly Reports** - Har juma soat 23:05 da haftalik tahlil
✅ **Monthly Analytics** - Oy boshi soat 23:10 da oylik mo'ljallari
✅ **Stock Tracking** - Mahsulotlarning qoldig'i avtomatik yangilanadi
✅ **Loveble POS Integration** - HMAC-SHA256 signature verification bilan webhook
✅ **Secure** - JWT tokens, signature verification, transaction safety

---

## 🚀 Tezda Boshlash

### Lokal Mashinada (Test)

```bash
# 1. Virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Config'ni yangilash
nano config.py
# -> Loveble credentials qo'shish

# 4. Bot ishga tushirish
python3 main.py
```

### Serverga O'rnatish (Production)

```bash
# Qisqa gid uchun
cat QUICK_DEPLOY.md

# Yoki to'liq gid uchun
cat SETUP_SERVER.md

# Deploy skripti bilan (avtomatik)
sudo bash deploy.sh
```

---

## 📋 Konfiguratsiya

`config.py` ni o'zingizga moslashtiring:

```python
# Telegram Bot
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_ADMIN_ID = 5995404792

# Loveble API
LOVEBLE_API_KEY = "sk_live_..."
LOVEBLE_WEBHOOK_SECRET = "whsec_live_..."
LOVEBLE_SHOP_ID = "said_coffee_shop"

# Products
PRODUCTS = {
    "espresso": { "loveble_id": "ded1_gahvaxona" },
    "cappuccino": { "loveble_id": "prod_cappuccino" },
    # ... va hokazolar
}
```

---

## 🧪 Webhook Testing

```bash
# Test skript ishga tushirish
python3 test_webhook.py

# Yoki manual CURL:
curl -X POST http://localhost:8443/webhook/loveble \
  -H "Content-Type: application/json" \
  -H "X-Loveble-Signature: <signature>" \
  -d '{"event_type":"order_paid",...}'
```

---

## 📂 Papka Tuzulishi

```
coffee_system/
├── main.py                          # Entry point
├── config.py                        # Konfiguratsiya
├── requirements.txt                 # Dependencies
├── README.md                        # Bu fayl
├── QUICK_DEPLOY.md                 # Qisqa deploy gid
├── SETUP_SERVER.md                 # To'liq server setup
├── test_webhook.py                 # Webhook test skripti
├── deploy.sh                        # Deploy avtomation
│
├── bot/
│   ├── __init__.py
│   ├── bot.py                      # Telegram bot initialization
│   ├── handlers.py                 # Commands (/start, /daily, /weekly, /monthly)
│   ├── commands.py                 # Additional commands
│   └── notifier.py                 # Notification system
│
├── backend/
│   ├── __init__.py
│   ├── loveble_api.py             # Loveble webhook handling
│   ├── database.py                # SQLite operations
│   ├── models.py                  # Pydantic models
│   ├── scheduler.py               # APScheduler jobs
│   └── reports.py                 # Report generation
│
└── docs/
    ├── LOVEBLE_UZBEKCHA.md        # Uzbek Loveble guide
    ├── LOVEBLE_SETUP.md           # English setup
    ├── LOVEBLE_INTEGRATION.md     # Integration details
    └── LOVEBLE_CHECKLIST_*.md     # Checklists
```

---

## 🔧 Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Runtime |
| **aiogram** | 3.4.1 | Telegram bot framework |
| **Flask** | 2.x | Webhook server |
| **APScheduler** | 3.x | Task scheduling |
| **SQLite3** | 3.x | Database |
| **Pydantic** | 2.x | Data validation |

---

## 📊 Database Schema

**6 ta table:**

1. **products** - Mahsulotlar (espresso, cappuccino, va boshqalar)
2. **sales** - Sotuvlar qaydlari
3. **daily_reports** - Kunlik hisobot (23:00)
4. **weekly_reports** - Haftalik hisobot (juma 23:05)
5. **monthly_reports** - Oylik hisobot (1-kun 23:10)
6. **loveble_webhooks** - Webhook loglar

---

## 🔐 Security

✅ **HMAC-SHA256** - Webhook signature verification
✅ **Admin Authentication** - Telegram ID tekshirish
✅ **Database Transactions** - ACID garantiyalari
✅ **Error Logging** - Barcha xatolar qaydda olinadi
✅ **Rate Limiting** - Webhook queue handling

---

## 📱 Telegram Commands

Bot @coffee_diagnostlar_bot'da:

| Command | Description |
|---------|-------------|
| `/start` | Bot haqida ma'lumot |
| `/daily` | Bugun'ning hisobot |
| `/weekly` | Shu hafta'ning hisobot |
| `/monthly` | Shu oy'ning hisobot |
| `/stock` | Mahsulotlarning qoldig'i |
| `/help` | Yordam |

---

## 📈 Hisobotlar

### Kunlik (23:00)
```
Joni 27, 2026
━━━━━━━━━━━━━━━━━━━━━
📊 Sotuvlar: 12 ta
💰 Jami: 89,500 so'm
📌 Top: Cappuccino (5 ta)
⏱️ Vaqti: 14:30 - 23:00
```

### Haftalik (Juma 23:05)
- Har kun'ning statistikasi
- O'rtacha sotuv miqdori
- Eng ko'p sotilgan mahsulot
- Haftaning jami foyda

### Oylik (1-kun 23:10)
- Haftaning statistikasi
- Oyning trend'i
- Mahsulot kategoriyasi bo'yicha tahlil
- Oyning eng yaxshi kun'i

---

## 🚨 Troubleshooting

### Bot ishlamayapti?

```bash
# Logs ko'rish
tail -f coffee_bot.log

# Virtual environment ishlamoqda?
source venv/bin/activate
python3 main.py  # Manual start
```

### Webhook xatosi?

```bash
# LOVEBLE_WEBHOOK_SECRET'ni tekshiring
cat config.py | grep WEBHOOK_SECRET

# Signature verification
python3 test_webhook.py
```

### Database xatosi?

```bash
# Database qayta yaratish
rm coffee.db
python3 main.py
# CTRL+C bilan to'xtang, qayta ishga tushirish uchun yo'q kerak
```

---

## 📞 Loveble Integration Checklist

- [ ] Loveble API Key olingan
- [ ] Webhook Secret olingan
- [ ] Shop ID olingan
- [ ] 8 ta Product ID'lar olingan
- [ ] config.py yangilandi
- [ ] Webhook URL Loveble'da qo'shildi
- [ ] Events (order_paid, order_completed) aktivlashtirildi
- [ ] Test webhook yuborildi
- [ ] Telegram notification qabul qilindi
- [ ] Logs'da xatolar yo'q

---

## 📝 Files Reference

| File | Purpose |
|------|---------|
| `QUICK_DEPLOY.md` | 3-qadamli tezda deploy |
| `SETUP_SERVER.md` | To'liq server setup qo'llanmasi |
| `test_webhook.py` | Webhook test skripti |
| `deploy.sh` | Avtomatik deploy (Linux) |
| `LOVEBLE_UZBEKCHA.md` | Loveble integratsiya (Uzbek) |
| `LOVEBLE_*.md` | Qo'shimcha gidlar |

---

## 🎉 Tayyor?

1. **Lokal test:** `python3 main.py`
2. **Server'ga deploy:** `sudo bash deploy.sh`
3. **Loveble'ga connect:** Webhook URL'ni qo'shish
4. **Test:** `python3 test_webhook.py`

---

## 📞 Support

Muammolar uchun logs ko'ring:
```bash
tail -100 coffee_bot.log
```

---

**Version:** 1.0.0
**Last Updated:** January 27, 2026
**Status:** ✅ Production Ready
