# 🚀 Serverga O'rnatish - 3 Qadami

## Qisqa Gid

**Vaqti:** 5-10 daqiqa

---

## QADAMI 1: Server'ga kirish

```bash
ssh root@YOUR_SERVER_IP
# Yoki: ssh user@YOUR_SERVER_IP (keyin sudo dan foydalaning)
```

---

## QADAMI 2: Code'ni yuklash

```bash
cd /home
git clone <YOUR_GITHUB_REPO_URL> coffee-bot
# Yoki scp bilan:
# scp -r ./coffee_system root@SERVER_IP:/home/coffee-bot/
```

---

## QADAMI 3: Deploy skriptini ishga tushirish

```bash
cd /home/coffee-bot/coffee_system
chmod +x deploy.sh
sudo bash deploy.sh
```

**Script avtomatik qiladi:**
- ✅ Python va dependencies o'rnatish
- ✅ Virtual environment yaratish
- ✅ Systemd service yaratish
- ✅ Firewall o'rnatish (8443 port)
- ✅ Bot ishga tushirish

---

## QADAMI 4: Config'ni yangilash (MUHIM!)

Deploy'dan oldin yoki keyin:

```bash
nano /home/coffee-bot/coffee_system/config.py
```

**O'zgartirilishi kerak:**

```python
# Line 11-14 (Loveble credentials):
LOVEBLE_API_KEY = "sk_live_..."
LOVEBLE_WEBHOOK_SECRET = "whsec_live_..."
LOVEBLE_SHOP_ID = "said_coffee_shop"

# PRODUCTS section - barcha loveble_id'lar:
PRODUCTS = {
    "espresso": { "loveble_id": "ded1_gahvaxona" },
    "cappuccino": { "loveble_id": "prod_cappuccino" },
    # ... va hokazolar
}
```

---

## ✅ Tekshirish

### 1. Service ishlamoqda?
```bash
systemctl status coffee-bot
```

### 2. Logs ko'rish
```bash
tail -f /var/log/coffee-bot/coffee_bot.log
```

### 3. Webhook test
```bash
python3 test_webhook.py
```

---

## 🔗 Loveble'da Webhook O'rnatish

**Settings > Integrations > Webhooks**

```
URL: https://YOUR_SERVER_IP:8443/webhook/loveble
Events: ✅ order_paid
        ✅ order_completed
Header: X-Loveble-Signature
Secret: <LOVEBLE_WEBHOOK_SECRET dan>
```

---

## 🆘 Muammolar

| Muamma | Yechim |
|--------|--------|
| Service ishlamayapti | `sudo systemctl restart coffee-bot` |
| Port 8443 band | `sudo lsof -i :8443` va kill qiling |
| Database xatosi | `rm coffee.db` va qayta ishga tushiring |
| Signature xatosi | `config.py`da LOVEBLE_WEBHOOK_SECRET ni tekshiring |

---

## 📞 Tezda Qollamalar

```bash
# Logs ko'rish
tail -100 /var/log/coffee-bot/coffee_bot.log

# Service qayta ishga tushirish
systemctl restart coffee-bot

# Config ni edit qilish
nano /home/coffee-bot/coffee_system/config.py

# Webhook test qilish
cd /home/coffee-bot/coffee_system
python3 test_webhook.py
```

---

## 🎉 Tugallandi!

Bot serverda ishga tushdi va Loveble webhooklarini qabul qilmoqda! ✨
