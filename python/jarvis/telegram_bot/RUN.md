# Jarvis Telegram bot — ishga tushirish

## Terminalda botni ishga tushirish (yakuniy buyruq)

**PowerShell yoki CMD da (bitta qator):**

```powershell
cd "c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\jarvis\telegram_bot" && python app.py
```

**Yoki ikki qadam:**
```powershell
cd "c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\jarvis\telegram_bot"
python app.py
```

**To'xtatish:** `Ctrl+C`

---

**Yoki** `run_bot.bat` faylini ikki marta bosing (bot papkasida).

---

## 2. "Timed out" xatosi bo'lsa

- **Internet:** Wi‑Fi yoki mobil internet ishlayotganiga ishonch hosil qiling.
- **Telegram bloklangan bo'lsa:** VPN yoqib qayta urinib ko'ring.
- **Firewall:** Windows Defender yoki antivirus Telegram (api.telegram.org) ga ruxsat bergan bo‘lishi kerak.

---

## 3. .env tekshiruvi

`jarvis/telegram_bot/.env` faylida:

- `TELEGRAM_BOT_TOKEN` yoki `BOT_TOKEN` — @BotFather dan olingan token
- `GROQ_API_KEY` — Sun'iy intellekt API kaliti (suhbat uchun, ixtiyoriy)
