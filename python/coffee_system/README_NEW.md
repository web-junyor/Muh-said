# ☕ Coffee Shop Management Bot - Loveble Integration

Telegram bot **Loveble** POS sistemasi bilan integratsiya qilgan. Avtomatik sotuvlar qaydda olish, kunlik/haftalik/oylik diagnostika va inventar boshqaruvi.

## 📋 Xususiyatlari

### ✅ Avtomat Loveble Integratsiyasi
- **Webhook orqali sotuvlar qaydda olish** - Mahsulot sotilsa, bot avtomatik ma'lumot oladi
- **Real-time notifikatsiyasi** - Mahsulot nomi, miqdor va chekni Telegram orqali yuboradi
- **Inventar avtomatik yangilash** - Qoldig'ini davlat-da kamaytiradi

### 📊 Diagnostika va Hisobotlar
- **Kunlik Diagnostika (23:00)** - Bugungi sotuvlar, qoldig'i, daromad
- **Haftalik Hisobot (Juma 23:05)** - Haftaning jami sotuvlari, best/worst products
- **Oylik Hisobot (1-quni 23:10)** - Oyning jami statisti, growth rate, profitabilite

### ⚠️ Ogohlantirmalar
- **Kam Qoldig'i Alerts** - 3 dona yoki kamroq qolsa xabar beradi
- **Kritik Alerts** - 1 dona qolsa darhol ogohlantirma
- **Loveble Sync** - Loveble bilan inventar synchonizatsiyasi

### 💾 Database
- **SQLite** - Barcha ma'lumotlar lokal bazada saqlandi
- **Transaction Safe** - Sotuvlar va inventar tranzaksiya-xavfsiz
- **Historical Data** - Barcha sotuvlar tarixi saqlanadi

---

## 🚀 Setup va Installation

### 1️⃣ Requirements o'rnatish

```bash
# Python 3.9+ kerak
python --version

# Virtual environment yaratish
python -m venv venv

# Activation
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Packages o'rnatish
pip install -r requirements.txt
```

### 2️⃣ Configuration

**`config.py` faylida quyidagi parametrlarni o'zgartiring:**

```python
# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # BotFather dan oling
TELEGRAM_ADMIN_ID = 123456789  # Sizning Telegram ID

# Loveble API Credentials
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY"
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID"
LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET"
```

### 3️⃣ Database Initialization

```bash
# Database avtomatik yaratiladi, lekin manual check:
python -c "from backend.database import db; print('Database OK')"
```

---

## 📱 Botni Ishga Tushirish

### Development Mode

```bash
# Polling modida (test uchun)
python main.py
```

### Production Mode

```bash
# Gunicorn va webhook bilan
gunicorn --workers 4 --worker-class gevent --bind 0.0.0.0:8443 main:app
```

---

## 🔗 Loveble Webhook Integration

### Webhook URL Loveble Dashboard da sozlang:
```
https://yourdomain.com/webhook/loveble
```

### Webhook Events (avtomatik qayta ishlanadi):
- `order_paid` - To'langan buyurtma
- `order_completed` - Tugallangan buyurtma

### Webhook Format:
```json
{
  "event_type": "order_paid",
  "order_id": "order_123",
  "shop_id": "shop_456",
  "items": [
    {
      "product_id": "1",
      "product_name": "Espresso",
      "quantity": 2,
      "price": 5000,
      "total_price": 10000
    }
  ],
  "total_amount": 10000,
  "payment_method": "cash",
  "payment_status": "completed"
}
```

---

## 📡 API Endpoints

### Health Check
```bash
GET http://localhost:8443/health
```

### Statistics
```bash
GET http://localhost:8443/stats
```

### Loveble Webhook
```bash
POST http://localhost:8443/webhook/loveble
```

---

## 🤖 Telegram Bot Commands

