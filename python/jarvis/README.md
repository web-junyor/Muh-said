# Jarvis — bitta papkada hammasi

Bu **jarvis** papkasida Jarvisning uch turi bitta joyda: **Telegram bot**, ovozli yordamchi (Python) va veb chatbot (Next.js). Hammasi o‘zbekcha va odobli.

---

## Papka tuzilishi

```
jarvis/
├── README.md              ← siz o‘qiyapsiz
├── jarvis.py              ← ovozli yordamchi (mikrofon orqali buyruq)
├── run_jarvis.bat         ← ovozli Jarvisni ishga tushirish (Windows)
├── requirements_ovoz.txt  ← ovozli yordamchi uchun Python kutubxonalari
├── telegram_bot/          ← Jarvis Telegram bot (asosiy — bot ko‘rinishida)
│   ├── main.py
│   ├── handlers.py
│   ├── groq_client.py
│   ├── prompt.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
└── jarvis_chatbot/        ← veb chatbot (brauzerda chat)
    ├── package.json
    ├── .env.local          ← siz yaratasiz (GROQ_API_KEY)
    └── ...
```

---

## 1. Jarvis Telegram bot (telegram_bot)

**Nima qiladi:** Telegramda bot sifatida ishlaydi. Xabar yuborasiz — Jarvis Groq (Llama) orqali o‘zbekcha, odobli javob yozadi. Suhbat tarixi saqlanadi.

### Nimalar kerak

- **Python 3**
- **Telegram bot token** — [@BotFather](https://t.me/BotFather) dan yangi bot yarating, token oling.
- **Groq API kaliti** — [console.groq.com](https://console.groq.com) → API Keys.

### Qanday ishga tushirish

1. **telegram_bot** papkasiga o‘ting:
   ```bash
   cd telegram_bot
   ```

2. **.env** fayl yarating (yoki `.env.example` dan nusxa olib to‘ldiring):
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   GROQ_API_KEY=gsk_...
   ```

3. Kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

4. Botni ishga tushiring:
   ```bash
   python main.py
   ```
   To‘xtatish: **Ctrl+C**.

5. Telegramda botni oching va `/start` bosing. Keyin istalgan savol yozing — Jarvis javob beradi.

---

## 2. Ovozli Jarvis (jarvis.py)

**Nima qiladi:** Mikrofon orqali "Jarvis" deb ayting, keyin buyruq (masalan: soat necha, muzikani qo‘y, telegram och). Jarvis ovozda javob beradi.

### Nimalar kerak

- **Python 3** (kompyuteringizda o‘rnatilgan bo‘lishi kerak).
- **Kutubxonalar:**  
  Terminalda `jarvis` papkasida:
  ```bash
  pip install -r requirements_ovoz.txt
  ```
  Agar `PyAudio` xato bersa (Windows):  
  `pip install pipwin` → keyin `pipwin install pyaudio`.
- **Mikrofon** ulangan va ishlashi kerak.
- **Internet** (ovozni matnga aylantirish uchun Google ishlatiladi).

### Qanday ishga tushirish

- **Windows:** `run_jarvis.bat` ni ikki marta bosing (yoki terminalda `run_jarvis.bat` yozing).
- **Yoki:** Terminalda `jarvis` papkasiga o‘ting va:
  ```bash
  python jarvis.py
  ```
  To‘xtatish: **Ctrl+C**.

### Qisqacha buyruqlar

- Soat necha / xozirgi vaqt  
- Muzikani qo‘y / musiqani yop  
- Brauzerni och / yop  
- Kalkulyator, bloknot, Telegram, VS Code och/yop  
- "Latifa aytib ber"  
- "Hamma ilovalarni yop"

Batafsil: `jarvis.py` ichidagi `opts["cmds"]` da.

---

## 3. Veb chatbot (jarvis_chatbot)

**Nima qiladi:** Brauzerda chat: xabar yozasiz, Jarvis Groq (Llama) orqali o‘zbekcha, odobli javob beradi. Ovozli javob (TTS) ham bor.

### Nimalar kerak

- **Node.js** (va `pnpm` yoki `npm`) — kompyuteringizda o‘rnatilgan bo‘lishi kerak.
- **Groq API kaliti** — bepul: [console.groq.com](https://console.groq.com) → API Keys → yangi kalit yarating.

### Qanday ishga tushirish

1. **jarvis_chatbot** papkasiga o‘ting:
   ```bash
   cd jarvis_chatbot
   ```

2. **Kalit** uchun `.env.local` fayl yarating (papka ichida). Ichiga yozing:
   ```
   GROQ_API_KEY=sizning_groq_kalitingiz
   ```

3. **Kutubxonalarni** o‘rnating:
   ```bash
   pnpm install
   ```
   (yoki `npm install`)

4. **Serverni** ishga tushiring:
   ```bash
   pnpm dev
   ```
   (yoki `npm run dev`)

5. Brauzerda **http://localhost:3000** oching. Chat o‘zbekcha va odobli.

Batafsil: `jarvis_chatbot/README.md`.

---

## Qisqacha: nima kerak?

| Qaysi qismi           | Kerak bo‘ladigan narsalar |
|-----------------------|---------------------------|
| **Telegram bot**      | Python, `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `pip install -r telegram_bot/requirements.txt` |
| **Ovozli Jarvis**     | Python, mikrofon, `pip install -r requirements_ovoz.txt` |
| **Veb chatbot**       | Node.js, Groq API kaliti (`.env.local`), `pnpm install` va `pnpm dev` |

Uchalasi mustaqil: istagan birini ishlatishingiz mumkin.
