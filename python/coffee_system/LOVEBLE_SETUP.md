# Loveble Configuration - Step by Step
# Loveble Konfiguratsiyasi - Bosqichma Bosqich

## 🎯 Your Task in 5 Minutes

You need to **find 4 things from Loveble** and **put them in config.py**

---

## Step 1: Open Loveble Dashboard

Go to: `https://loveble.com` → Login with your credentials

Look for: **Settings** or **Sozlamalar** or **Configuration**

---

## Step 2: Find API Key

**In Loveble Dashboard:**
1. Click **Settings** (Sozlamalar)
2. Find **API Keys** or **API Integration**
3. Look for something like:
   ```
   API Key: sk_live_5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p
   ```
4. **Copy it** (click icon or select all with Ctrl+C)

**In config.py:**
Find line 11:
```python
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY_HERE"
```

Replace with your API key:
```python
LOVEBLE_API_KEY = "sk_live_5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"
```

---

## Step 3: Find Shop ID

**In Loveble Dashboard:**
1. Look for **Shop Settings** or **Do'kon Sozlamalari**
2. Find **Shop ID**:
   ```
   Shop ID: shop_1234567890abcdef
   ```
3. **Copy it**

**In config.py:**
Find line 14:
```python
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID_HERE"
```

Replace with:
```python
LOVEBLE_SHOP_ID = "shop_1234567890abcdef"
```

---

## Step 4: Find Webhook Secret

**In Loveble Dashboard:**
1. Go to **Webhooks** or **Veb Hakerlar**
2. Look for existing webhook or **Add Webhook**
3. Find **Secret** or **Webhook Secret**:
   ```
   Secret: whsec_live_xyz123abc789def456ghi789jkl012
   ```
4. **Copy it**

**In config.py:**
Find line 13:
```python
LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET_HERE"
```

Replace with:
```python
LOVEBLE_WEBHOOK_SECRET = "whsec_live_xyz123abc789def456ghi789jkl012"
```

---

## Step 5: Find Product IDs

**In Loveble Dashboard:**
1. Go to **Products** or **Mahsulotlar**
2. Open each coffee product
3. Look for **Product ID** or **ID** field
4. Copy each one

**Example what you'll find:**
```
Cappuccino:
  Product ID: prod_cappuccino_a1b2c3d4e5f6

Espresso:
  Product ID: prod_espresso_x9y8z7w6v5u4

Latte:
  Product ID: prod_latte_m1n2o3p4q5r6

... and so on for all 8 products
```

**In config.py:**
Find the **PRODUCTS** section (around line 25):

```python
PRODUCTS = {
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,
        "loveble_id": "cappuccino_loveble_id"  # ← CHANGE THIS
    },
    "espresso": {
        "id": "1",
        "name": "Espresso",
        "initial_stock": 12,
        "price": 5000,
        "loveble_id": "espresso_loveble_id"    # ← CHANGE THIS
    },
    "latte": {
        "id": "3",
        "name": "Latte",
        "initial_stock": 12,
        "price": 8000,
        "loveble_id": "latte_loveble_id"       # ← CHANGE THIS
    },
    "americano": {
        "id": "4",
        "name": "Americano",
        "initial_stock": 12,
        "price": 6000,
        "loveble_id": "americano_loveble_id"   # ← CHANGE THIS
    },
    "flat_white": {
        "id": "5",
        "name": "Flat White",
        "initial_stock": 12,
        "price": 8500,
        "loveble_id": "flatwhite_loveble_id"   # ← CHANGE THIS
    },
    "macchiato": {
        "id": "6",
        "name": "Macchiato",
        "initial_stock": 12,
        "price": 7500,
        "loveble_id": "macchiato_loveble_id"   # ← CHANGE THIS
    },
    "mocha": {
        "id": "7",
        "name": "Mocha",
        "initial_stock": 12,
        "price": 9000,
        "loveble_id": "mocha_loveble_id"       # ← CHANGE THIS
    },
    "affogato": {
        "id": "8",
        "name": "Affogato",
        "initial_stock": 12,
        "price": 9000,
        "loveble_id": "affogato_loveble_id"    # ← CHANGE THIS
    },
}
```

**Replace all the `loveble_id` values with real ones from Loveble:**

```python
PRODUCTS = {
    "cappuccino": {
        "id": "2",
        "name": "Cappuccino",
        "initial_stock": 12,
        "price": 7000,
        "loveble_id": "prod_cappuccino_a1b2c3d4e5f6"  # ✅ REAL ID!
    },
    "espresso": {
        "id": "1",
        "name": "Espresso",
        "initial_stock": 12,
        "price": 5000,
        "loveble_id": "prod_espresso_x9y8z7w6v5u4"    # ✅ REAL ID!
    },
    "latte": {
        "id": "3",
        "name": "Latte",
        "initial_stock": 12,
        "price": 8000,
        "loveble_id": "prod_latte_m1n2o3p4q5r6"       # ✅ REAL ID!
    },
    # ... and so on
}
```

---

## Step 6: Configure Webhook in Loveble

Now that you have the webhook secret, you need to **tell Loveble** where to send the webhook.