### Admin uchun:
- `/start` - Botni start qilish, dashboard ko'rsatish
- **📊 Kunlik Hisobot** - Bugungi statistika
- **📈 Haftalik Hisobot** - Hafta davomida
- **📅 Oylik Hisobot** - Oy davomida
- **📦 Qoldig'i** - Inventar holati
- **⚠️ Kam Qoldig'i** - Low stock alerts
- **🆘 Yordamga** - Bot qo'llanmasi

---

## 📦 Mahsulotlar (Products)

8 ta koffee mahsuloti, har biri 12 dona dastlabki qoldig'i:

| # | Mahsulot | Narxi (som) | Initial Stock |
|---|----------|------------|---------------|
| 1 | Espresso | 5,000 | 12 |
| 2 | Cappuccino | 7,000 | 12 |
| 3 | Latte | 8,000 | 12 |
| 4 | Americano | 6,000 | 12 |
| 5 | Flat White | 8,500 | 12 |
| 6 | Macchiato | 7,500 | 12 |
| 7 | Mocha | 9,000 | 12 |
| 8 | Affogato | 8,500 | 12 |

---

## 🗂️ Folder Structure

```
coffee_system/
├── config.py                 # ⚙️ Sozlamalar
├── main.py                   # 🚀 Entry point
├── requirements.txt          # 📦 Dependencies
├── coffee.db                 # 💾 SQLite database
├── logs/
│   └── coffee_bot.log        # 📋 Logs
│
├── backend/                  # 🔧 Backend logic
│   ├── __init__.py
│   ├── models.py            # 📊 Data models
│   ├── database.py          # 💾 Database manager
│   ├── loveble_api.py       # 🔗 Loveble integration
│   └── scheduler.py         # ⏰ Diagnostika scheduler
│
└── bot/                      # 🤖 Telegram bot
    ├── __init__.py
    ├── bot.py               # Bot core
    └── handlers.py          # 📨 Message handlers
```

---

## 🛠️ Debugging

### Logs ko'rish
```bash
tail -f coffee_bot.log
```

### Database tekshirish
```bash
sqlite3 coffee.db
# Ichida:
sqlite> SELECT * FROM products;
sqlite> SELECT * FROM sales;
sqlite> SELECT * FROM daily_reports;
```

### Loveble webhook logs
```bash
sqlite3 coffee.db "SELECT * FROM loveble_webhooks ORDER BY processed_at DESC LIMIT 10;"
```

---

## 🔒 Security

- ✅ Webhook signaturani tekshirish
- ✅ Admin ID validation
- ✅ Database encryption qo'llanishini maslahat beriladi
- ✅ Loveble API key xavfsiz saqlang (.env faylida)

---

## 📝 Environment Variables (.env)

```bash
# .env fayli yaratish (production uchun)
TELEGRAM_BOT_TOKEN=your_token_here
LOVEBLE_API_KEY=your_key_here
DATABASE_PATH=/path/to/database
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_SECRET=your_secret_here
```

---

## 🚨 Troubleshooting

### Bot jawob bermayapti
- ✅ Token to'g'ri ekanini tekshiring
- ✅ Internet ulanishini tekshiring
- ✅ Admin ID to'g'ri ekanini tekshiring

### Loveble webhook qayta ishlalmayapti
- ✅ Secret key to'g'ri ekanini tekshiring
- ✅ Webhook URL loveble dashboardda to'g'ri ekanini tekshiring
- ✅ Server logglarni tekshiring (`coffee_bot.log`)

### Database xatolar
- ✅ Fayl huquqlari tekshiring
- ✅ Disk joyini tekshiring
- ✅ Database lock bo'lmaganini tekshiring

---

## 🤝 Support

Agar muammo bo'lsa:
1. Logglarni tekshiring: `coffee_bot.log`
2. Database logglarini tekshiring: `sqlite3 coffee.db`
3. Loveble webhook logglarini tekshiring

---

## 📄 License

Foydalanish uchun admin ruxsat kerak.

**Version:** 1.0.0
**Last Updated:** 2026-01-26
