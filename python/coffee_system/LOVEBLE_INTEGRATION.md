# Loveble Integration Guide
# Loveble Integratsiyasining Tafsiloti

## 1. Loveble dan Bot ga Keladigan Webhooks

### Webhook POST Request Format
Loveble sizning Flask serveringizga quyidagi formatta POST request yuboradi:

**URL:** `http://YOUR_SERVER:8443/webhook/loveble`

**Headers (Loveble tomonidan yuboriladi):**
```
Content-Type: application/json
X-Loveble-Signature: HMAC-SHA256 signature
```

### Webhook Payload (JSON Body)
```json
{
  "event_type": "order_paid",
  "order_id": "ORD-20260127-00123",
  "shop_id": "YOUR_SHOP_ID",
  "timestamp": "2026-01-27T12:30:45",
  "items": [
    {
      "product_id": "cappuccino_loveble_id",
      "product_name": "Cappuccino",
      "quantity": 2,
      "price": 7000,
      "total_price": 14000
    },
    {
      "product_id": "espresso_loveble_id",
      "product_name": "Espresso",
      "quantity": 1,
      "price": 5000,
      "total_price": 5000
    }
  ],
  "total_amount": 19000,
  "payment_status": "paid",
  "payment_method": "card",
  "customer_phone": "+998901234567"
}
```

### Webhook Event Types (Qabul qiladigan event tiplari)
Bot bu event tiplarini qabul qiladi:
- `order_created` - Buyurtma yaratildi (xisobga olinmaydi)
- `order_paid` - **Buyurtma to'landi (xisobga olinadi)**
- `order_completed` - **Buyurtma bajarildi (xisobga olinadi)**
- `order_cancelled` - Buyurtma bekor qilindi (xisobga olinmaydi)
- `order_refunded` - Pul qaytarilildi (xisobga olinmaydi)

**⚠️ MUHIM:** Faqat `order_paid` va `order_completed` events xisobga olinadi!

---

## 2. Loveble da Webhook ni O'rnatish

### Step 1: Loveble Settings ga kiring
1. Loveble dashboard ga kiring
2. **Settings** → **Webhooks** bo'limiga o'ting
3. **Add Webhook** tugmasini bosing

### Step 2: Webhook URL o'rnatish
```
Webhook URL: http://YOUR_DOMAIN:8443/webhook/loveble
```

**Qo'shimcha ma'lumot:**
- `YOUR_DOMAIN` = Sizning server IP addressi yoki domain nomi
  - Local: `http://localhost:8443` yoki `http://127.0.0.1:8443`
  - Production: `http://your-server-domain.com:8443`
- Port: **8443** (config.py da belgilangan)
- Path: `/webhook/loveble` (Flask route)

### Step 3: Webhook Secret o'rnatish
1. Loveble webhooks settings da **Secret** qismini toping
2. Qandaydir `secret_key` ni copy qiling
3. Bizning **config.py** da o'rnatish:

```python
LOVEBLE_WEBHOOK_SECRET = "YOUR_SECRET_KEY_FROM_LOVEBLE"
```

### Step 4: Event tiplarini tanlash
O'rnatish vaqtida quyidagi event tiplarini **aktiv** qiling:
- ✅ **order_paid** - To'langan buyurtmalar
- ✅ **order_completed** - Bajarilgan buyurtmalar
- ❌ order_created (ixtiyoriy)
- ❌ order_cancelled (ixtiyoriy)

---

## 3. Config.py ga Loveble Credentials o'rnatish

Quyidagi maydonlarni **mutlaqo** to'ldirish kerak:

```python
# ==================== Loveble API Settings ====================
LOVEBLE_API_KEY = "pk_live_abcdef123456789"  # Loveble dan olingan API key
LOVEBLE_API_URL = "https://api.loveble.com"   # Loveble API URL (o'zgartirmang)
LOVEBLE_WEBHOOK_SECRET = "whsec_abcdef123"    # Webhook signature uchun secret
LOVEBLE_SHOP_ID = "your-shop-id-123"          # Loveble shop ID
```

