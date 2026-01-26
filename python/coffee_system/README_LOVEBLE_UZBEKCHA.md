# 🎉 LOVEBLE INTEGRATION - O'ZBEK TILIDA TAYYOR!
# Bot Loveble AI ga Yuboriladigan Barcha Ma'lumot

---

## ✅ TAYYYORLANGAN FAYLLAR

Bot Loveble AI'ga yuboriladigan **12 ta fayl** tayyor!

### 📁 Loveble uchun Uzbek Tilida Fayllar:

1. **LOVEBLE_UZBEKCHA.md** (Bu yerni o'qing birinchi!)
   - Bot nima qiladi
   - Loveble'da o'rnatish kerakli joylar
   - Webhook format
   - Checklist

2. **LOVEBLE_CHECKLIST_UZBEKCHA.md**
   - Har bir qadamni tekshirish
   - Loveble'dan olinushi kerak
   - Bot'da o'rnatish kerakli
   - FINAL CHECKLIST

3. **SEND_TO_LOVEBLE_AI.txt**
   - Loveble AI'ga yuboriladigan qisqa xabar
   - Mahsulotlar ro'yxati
   - O'rnatish joylar
   - Webhook format misoli

4. **loveble_integration_request.json**
   - Teknik JSON format
   - Barcha requirement'lar
   - Webhook payload example
   - Product mapping

### 📁 Loveble uchun Ingliz Tilida Fayllar:

5. **LOVEBLE_SETUP.md** - Setup guide (5 min)
6. **LOVEBLE_ADMIN.md** - Admin guide
7. **LOVEBLE_QUICK_START.md** - Quick reference
8. **LOVEBLE_EXAMPLES.md** - Real examples
9. **LOVEBLE_INTEGRATION.md** - Complete manual
10. **LOVEBLE_INDEX.md** - Navigation guide
11. **LOVEBLE_START.md** - Summary
12. **LOVEBLE_README.txt** - About docs

---

## 🎯 LOVEBLE AI'GA FAYLLARNI QANDAY YUBORISH?

### 1️⃣ Eng Muhim - Loveble'ga O'zbekchasini Yubor:

**Birinchi yubor:**
```
File: SEND_TO_LOVEBLE_AI.txt
Ko'piklashtirashu va Telegram yoki email'ga yuboring
```

**Ikkinchi yubor (agar so'rasalar):**
```
File: LOVEBLE_UZBEKCHA.md
Butun Uzbek tilida detailed guide
```

**Uchinchi yubor (teknik):**
```
File: loveble_integration_request.json
JSON format'da barcha requirement'lar
```

### 2️⃣ Loveble'dan Qanday Javob Kutish:

Loveble AI sizga berishi kerak:
- ✅ Shop ID
- ✅ API Key
- ✅ Webhook Secret
- ✅ 8 ta Product ID
- ✅ Webhook o'rnatildi (OK)
- ✅ Test webhook 200 returned (OK)

---

## 📝 LOVEBLE AI'GA YUBORILADIGAN MATNI

```
Assalomu alaikum!

Biz Telegram bot qilyaptibiz kahva do'konimizning
satuvlarini kuzatish uchun.

BOT NIMA QILADI:
• Real-time sotuv xabari (2 sekundda)
• Har kun kunlik hisobot (23:00)
• Har juma haftalik hisobot (23:05)
• Har oy oylik hisobot (23:10)
• Qoldig'i kuzatishi

MAHSULOTLAR (8 ta):
1. Espresso - 5,000 som
2. Cappuccino - 7,000 som
3. Latte - 8,000 som
4. Americano - 6,000 som
5. Flat White - 8,500 som
6. Macchiato - 7,500 som
7. Mocha - 9,000 som
8. Affogato - 9,000 som

SIZDAN KERAK:
1. Shop ID
2. API Key
3. Webhook Secret
4. Har bir mahsulotning Product ID (8 ta)
5. Webhook URL'ni o'rnatish:
   http://SERVER_IP:8443/webhook/loveble

WEBHOOK EVENTS:
✅ order_paid (to'langan buyurtmalar)
✅ order_completed (bajarilgan buyurtmalar)

SECURITY:
• Signature verification: HMAC-SHA256
• Header: X-Loveble-Signature

Ko'proq ma'lumot uchun LOVEBLE_UZBEKCHA.md faylini ko'ring!
```

---

## 🚀 STEP-BY-STEP PROCESS

### STEP 1: Loveble AI'ga Xabar Yubor (5 min)
```
1. SEND_TO_LOVEBLE_AI.txt'ni o'q
2. Textni copy qil
3. Loveble AI'ga yubor (Telegram/Email)
4. Javobni kut (1-24 soat)
```

### STEP 2: Javobni Olib Ko'r (Agar Savollar Bo'lsa)
```
Agar Loveble so'rasalar:
• LOVEBLE_UZBEKCHA.md'ni o'qit
• LOVEBLE_CHECKLIST_UZBEKCHA.md'ni ko'rsatit
• loveble_integration_request.json'ni yo'llat
```

### STEP 3: Credentials'ni Bot'ga Yoz
```
config.py faylini o'z:

LOVEBLE_API_KEY = "...ijobat key..."
LOVEBLE_WEBHOOK_SECRET = "...ijobat secret..."
LOVEBLE_SHOP_ID = "...ijobat shop id..."

PRODUCTS = {
    "cappuccino": { "loveble_id": "...cappuccino id..." },
    # va boshqa 7 ta
}
```

### STEP 4: Botni Ishga Tushir
```bash
cd coffee_system
python main.py
```

### STEP 5: Test Qil
```
Loveble POS'da test sotuv qil
Telegram'da xabar qabul qil
Barcha o'rnatildi! ✅
```

---

## 📋 CHECKLIST - LOVEBLE'DAN OLIB

Loveble ijobat beradigach tekshiring:

- [ ] Shop ID olingan
- [ ] API Key olingan
- [ ] Webhook Secret olingan
- [ ] Espresso Product ID olingan
- [ ] Cappuccino Product ID olingan
- [ ] Latte Product ID olingan
- [ ] Americano Product ID olingan
- [ ] Flat White Product ID olingan
- [ ] Macchiato Product ID olingan
- [ ] Mocha Product ID olingan
- [ ] Affogato Product ID olingan
- [ ] Webhook o'rnatildi (200 OK)
- [ ] order_paid event aktiv
- [ ] order_completed event aktiv
- [ ] Test webhook muaffaqiyatli

**Hammasi to'ldirildi?** → Config.py ni o'zgarit va `python main.py` qiling!

---

## 🎯 XABAR YUBORING!

### Loveble AI'ga Yo'llash Kerakli:

**Hamma fayllarni bir folder'da:**
```
coffee_system/
├── SEND_TO_LOVEBLE_AI.txt ← BIRINCHI YUBOR!
├── LOVEBLE_UZBEKCHA.md
├── LOVEBLE_CHECKLIST_UZBEKCHA.md
├── loveble_integration_request.json
└── (boshqa LOVEBLE_* fayllar)
```

**Qaysi yo'l orqali:**
- Telegram bot @loveble_support_bot
- Email: support@loveble.com (agar bo'lsa)
- Loveble dashboard chat
- WhatsApp (agar bo'lsa)

**Qanday yubor:**
1. SEND_TO_LOVEBLE_AI.txt'ni copy-paste qil
2. "Assalomu alaikum! Biz Telegram bot..." xabarni yubor
3. Loveble'dan javob kutish

---

## 💬 LOVEBLE IJOBAT BERGANDA

Agar Loveble quyidagilarni beradigan bo'lsa:

```json
{
  "shop_id": "shop_12345",
  "api_key": "sk_live_abcdef123...",
  "webhook_secret": "whsec_live_xyz789...",
  "products": {
    "espresso": "prod_espresso_1a2b3c",
    "cappuccino": "prod_cappuccino_4d5e6f",
    ...
  }
}
```

Bot'da config.py'ni o'zgarit:

```python
LOVEBLE_API_KEY = "sk_live_abcdef123..."
LOVEBLE_WEBHOOK_SECRET = "whsec_live_xyz789..."
LOVEBLE_SHOP_ID = "shop_12345"

PRODUCTS = {
    "espresso": { "loveble_id": "prod_espresso_1a2b3c" },
    "cappuccino": { "loveble_id": "prod_cappuccino_4d5e6f" },
    # va boshqa 6 ta
}
```

Ishga tushir:
```bash
python main.py
```

Test qil:
```
Loveble POS'da sotuv qil
Telegram'da xabar kutish
Barcha tayyor! ✅
```

---

## 🎁 Bot'da Tayyor:

✅ Flask server (port 8443)
✅ Telegram bot
✅ Database (SQLite)
✅ Scheduler (kunlik/haftalik/oylik)
✅ 8 mahsulot
✅ Xavfsizlik (signature verification)
✅ Logging
✅ Error handling

**Faqat Loveble ma'lumotlari kerak!**

---

## 📞 QISQA JADVAL

| Qadam | Nima | Vaqt |
|-------|------|------|
| 1 | Loveble AI'ga xabar | 5 min |
| 2 | Javob kutish | 1-24 soat |
| 3 | Config.py ni o'zgarish | 2 min |
| 4 | Bot ishga tushirish | 1 min |
| 5 | Test qilish | 5 min |

**Jami:** ~1-24 soat ⏱️

---

## ✨ TUGAGANI!

**Tayyorlik shu:** ✅
**Loveble integrationsya:** ⏳ Loveble AI'dan kutish
**Bot:** ✅ Tayyor
**Dokumentatsiya:** ✅ O'zbek + Ingliz
**Config template:** ✅ Tayyor

**Endi Loveble AI'ga xabar yubor!** 🚀

---

**Ko'proq savollar?**
- LOVEBLE_UZBEKCHA.md'ni o'q
- LOVEBLE_CHECKLIST_UZBEKCHA.md'ni tekshir
- loveble_integration_request.json'ni o'qish

**Tayyyorligi sana:** 27-Yanvar 2026
**Status:** ✅ LOVEBLE AI'GA YUBORILADIGA TAYYOR!
**Versiya:** 1.0.0

---

**NEXT STEP:** SEND_TO_LOVEBLE_AI.txt ni o'qiy va Loveble AI'ga yubor! 📧
