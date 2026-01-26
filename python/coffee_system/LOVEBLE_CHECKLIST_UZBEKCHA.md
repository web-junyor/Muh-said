# ✅ LOVEBLE AI GA YUBORILADIGAN CHECKLIST
# Loveble Integration Checklist - Uzbek Version

---

## 📋 Loveble AI Dan Quyidagilarni So'rang va Oling

### 1️⃣ SHOP ID
**Nima?** Loveble'dagi do'kon ID'si
**Qayerdan?** Settings → Shop Information
**Format:** `shop_1234567890` yoki `shop_abc123def456`
**Ko'rinish:** Text string
**Misol:** `shop_cafe_downtown`

**Berildi?** ☐
**Olingan qiymat:** `________________`

---

### 2️⃣ API KEY
**Nima?** Bot Loveble API'ni chaqirish uchun key
**Qayerdan?** Settings → API Keys → Create New
**Format:** `sk_live_abcdef123...`  yoki `pk_live_xyz789...`
**Ko'rinish:** Long text string (60+ characters)
**Eslatma:** XAVFLI! Boshqalardan xidni qilib qo'ymang!

**Berildi?** ☐
**Olingan qiymat:** `________________________________`

---

### 3️⃣ WEBHOOK SECRET
**Nima?** Webhook signature'ni tekshirish uchun secret
**Qayerdan?** Settings → Webhooks → Create/View Secret
**Format:** `whsec_live_abcdef123...`
**Ko'rinish:** Long text string (40+ characters)
**Eslatma:** XAVFLI! Boshqalardan xidni qilib qo'ymang!

**Berildi?** ☐
**Olingan qiymat:** `________________________________`

---

### 4️⃣ MAHSULOT ID'LAR (8 ta)
**Nima?** Har bir mahsulotning noyob ID'si
**Qayerdan?** Products → Har bir product'ga click → Product ID ko'ring
**Format:** `prod_cappuccino_abc123` yoki UUID ko'rinishida
**Ko'rinish:** Text string

#### Espresso
**Bot ID:** 1
**Narxi:** 5,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Cappuccino
**Bot ID:** 2
**Narxi:** 7,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Latte
**Bot ID:** 3
**Narxi:** 8,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Americano
**Bot ID:** 4
**Narxi:** 6,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Flat White
**Bot ID:** 5
**Narxi:** 8,500 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Macchiato
**Bot ID:** 6
**Narxi:** 7,500 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Mocha
**Bot ID:** 7
**Narxi:** 9,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

#### Affogato
**Bot ID:** 8
**Narxi:** 9,000 som
**Loveble ID:** `________________`
**Berildi?** ☐

---

## 🔧 Loveble'da O'rnatish Kerak

### ✅ WEBHOOK O'RNATISH

**Qayerda?** Settings → Webhooks → Add New Webhook

**O'rnatadigan qiymatlar:**