### Qayerdan olinadi?
1. **LOVEBLE_API_KEY**: Loveble Settings → API Keys
2. **LOVEBLE_WEBHOOK_SECRET**: Loveble Settings → Webhooks → Secret
3. **LOVEBLE_SHOP_ID**: Loveble Settings → Shop ID yoki Dashboard

---

## 4. Mahsulotlarni Loveble bilan sinxronizatsiya qilish

### Config.py da mahsulotlarni to'g'rilash

Har bir mahsulot uchun **Loveble ID** ni to'g'ri o'rnatish juda **muhim**!

```python
PRODUCTS = {
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,  # som
        "loveble_id": "cappuccino_loveble_id"  # ⚠️ Bu Loveble da to'g'ri bo'lishi kerak!
    },
    # ... boshqa mahsulotlar
}
```

**Loveble_id ni qayerdan olish?**
1. Loveble dashboard ga kiring
2. **Products** bo'limiga o'ting
3. Har bir mahsulotning ID sini copy qiling
4. Config.py da `loveble_id` ga paste qiling

**Misol Loveble dan:**
```
- Cappuccino: ID = "prod_cappuccino_uuid"
- Espresso: ID = "prod_espresso_uuid"
- Latte: ID = "prod_latte_uuid"
```

---

## 5. Test qilish - Webhook Test Request

### Method 1: Using curl (Buyurtma simulyatsiya qilish)

```bash
# HMAC signature yaratish
SECRET="YOUR_WEBHOOK_SECRET"
PAYLOAD='{"event_type":"order_paid","order_id":"TEST-001","shop_id":"shop123","timestamp":"2026-01-27T12:00:00","items":[{"product_id":"2","product_name":"Cappuccino","quantity":1,"price":7000,"total_price":7000}],"total_amount":7000,"payment_status":"paid","payment_method":"card"}'

# Signature hisoblash (openssl bilan)
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" -r | awk '{print $1}')

# Test request yuborish
curl -X POST http://localhost:8443/webhook/loveble \
  -H "Content-Type: application/json" \
  -H "X-Loveble-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

### Method 2: Using Python script

Fayl yarating: `test_webhook.py`

```python
#!/usr/bin/env python3
import requests
import json
import hmac
import hashlib

# Konfiguratsiya
WEBHOOK_URL = "http://localhost:8443/webhook/loveble"
WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET"

# Test payload
payload = {
    "event_type": "order_paid",
    "order_id": "TEST-20260127-001",
    "shop_id": "shop123",
    "timestamp": "2026-01-27T12:00:00",
    "items": [
        {
            "product_id": "2",
            "product_name": "Cappuccino",
            "quantity": 2,
            "price": 7000,
            "total_price": 14000
        }
    ],
    "total_amount": 14000,
    "payment_status": "paid",
    "payment_method": "card",
    "customer_phone": "+998901234567"
}

# JSON stringga aylantirish
payload_str = json.dumps(payload)

# HMAC signature yaratish
signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    payload_str.encode(),
    hashlib.sha256
).hexdigest()

# Headers
headers = {
    "Content-Type": "application/json",
    "X-Loveble-Signature": signature
}

