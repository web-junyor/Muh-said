# Loveble AI ga Yuboriladigan Konfiguratsiya
# Loveble Integration Setup - O'zbek Tilida

---

## 📝 Loveble AI ga Quyidagi Ma'lumotni Yuboring

Salom! Biz Telegram bot yaratdik bu 8 ta mahsulot (kahva) bilan.

### ✅ Bot nima qiladi?

- **Sotuv xabari:** Har bir sotuv bo'lganda admin Telegramga xabar oladi (2 sekundda)
- **Qunlik hisobot:** Har kun soat 23:00 da kunlik satishlarni yuboradi
- **Haftalik hisobot:** Har juma soat 23:05 da haftalik satishlarni yuboradi
- **Oylik hisobot:** Har oy 1-kuni soat 23:10 da oylik satishlarni yuboradi
- **Qoldig'i:** Mahsulotlarning qoldig'ini kuzatib turadi

---

## 🔧 Loveble da O'rnatish Kerak

### 1. Webhook URL O'rnatish

**Webhook manzili:**
```
http://YOUR_SERVER_IP:8443/webhook/loveble
```

Misol (agar siz local'da test qilayotgan bo'lsangiz):
```
http://192.168.1.100:8443/webhook/loveble
```

Yoki agar server bo'lsa:
```
https://yourserver.com:8443/webhook/loveble
```

### 2. Webhook Secret O'rnatish

Webhook qabul qilish uchun **Secret key** kerak. Loveble tomonidan o'rnatilgan secret ni qabul qilish kerak.

**Ishlash:**
- Loveble webhooks settings da secret ko'rsatiladi
- Bot o'sha secret bilan signature tekshiradi
- Agar signature to'g'ri bo'lmasa, webhook qabul qilinmaydi (xavfsizlik)

### 3. Product ID Mapping

Loveble'da 8 ta mahsulot mavjud. Bot har bir mahsulotning **Product ID** sini bilishi kerak:

**Mahsulotlar ro'yxati:**
```
1. Espresso
2. Cappuccino
3. Latte
4. Americano
5. Flat White
6. Macchiato
7. Mocha
8. Affogato
```

Loveble'da har bir mahsulotning ID sini kopirang va biza yuboring.

### 4. Event Tiplarini O'rnatish

Loveble webhook settings'da quyidagi events aktiv bo'lishi kerak:

✅ **order_paid** - To'langan buyurtmalar (MUHIM!)
✅ **order_completed** - Bajarilgan buyurtmalar (MUHIM!)
❌ order_created - (ixtiyoriy, talab qilinmaydi)
❌ order_cancelled - (ixtiyoriy, talab qilinmaydi)

---

## 📤 Webhook Data Formati

Bot quyidagi formattada data qabul qiladi:

```json
{
  "event_type": "order_paid",
  "order_id": "ORD-20260127-001",
  "shop_id": "YOUR_SHOP_ID",
  "timestamp": "2026-01-27T14:30:45",

  "items": [
    {
      "product_id": "prod_cappuccino_abc123",
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
```

**Majburiy maydonlar:**
- `event_type`: "order_paid" yoki "order_completed"
- `order_id`: Chek/buyurtma ID
- `items`: Sotilgan mahsulotlar ro'yxati
- `total_amount`: Jami narx
- `timestamp`: Vaqt

---

## 🔐 Signature Verification

Bot webhook'ni **HMAC-SHA256** bilan tekshiradi.

**Ishlash:**
1. Loveble webhook secret ni beradigan header: `X-Loveble-Signature`
2. Bot payload bilan secret'ni HMAC-SHA256 qiladi
3. Signature'ni solishtiradi
4. Agar to'g'ri bo'lsa - qabul qiladi
5. Agar noto'g'ri bo'lsa - rad qiladi

**Header misoli:**
```
X-Loveble-Signature: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## 📋 Loveble Tekshirib O'tishi Kerak

Loveble AI dan quyidagilarni so'rang:

1. ✅ **Shop ID** nima? (Bot'ga kerak)
2. ✅ **API Key** sini copy qiling (Bot'ga kerak)
3. ✅ **8 ta mahsulot ID** sini copy qiling (Bot'ga kerak)
4. ✅ **Webhook secret** yaratib qildingmi? (Bot'ga kerak)
5. ✅ Webhook URL o'rnatib bo'ldingmi? (Bot saraladi)
6. ✅ order_paid va order_completed events aktiv ekanini tekshiring
7. ✅ Test webhook yuborishingiz mumkinmi?

---

## 🔄 Bot Setup Qilish

Bot uchun quyidagi ma'lumot kerak:

```
LOVEBLE_API_KEY = "sk_live_..."
LOVEBLE_WEBHOOK_SECRET = "whsec_live_..."
LOVEBLE_SHOP_ID = "shop_..."

