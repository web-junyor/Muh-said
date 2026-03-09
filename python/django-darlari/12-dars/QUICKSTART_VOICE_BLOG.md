# 🚀 TEZKOR BOSHLASH - VOICE BLOG SYSTEM

## 1️⃣ DJANGO ISHGA TUSHIRISH

```powershell
# Workspace: c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\django-darlari\12-dars

cd "c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\django-darlari\12-dars"

# Virtual environment (agar mavjud bo'lsa)
.\.venv\Scripts\Activate.ps1

# Django migrations

python manage.py migrate
# Server ishga tushish
python manage.py runserver
```

**Sayt**: `http://localhost:8000`

---

## 2️⃣ BOT ISHGA TUSHIRISH

```powershell
# Bosh workspace
cd "c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\django-darlari\12-dars\bot"

# .env faylni tekshiring
# BOT_TOKEN = ...
# DJANGO_BASE_URL = http://localhost:8000
# DJANGO_BOT_KEY = ...

# Bot ishga tushish
python main.py
```

---

## 3️⃣ TELEGRAM BOT BILAN TEKSHIRISH

### Birinchi test: **Tekst + Ovoz (Single)**
```
/start
👉 Tilni tanlang: O'zbekcha ✅
📝 Yangi blog yozish
🧾 Sarlavhani yozing: "Mening Birinchi Blogi"
📄 Blog matniga: OVOZLI XABAR YUBORING
✅ Ovoz qabul qilindi!
👉 ✅ Tayyorman tugmasini bosing
📷 Rasim qo'shasizmi? ❌ Kiritmaslik
✅ Blog saqlandi! 🔗 Sayt ochish
```

### Ikkinchi test: **Ko'p Ovozli Xabarlar (Multiple)**
```
/start
👉 Tilni tanlang: Ruscha ✅
📝 Написать новый блог
🧾 Введите заголовок: "Мой День"
📄 В теле блога: ПЕРВОЕ ГОЛОСОВОЕ СООБЩЕНИЕ
✅ Голос принят.
👉 ➕ Добавить ещё голос
📄 ВТОРОЕ ГОЛОСОВОЕ СООБЩЕНИЕ
✅ Голос принят.
👉 ➕ Добавить ещё голос
📄 ТРЕТЬЕ ТЕКСТОВОЕ СООБЩЕНИЕ (text да'mga)
✅ Текст принят.
👉 ✅ Готово
📷 Добавить фото? ➕ Добавьте фото
📸 [RASM YUBORING]
✅ Блог создан! 🔗 Открыть на сайте
```

---

## 4️⃣ SAYTDA TEKSHIRISH

1. **Brauzer**: `http://localhost:8000`
2. **Login**: `admin/admin` (agar mavjud bo'lsa)
3. **Blog ko'rish**: `http://localhost:8000/post/<id>/?t=<token>`
4. **Ko'rish**: Multi-qator ovozlar **"\n\n"** bilan ajratib ko'rinishi kerak

---

## ✅ CHEKLİST - HAMMASI ISHLAYAPTIMI?

- [ ] Django `http://localhost:8000` da ishlaydi
- [ ] Bot token ishlaydi
- [ ] Bot `/start` ga javob beradi
- [ ] Blog sarlavhasi kiritiladi
- [ ] **YANGI**: Birinchi ovozli xabar qabul qilinadi
- [ ] **YANGI**: "➕ Yana ovoz" tugmasi ko'rinadi
- [ ] **YANGI**: Ikkinchi ovozli xabar qabul qilinadi
- [ ] **YANGI**: "✅ Tayyorman" tugmasini bosish mumkin
- [ ] Blog Django DB-da saqlanadi
- [ ] Saytda multi-qator ko'rinadi
- [ ] Rasim qo'shilishi mumkin
- [ ] "Bloglar tarixi" ishlaydi

---

## 🐛 TEZKOR FIX (Agar Muammo Bo'lsa)

### Muammo: Bot ovozni taniy olmaydi
```
FIX: ffmpeg o'rnatilganini tekshiring
Windows: https://ffmpeg.org/download.html
Yoki: choco install ffmpeg
```

### Muammo: Bot Django-ga ulanmaydi
```
FIX: .env faylni tekshiring:
- DJANGO_BASE_URL = http://localhost:8000 ✅
- DJANGO_BOT_KEY = (o'zgaruvchisi) ✅
```

### Muammo: Saytda text ko'rinmaydi
```
FIX: Django server qayta ishga tushiring:
Ctrl+C -> python manage.py runserver
```

---

## 📞 DEBUGGING

### Terminal 1: Django
```powershell
python manage.py runserver
```

### Terminal 2: Bot
```powershell
python main.py
# ERROR va WARNING'larni tekshiring
```

### Terminal 3: Logs (optional)
```powershell
tail -f bot.log
```

---

## 🎯 KEYINGI BOSQICHLAR

1. ✅ **Bot testlash**
2. ✅ **Saytda ko'rsatish**
3. ⏭️ Deployment (heroku, railway, vps)
4. ⏭️ Admin panel
5. ⏭️ Analytics

---

Tayyor? 🚀 `python main.py` boshlang!