| Maydon | Qiymat |
|-------|--------|
| **Webhook URL** | `http://YOUR_SERVER_IP:8443/webhook/loveble` |
| **Webhook Secret** | (o'zingiz yaratilgan secret) |
| **Request Method** | POST |
| **Content Type** | application/json |

**O'rnatildi?** ☐

---

### ✅ EVENTS AKTIVATSIYA QILISH

**Qayerda?** Webhooks → Events Selection

**Aktiv qilish kerak:**
- ✅ `order_paid` - To'langan buyurtmalar (MUHIM!)
- ✅ `order_completed` - Bajarilgan buyurtmalar (MUHIM!)
- ❌ `order_created` - Yaratilgan (ixtiyoriy)
- ❌ `order_cancelled` - Bekor qilingan (ixtiyoriy)
- ❌ `order_refunded` - Pul qaytarish (ixtiyoriy)

**Aktivatsiya qilindi?** ☐

---

### ✅ TEST WEBHOOK YUBORISH

**Qayerda?** Webhooks → Test Webhook

**Test ma'lumotlar:**
```json
{
  "event_type": "order_paid",
  "order_id": "TEST-001",
  "shop_id": "shop_id",
  "timestamp": "2026-01-27T14:30:45",
  "items": [
    {
      "product_id": "prod_cappuccino",
      "product_name": "Cappuccino",
      "quantity": 1,
      "price": 7000,
      "total_price": 7000
    }
  ],
  "total_amount": 7000,
  "payment_status": "paid",
  "payment_method": "card"
}
```

**Test yuborildi?** ☐
**Javob:** HTTP 200 OK?  ☐

---

## 🔐 SIGNATURE VERIFICATION

**Nima?** Bot webhook'ni tekshirish uchun signature ishlatadi

**Ishlash:**
1. Loveble webhook body + secret bilan HMAC-SHA256 qiladi
2. Header'da `X-Loveble-Signature` orqali yuboradi
3. Bot o'sha signature'ni tekshiradi
4. Agar to'g'ri bo'lsa - qabul qiladi ✅
5. Agar noto'g'ri bo'lsa - rad qiladi ❌

**Signature header misoli:**
```
X-Loveble-Signature: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

**Signature tekshiriladi?** ☐

---

## 📊 PAYLOAD FORMAT TEKSHIRUVI

**Bot quyidagi formatni qabul qiladi:**

```json
{
  "event_type": "order_paid|order_completed",
  "order_id": "string",
  "shop_id": "string",
  "timestamp": "ISO-8601",
  "items": [
    {
      "product_id": "string",
      "product_name": "string",
      "quantity": "number",
      "price": "number",
      "total_price": "number"
    }
  ],
  "total_amount": "number",
  "payment_status": "string",
  "payment_method": "string"
}
```

**Barcha maydonlar?** ☐
**items array?** ☐
**product_id correct?** ☐

---

## 📝 LOVEBLE CHECKLIST

- [ ] Webhook URL o'rnatildi: `http://YOUR_IP:8443/webhook/loveble`
- [ ] Webhook secret yaratildi
- [ ] order_paid event aktiv
- [ ] order_completed event aktiv
- [ ] X-Loveble-Signature header yuboriladi
- [ ] Payload JSON format'da
- [ ] items array mavjud
- [ ] product_id correct
- [ ] total_amount correct
- [ ] timestamp ISO-8601 formatda
- [ ] Test webhook 200 OK qaytaradi
- [ ] Retry logic o'rnatildi
- [ ] Webhook logs ko'rish imkoniyati
- [ ] API key active
- [ ] Shop ID correct
- [ ] All 8 products mapped

---

## 💬 LOVEBLE AI'GA YUBORILADIGAN XABAR

```
Assalomu alaikum!

Men Telegram bot qilyaptibim kahva do'konimiz uchun.
Bot quyidagilar qiladi:
- Real-time sotuv xabari (Telegram)
- Kunlik/haftalik/oylik hisobotlar
- Qoldig'i kuzatish

Sizdan kerak:
1. Shop ID
2. API Key
3. Webhook Secret
4. 8 ta Product ID
5. Webhook o'rnatish: http://MY_IP:8443/webhook/loveble
6. Events: order_paid, order_completed
7. Signature header: X-Loveble-Signature (HMAC-SHA256)

Payload format:
{
  "event_type": "order_paid",
  "order_id": "...",
  "items": [
    {
      "product_id": "...",
      "product_name": "...",
      "quantity": N,
      "price": N,
      "total_price": N
    }
  ],
  "total_amount": N,
  "timestamp": "..."
}

Test webhook imkoniyati bo'lsa, juda zo'r!

Raxmat!
```

---

## ✅ FINAL CHECKLIST

### Loveble'dan Olingan:
- [ ] Shop ID
- [ ] API Key
- [ ] Webhook Secret
- [ ] All 8 Product IDs
- [ ] Webhook working (200 OK response)
- [ ] Events configured (order_paid, order_completed)
- [ ] Test webhook capability

### Bot'dan Kerakli:
- [ ] Flask server (port 8443)
- [ ] Telegram bot token
- [ ] Telegram admin ID
- [ ] Database (SQLite)
- [ ] APScheduler (daily/weekly/monthly)
- [ ] All 8 products configured

### O'rnatadigan Joylar:
- [ ] config.py - Loveble credentials
- [ ] config.py - Product IDs
- [ ] Loveble Settings - Webhook URL
- [ ] Loveble Settings - Events
- [ ] Loveble Settings - Webhook Secret

---

## 🚀 KEYINGI QADAM

**Loveble'dan javob kelib bo'lganda:**

1. **config.py ni o'zgarish:**
   ```python
   LOVEBLE_API_KEY = "olingan api key"
   LOVEBLE_WEBHOOK_SECRET = "olingan secret"
   LOVEBLE_SHOP_ID = "olingan shop id"

   PRODUCTS = {
       "cappuccino": { "loveble_id": "cappuccino product id" },
       # va boshqa 7 ta
   }
   ```

2. **Botni ishga tushirish:**
   ```bash
   cd coffee_system
   python main.py
   ```

3. **Test qilish:**
   - Loveble POS'da sotuv qiling
   - Telegram'da xabar olmaydingiz ekan
   - Logs tekshiring

---

## 📞 QANDAY YUBORISH?

### Loveble AI'ga:

1. **Bu fayl:** `LOVEBLE_UZBEKCHA.md`
2. **JSON fayl:** `loveble_integration_request.json`
3. **Xabar:** Yuqoridagi xaberni copy qilib yuboring

### Javobida:
- Shop ID
- API Key
- Webhook Secret
- 8 Product ID
- Confirmation: Webhook ready ✅

---

## ⏱️ VAQT

- Loveble'dan so'rash: 5 minutes
- Javob kutish: 1-24 soat
- Bot'da o'rnatish: 2 minutes
- Test qilish: 5 minutes

**Jami:** 1-24 soat ⏱️

---

**Tayyyorliq sana:** 27-Yanvar 2026
**Status:** ✅ Tayyor Loveble integrationiga
**Versiya:** 1.0.0

---

**Loveble AI'ga bo'lgan so'rovni Uzbek tilida yuboring!**