**In Loveble Dashboard:**
1. Go to **Webhooks**
2. Click **Add Webhook** or **Yangi Veb Hakerini Qo'sh**
3. Fill in:
   - **URL:** `http://YOUR_SERVER_IP:8443/webhook/loveble`
     - Example: `http://192.168.1.100:8443/webhook/loveble`
     - Or with domain: `https://mycoffee.com:8443/webhook/loveble`
   - **Secret:** Paste the webhook secret
   - **Events:** Select:
     - ✅ `order_paid` (When customer paid)
     - ✅ `order_completed` (When order finished)
4. Click **Save**

---

## Step 7: Verify config.py

**Open config.py** and check lines 11-14:

```python
# Line 11
LOVEBLE_API_KEY = "sk_live_5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"  # ✅ Filled?

# Line 13
LOVEBLE_WEBHOOK_SECRET = "whsec_live_xyz123abc789def456ghi789jkl012"  # ✅ Filled?

# Line 14
LOVEBLE_SHOP_ID = "shop_1234567890abcdef"  # ✅ Filled?
```

**Verify PRODUCTS section** has all real loveble_ids:
```python
"cappuccino": { "loveble_id": "prod_cappuccino_a1b2c3d4e5f6" }  # ✅ Real?
"espresso": { "loveble_id": "prod_espresso_x9y8z7w6v5u4" }      # ✅ Real?
# ... all 8 products should have REAL loveble_ids
```

---

## Step 8: Save and Test

1. **Save config.py** (Ctrl+S in your editor)
2. **Restart the bot:**
   ```bash
   # Stop current bot (Ctrl+C)
   # Then:
   python main.py
   ```

3. **Test it works:**
   ```bash
   # In another terminal:
   curl http://localhost:8443/health
   # Should return: {"status":"ok","bot":"running"}
   ```

4. **Make a test sale in Loveble POS**
5. **Check Telegram** - you should get notification in 2 seconds!

---

## Before & After Examples

### BEFORE (Wrong - Placeholders)
```python
LOVEBLE_API_KEY = "YOUR_LOVEBLE_API_KEY_HERE"
LOVEBLE_WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET_HERE"
LOVEBLE_SHOP_ID = "YOUR_SHOP_ID_HERE"

PRODUCTS = {
    "cappuccino": {
        "loveble_id": "cappuccino_loveble_id"  # ❌ Placeholder!
    },
    "espresso": {
        "loveble_id": "espresso_loveble_id"    # ❌ Placeholder!
    },
    # ...
}
```

### AFTER (Correct - Real Values)
```python
LOVEBLE_API_KEY = "sk_live_5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"
LOVEBLE_WEBHOOK_SECRET = "whsec_live_xyz123abc789def456ghi789jkl012"
LOVEBLE_SHOP_ID = "shop_1234567890abcdef"

PRODUCTS = {
    "cappuccino": {
        "loveble_id": "prod_cappuccino_a1b2c3d4e5f6"  # ✅ Real!
    },
    "espresso": {
        "loveble_id": "prod_espresso_x9y8z7w6v5u4"    # ✅ Real!
    },
    # ...
}
```

---

## ⚠️ IMPORTANT REMINDERS

1. **Don't share your API keys!** Keep config.py private
2. **API keys and secrets are case-sensitive** - Copy them exactly
3. **Update ALL 8 product loveble_ids** - Don't skip any!
4. **Webhook URL must match** - Port 8443, exact path `/webhook/loveble`
5. **Test after updating** - Make a sale and check Telegram

---

## 🆘 If Something Goes Wrong

**Error: "Invalid webhook signature"**
- ❌ Webhook secret doesn't match
- ✅ Copy exact secret from Loveble again
- ✅ Restart bot

**Error: "Product not found"**
- ❌ Product loveble_id is wrong
- ✅ Check Loveble dashboard for correct IDs
- ✅ Update config.py

**Error: "404 Not Found" on webhook**
- ❌ Webhook URL wrong in Loveble
- ✅ Should be: `http://YOUR_IP:8443/webhook/loveble`
- ✅ Check port 8443 is open

**Error: "Connection refused"**
- ❌ Bot not running
- ✅ Start bot: `python main.py`

---

## 📋 Checklist

- [ ] Found API Key in Loveble → Added to config.py line 11
- [ ] Found Shop ID in Loveble → Added to config.py line 14
- [ ] Found Webhook Secret in Loveble → Added to config.py line 13
- [ ] Found all 8 product IDs in Loveble
- [ ] Updated all 8 loveble_ids in PRODUCTS section
- [ ] Set webhook URL in Loveble: `http://YOUR_IP:8443/webhook/loveble`
- [ ] Set webhook secret in Loveble (matches config.py)
- [ ] Saved config.py
- [ ] Restarted bot: `python main.py`
- [ ] Tested webhook: `curl http://localhost:8443/health`
- [ ] Made test sale in Loveble POS
- [ ] Got Telegram notification within 2 seconds

**All checked? ✅ You're done! Bot is working!**

---

## File to Edit

**Full path:**
```
c:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python\coffee_system\config.py
```

**Or in VS Code:**
- Open folder: `coffee_system`
- Open file: `config.py`
- Edit lines 11-14 and PRODUCTS section
- Save (Ctrl+S)

---

**That's it! 5 minutes and you're done!**
