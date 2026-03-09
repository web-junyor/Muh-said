# Jarvis — Telegram bot

Telegramda Jarvis bilan suhbat. Barcha javoblar o‘zbekcha.

## Tez ishga tushirish

1. `.env` yarating (BOT_TOKEN, GROQ_API_KEY).
2. **run_bot.bat** ni ishga tushiring — u avtomatik venv yaratadi, kutubxonalarni o‘rnatadi va botni ishlatadi.

Yoki qo‘lda (boshqa loyihalardagi googletrans va httpx bilan to‘qnashmaslik uchun venv ishlatish ma’qul):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Batafsil: `jarvis/README.md`.

---

## Barcha bo'limlar (yakuniy)

| Bo'lim | Tugma | Nima qiladi |
|--------|--------|--------------|
| **Buyruqlar** | 📋 Buyruqlar | ⚡ Buyruq bajarish yoki 💬 Suhbatlashish |
| **Suhbatlashish** | — | 💬 Suhbat — Jarvis javob beradi |
| **Hamma buyruqlar** | 📜 Hamma buyruqlar | Standart + qo'shilgan buyruqlar, tahrirlash/o'chirish |
| **O'rgatish** | 📚 O'rgatish | Ilova, suhbat javobi, yangi buyruq (och/yop) |
| **Bot yop** | 🔒 Bot yop | Botni qulflash, keyin parol so'raydi |

Ishga tushirish: `cd jarvis\telegram_bot` → `python main.py` (parol kiritiladi).

---

## Bot nima qila oladi? (tushuntirish)

### 1. 📋 Buyruqlar
Bu bo‘limda ikki rejim tanlanadi:

- **⚡ Buyruqlar bajarish** — kompyuteringizda ilovalarni ochish/yopish, brauzerda qidiruv va h.k. Buning uchun quyidagi kabi matn yuborasiz: `musiqa och`, `brauzer och`, `kalkulator yop`.
- **💬 Suhbatlashish** — Jarvis bilan suhbat. Savol yozasiz, Jarvis javob beradi. O‘rgatilgan savol-javoblar avval tekshiriladi. Tarixni tozalash: «suhbatni tozalash» yozing.

---

### 2. 📜 Hamma buyruqlar
Barcha buyruqlar ro‘yxati: standart (musiqa, brauzer, kalkulator, Chrome profillar, ai och/yop va h.k.) va siz qo‘shgan buyruqlar. Har biriga **Tahrirlash** / **O‘chirish** tugmalari (standart buyruqlarni o‘zgartirib bo‘lmaydi, faqat ko‘rsatiladi).

---

### 3. 📚 O'rgatish
Botga yangi narsalar o‘rgatish:

- **🖥️ Ilovalarni o'rgatish** — ilova yo‘li va nomi (masalan: `C:\Program Files\MyApp, myapp.exe`). Keyin «ilova nomini och» kabi so‘zlar orqali ochish mumkin.
- **💬 Suhbatlashishni o'rgatish** — savol va bot javobini yozasiz; keyin shu savol kelsa bot shu javobni beradi.
- **➕ Buyruq qo'shish (och/yop)** — yangi «ochish» yoki «yopish» buyruqi (nomi + fayl/ilova yo‘li yoki yopiladigan jarayon nomi).

---

### 4. 🔒 Bot yop
Botni qulflash: tugma bosilganda siz «chiqdim» deb hisoblaysiz, keyin bot yana parol so‘raydi. Boshqalar sizning hisobingizsiz foydalana olmaydi.

---

### Standart buyruqlar (qisqacha)

| Nima | Misol |
|------|--------|
| Musiqa | `musiqa och`, `musiqa yop` |
| Kalkulator | `kalkulator och`, `kalkulator yop`, `kalkulator och hisobla: 5+5` |
| Brauzer | `brauzer och`, `brauzer qidir Python`, `brauzer yop` |
| Chrome profillar | `MS och`, `MS yop`, `MS qidir ...`, `SHMS och` va h.k. |
| YouTube | `yutub och`, `yutub yop`, `yutub qidir ...` |
| ChatGPT | `ai och`, `ai yop`, `prompt: matn` |
| Bloknot, fayl, Telegram | `bloknot och`, `fayl och`, `telegram och` va yop |
| Kalendar, Cursor, VS Code | `kalendar och`, `cursor och`, `vs code och` va yop |
| Ekran, Wi‑Fi | `ekrani yop` / `ekrani yoq`, `wi-fi yoq nomi: MW`, `wi-fi yop` |
| Hammasi yop | `hamma yop` |

Barchasi **Windows** da ishlaydi (ilovalar ochiladi/yopiladi). `.env` va `config` da Chrome profillar, musiqa fayli va boshqa yo‘llar sozlanadi.
