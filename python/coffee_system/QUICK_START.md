# QUICK START GUIDE - Coffee Shop Bot

## ⚡ 5 Minutes to Running Bot

### 1. Copy Bot Token
1. Open Telegram → @BotFather
2. /newbot → choose name → get TOKEN
3. Copy it

### 2. Get Your Admin ID
1. Open Telegram → @userinfobot
2. Get your ID number
3. Copy it

### 3. Edit config.py
```python
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"  # Paste token here
TELEGRAM_ADMIN_ID = 987654321  # Paste your ID here
```

### 4. Install & Run
```bash
pip install -r requirements.txt
python main.py
```

### 5. Test Bot
- Open Telegram
- Find your bot
- Send: `/start`
- See buttons? ✅ DONE!

---

## 🔗 Loveble Setup (Optional, but Recommended)

1. Get Loveble credentials
2. Add to config.py:
   ```python
   LOVEBLE_API_KEY = "your_key"
   LOVEBLE_SHOP_ID = "your_shop_id"
   LOVEBLE_WEBHOOK_SECRET = "your_secret"
   ```

3. In Loveble Dashboard:
   - Settings → Webhooks
   - Add: `https://yourdomain.com/webhook/loveble`
   - Add Secret from step 2

4. Done! Bot now syncs with Loveble

---

## 📊 What Bot Does

✅ **Shows daily/weekly/monthly sales**
✅ **Alerts when stock is low**
✅ **Syncs with Loveble POS**
✅ **Tracks all sales**
✅ **Admin-only access**

---

## 🆘 Problem? Check This

| Issue | Fix |
|-------|-----|
| Bot not responding | Check token in config.py |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Database error | Delete `coffee.db`, restart |
| Port error | Run on different port in config.py |

---

## 📞 Full Documentation

- **SETUP.md** - Detailed setup (production)
- **README_NEW.md** - Complete reference
- **SYSTEM_OVERVIEW.py** - Architecture & features