PRODUCTS = {
    "cappuccino": { "loveble_id": "prod_cappuccino_..." },
    "espresso": { "loveble_id": "prod_espresso_..." },
    # va boshqa 6 ta mahsulot
}
```

---

## 🧪 Test Qilish

Loveble'da test mode'da webhook yuborish mumkinmi?

Bot'ga test webhook yuborishda:
1. order_id ni yozing (misol: "TEST-001")
2. Har bir item uchun product_id, name, quantity, price yozing
3. Webhook URL ga POST qiling
4. Bot database'ga saqlab qoladi
5. Admin Telegramga xabar oladi

---

## ❓ Savollar

**Savollar Loveble'ga:**

1. **Webhook URL:** Biz qanday port ishlatishimiz kerak? (9443, 8000, boshqa?)
   - Javob: **8443** (standart)

2. **Event types:** Qaysilerini yuborsak bo'ladi?
   - Javob: Minimal **order_paid** va **order_completed**

3. **Signature:** Header'da X-Loveble-Signature bo'ladi?
   - Javob: Ha, HMAC-SHA256 bilan

4. **Retry:** Agar bot javob bermasa, qayta yuborasizmi?
   - Javob: Ha, bot har doim 200 OK qaytaradi

5. **Test mode:** Test webhook yuborish mumkinmi?
   - Javob: Ha, bizga kerak test'ni qabul qilish uchun

---

## 📞 Bot Haqida Qisqacha

**Bot:** Telegram bot + Flask server
**Port:** 8443
**Database:** SQLite (coffee.db)
**Mahsulotlar:** 8 ta (espresso, cappuccino, latte, americano, flat white, macchiato, mocha, affogato)
**Funktsiyalar:** Real-time notifications, daily/weekly/monthly reports, stock tracking

---

## ✅ Loveble Checklist

Loveble AI ga quyidagi checklist'ni yuboring:

- [ ] Webhook URL o'rnatildi: `http://YOUR_IP:8443/webhook/loveble`
- [ ] Webhook secret yaratildi
- [ ] X-Loveble-Signature header yuboriladi
- [ ] order_paid event aktiv
- [ ] order_completed event aktiv
- [ ] 8 ta product ID nomi
- [ ] API key yaratildi
- [ ] Shop ID nomi
- [ ] Test webhook yuborish imkoniyati
- [ ] Retry logic o'rnatildi

---

## 💬 Loveble AI ga Yuboriladigan Xabar

```
Assalomu alaikum!

Biz Telegram bot qilyaptibiz 8 ta mahsulot (kahva) sotuvini kuzatish uchun.

Bot quyidagilar kerak:

1. Webhook manzili: http://YOUR_IP:8443/webhook/loveble
2. Events: order_paid, order_completed
3. Signature header: X-Loveble-Signature (HMAC-SHA256)
4. Payload format: JSON (items array bilan)

Bizga kerak:
- Shop ID
- API Key
- Webhook Secret
- 8 ta Product ID

Quyida webhook format:
{
  "event_type": "order_paid",
  "order_id": "ORD-001",
  "shop_id": "shop_xyz",
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
  "timestamp": "2026-01-27T14:30:45"
}

Header:
X-Loveble-Signature: HMAC-SHA256(payload, secret)

Shunday qilsangiz, bot ishladi!
```

---

## 🎯 Oxirgi Qadam

Loveble AI dan javob keltirgach:

1. **Shop ID** → config.py ga yozing (LOVEBLE_SHOP_ID)
2. **API Key** → config.py ga yozing (LOVEBLE_API_KEY)
3. **Webhook Secret** → config.py ga yozing (LOVEBLE_WEBHOOK_SECRET)
4. **8 Product ID** → config.py PRODUCTS seksiyasiga yozing

Keyin:
```bash
python main.py
```

Tugadi! Bot ishladi! ✅

---

## 📧 Loveble AI Kontakti

Agar Loveble AI'da ko'rsatilsa, ularga bu fayl yuboring.

Ular quyidagilarni qilishlari kerak:
1. Webhook endpoint o'rnatish
2. Secret key berish
3. API key berish
4. Product ID'larini ko'rsatish
5. Test qilish

---

## ✨ Oxirgi Ma'lumot

**Telegram Bot Token:** Allaqachon o'rnatilgan
**Admin ID:** Allaqachon o'rnatilgan
**Mahsulotlar:** 8 ta (8 dona initial stock)
**Database:** SQLite (avtomatik yaratiladi)
**Scheduler:** Daily/weekly/monthly (avtomatik ishlaydi)

**Barcha tayyor! Faqat Loveble konfiguratsiyasi kerak!**

---

**Tayyyorliq sana:** 27-Yanvar 2026
**Status:** ✅ Loveble integrationga tayyor
**Versiya:** 1.0.0
