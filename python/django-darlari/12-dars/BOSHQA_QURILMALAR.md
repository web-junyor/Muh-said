# Boshqa qurilmalar (telefon, planshet) saytga kirishi uchun

Laptop yoqilgan paytda boshqa qurilmalar ham "Sayt ochish" linkini ochishi uchun:

## 1. Laptop IP manzilini biling
- **Windows:** `ipconfig` — **IPv4 Address** (masalan `192.168.1.100`)
- **Mac/Linux:** `ifconfig` yoki `ip addr`

## 2. Django ni barcha interfeyslarda ishga tushiring
```bash
cd django-darlari/12-dars
python manage.py runserver 0.0.0.0:8001
```

## 3. PUBLIC_SITE_URL ni laptop IP ga qo'ying
`config/settings.py` da yoki environment variable:
```bash
set PUBLIC_SITE_URL=http://192.168.1.100:8001
python manage.py runserver 0.0.0.0:8001
```
(O'rniga o'z IP ingizni yozing.)

Shundan keyin botdagi "Sayt ochish" linki `http://192.168.1.100:8001/...` bo'ladi va telefon/planshet bir xil Wi‑Fi da bo'lsa usha linkni ochadi.