# Request yuborish
response = requests.post(WEBHOOK_URL, data=payload_str, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
```

Ishga tushirish:
```bash
cd coffee_system
python test_webhook.py
```

**Kutilgan javob:**
```json
{
  "status": "ok",
  "message": "Webhook processed"
}
```

---

## 6. Xatosiz Ishlash Uchun Tekshirish Ro'yxati

### ✅ Before Running Bot

1. **Config.py tekshiring:**
   - [ ] `LOVEBLE_API_KEY` to'ldirilgan
   - [ ] `LOVEBLE_WEBHOOK_SECRET` to'ldirilgan
   - [ ] `LOVEBLE_SHOP_ID` to'ldirilgan
   - [ ] Barcha `loveble_id` lar to'g'ri belgilangan

2. **Loveble Settings tekshiring:**
   - [ ] Webhook URL o'rnatilgan: `http://YOUR_IP:8443/webhook/loveble`
   - [ ] Webhook Secret o'rnatilgan
   - [ ] `order_paid` va `order_completed` events aktiv
   - [ ] API Key yaratilgan va active

3. **Network tekshiring:**
   - [ ] Firewall 8443 portini blok qilmaydi
   - [ ] Server port 8443 da listening holatida
   - [ ] Loveble serveridan sizning serverga kirish mumkin

### ✅ Running Bot

```bash
cd coffee_system
python main.py
```

Kutilgan log lines:
```
Database initialized successfully
Coffee Shop Bot Starting
Database loaded with 8 products
Setting up diagnostics scheduler...
Diagnostics scheduler started successfully
Starting Flask server on 0.0.0.0:8443
Starting Telegram bot...
Running on http://0.0.0.0:8443
```

### ✅ Webhook Test

1. **Loveble da test buyurtma qiling** yoki test webhook yu borish
2. **Logs tekshiring:**
   ```bash
   tail -f coffee_bot.log
   ```

3. **Kutilgan logs:**
   ```
   Received Loveble webhook: order_paid
   Processing sale...
   Order processed successfully
   ```

---

## 7. Common Errors va Yechimlar

### Error: "Invalid Loveble webhook signature"
**Sabab:** HMAC signature noto'g'ri
**Yechim:**
- `LOVEBLE_WEBHOOK_SECRET` to'g'ri ekani tekshiring
- Loveble settings da secret o'zgarmaganini tekshiring

### Error: "404 Not Found" on webhook
**Sabab:** Webhook URL noto'g'ri
**Yechim:**
- URL: `http://YOUR_IP:8443/webhook/loveble` bo'lishi kerak
- Port 8443 da listening ekani tekshiring

### Error: "Connection refused"
**Sabab:** Flask server ishlamayapti
**Yechim:**
- Bot is running: `python main.py` ishga tushiring
- Port: 8443 o'zga server tomonidan band emasligini tekshiring

### Error: "No item with that key" (Database)
**Sabab:** Database schema muammo
**Yechim:**
```bash
# Old database ni o'chirish
rm coffee.db
# Yangi database yaratish uchun botni restart qilish
python main.py
```

### Error: "product_id not found in products"
**Sabab:** Config.py da mahsulot ID tug'ri emasligini
**Yechim:**
- Loveble da mahsulot ID ni tekshiring
- Config.py da to'g'ri `loveble_id` qo'ying

---

## 8. Production Deployment

### Nginx Reverse Proxy (sertifikat bilan)

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

Fayl: `/etc/systemd/system/coffee-bot.service`

```ini
[Unit]
Description=Coffee Shop Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/coffee_system
ExecStart=/home/user/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable coffee-bot
sudo systemctl start coffee-bot
```

---

## 9. Monitoring va Debugging

### Logs tekshirish
```bash
# Real-time logs
tail -f coffee_bot.log

# Xatolar
grep ERROR coffee_bot.log

# Webhooks haqida
grep "webhook" coffee_bot.log
```

### Health Check
```bash
curl http://localhost:8443/health
# Javob: {"status":"ok","bot":"running"}
```

### Statistics
```bash
curl http://localhost:8443/stats
# Javob: {"today_sales":5,"today_revenue":35000,"stock":{...}}
```

---

## 10. Summary Checklist

- [ ] Loveble API Key olingan va config.py ga qo'yilgan
- [ ] Webhook Secret olingan va config.py ga qo'yilgan
- [ ] Shop ID olingan va config.py ga qo'yilgan
- [ ] Barcha mahsulotlarning loveble_id tug'ri belgilangan
- [ ] Webhook URL Loveble settings da o'rnatilgan
- [ ] Webhook secret Loveble settings da o'rnatilgan
- [ ] order_paid va order_completed events aktiv
- [ ] Firewall 8443 portini ruxsat beradi
- [ ] Flask server ishga tushadi va 8443 portda listening
- [ ] Test webhook yuborildi va 200 OK javob olindi
- [ ] Database 8 mahsulot bilan yaratildi
- [ ] Telegram admin ID to'g'ri belgilangan
- [ ] Bot /start komandasiga javob beradi

**Barcha tekshiruvlar** ✅ bo'lsa - **XATOSIZ ISHLAYDI!**
