# Loveble Integration Documentation Index
# Loveble Integratsiyasining Dokumentatsiya Ro'yxati

## 📚 Documentation Files

Choose the guide that best matches your need:

### 🚀 **Start Here** (5 minutes)
**File:** `LOVEBLE_SETUP.md`
- **What:** Step-by-step setup instructions
- **Who:** First-time setup
- **Time:** 5 minutes
- **Contains:**
  - How to find credentials in Loveble
  - How to update config.py
  - How to set webhook URL
  - Checklist to verify everything works

👉 **[Read LOVEBLE_SETUP.md](LOVEBLE_SETUP.md)**

---

### 📱 **For Admins** (10 minutes)
**File:** `LOVEBLE_ADMIN.md`
- **What:** Overview of what the bot does
- **Who:** Admin/owner of coffee shop
- **Time:** 10 minutes
- **Contains:**
  - What bot does when Loveble sends data
  - Daily/weekly/monthly reports
  - Telegram commands
  - Troubleshooting guide
  - Security features explained

👉 **[Read LOVEBLE_ADMIN.md](LOVEBLE_ADMIN.md)**

---

### ⚡ **Quick Reference** (2 minutes)
**File:** `LOVEBLE_QUICK_START.md`
- **What:** Quick lookup guide
- **Who:** Need quick answers
- **Time:** 2 minutes
- **Contains:**
  - Configuration checklist (30 seconds)
  - Payload format
  - Debugging commands
  - Common issues & fixes
  - Success indicators

👉 **[Read LOVEBLE_QUICK_START.md](LOVEBLE_QUICK_START.md)**

---

### 📊 **Real Examples** (15 minutes)
**File:** `LOVEBLE_EXAMPLES.md`
- **What:** Real examples with diagrams
- **Who:** Want to understand how it works
- **Time:** 15 minutes
- **Contains:**
  - Architecture diagram
  - Real webhook examples (1, 2, 3 products)
  - Telegram notification examples
  - Database schema after sales
  - Complete flow diagram
  - Testing examples with code
  - Deployment checklist

👉 **[Read LOVEBLE_EXAMPLES.md](LOVEBLE_EXAMPLES.md)**

---

### 📖 **Complete Guide** (30 minutes)
**File:** `LOVEBLE_INTEGRATION.md`
- **What:** Comprehensive guide with all details
- **Who:** Need full understanding
- **Time:** 30 minutes
- **Contains:**
  - What webhooks are and formats
  - How to set up webhooks in Loveble
  - Full config.py guide
  - Product synchronization
  - Testing with curl and Python
  - Error solutions
  - Production deployment
  - Monitoring and debugging

👉 **[Read LOVEBLE_INTEGRATION.md](LOVEBLE_INTEGRATION.md)**

---

## 🎯 Quick Navigation by Task

| I want to... | Read this | Time |
|-----------|----------|------|
| **Start using bot right now** | LOVEBLE_SETUP.md | 5 min |
| **Understand what bot does** | LOVEBLE_ADMIN.md | 10 min |
| **See an example webhook** | LOVEBLE_EXAMPLES.md | 5 min |
| **See all Telegram commands** | LOVEBLE_ADMIN.md | 2 min |
| **Debug webhook signature error** | LOVEBLE_INTEGRATION.md → Section 7 | 3 min |
| **Set up production deployment** | LOVEBLE_INTEGRATION.md → Section 8 | 10 min |
| **Test webhook manually** | LOVEBLE_QUICK_START.md → Debugging | 5 min |
| **Understand database schema** | LOVEBLE_EXAMPLES.md → Database Schema | 3 min |
| **See real payload examples** | LOVEBLE_EXAMPLES.md → Real Examples | 10 min |

---

## 🔍 Search by Topic

### Configuration
- How to update config.py: **LOVEBLE_SETUP.md**
- Where to get API key: **LOVEBLE_SETUP.md - Step 2**
- Where to get shop ID: **LOVEBLE_SETUP.md - Step 3**
- Where to get webhook secret: **LOVEBLE_SETUP.md - Step 4**
- How to map products: **LOVEBLE_SETUP.md - Step 5**

### Webhooks
- What is a webhook: **LOVEBLE_INTEGRATION.md - Section 1**
- Webhook format: **LOVEBLE_QUICK_START.md**
- Webhook signature: **LOVEBLE_INTEGRATION.md - Section 1 & LOVEBLE_EXAMPLES.md**
- How to set up webhook: **LOVEBLE_SETUP.md - Step 6**

### Bot Features
- Daily diagnostics: **LOVEBLE_ADMIN.md - Section 2**
- Weekly reports: **LOVEBLE_ADMIN.md - Section 2**
- Telegram commands: **LOVEBLE_ADMIN.md - Section 2**
- Admin notifications: **LOVEBLE_ADMIN.md - Section 1**

### Testing & Debugging
- Health check: **LOVEBLE_QUICK_START.md - Debugging**
- Webhook testing: **LOVEBLE_QUICK_START.md - Debugging**
- Manual test with curl: **LOVEBLE_INTEGRATION.md - Section 5**
- Manual test with Python: **LOVEBLE_EXAMPLES.md - Testing**
- Common errors: **LOVEBLE_QUICK_START.md - Common Issues**

### Deployment
- Local development: **LOVEBLE_INTEGRATION.md - Section 5**
- Production with Nginx: **LOVEBLE_INTEGRATION.md - Section 8**
- Production with systemd: **LOVEBLE_INTEGRATION.md - Section 8**

### Security
- Signature verification: **LOVEBLE_ADMIN.md - Section 3**
- How HMAC works: **LOVEBLE_EXAMPLES.md - Signature Example**
- Admin authentication: **LOVEBLE_ADMIN.md - Section 3**

---

## 📋 File Locations

```
coffee_system/
├── LOVEBLE_SETUP.md              ← START HERE! (5 min setup)
├── LOVEBLE_ADMIN.md              ← For coffee shop admin
├── LOVEBLE_QUICK_START.md        ← Quick reference
├── LOVEBLE_EXAMPLES.md           ← Real examples & diagrams
├── LOVEBLE_INTEGRATION.md        ← Complete detailed guide
├── LOVEBLE_INDEX.md              ← This file! Navigation guide
│
├── main.py                        ← Start bot here
├── config.py                      ← Configure bot here
├── requirements.txt               ← Python dependencies
├── coffee_bot.log                 ← Bot logs (created on run)
├── coffee.db                      ← Database (created on run)
│
├── backend/
│   ├── loveble_api.py             ← Webhook processing
│   ├── database.py                ← Sales database
│   ├── scheduler.py               ← Daily/weekly/monthly reports
│   ├── models.py                  ← Data models
│   ├── click_webhook.py           ← Click payment (alternative)
│   └── reports.py                 ← Report generation
│
└── bot/
    ├── bot.py                     ← Telegram bot core
    ├── handlers.py                ← Bot commands
    └── notifier.py                ← Notifications
```

---

## 🎓 Learning Path

### Complete Beginner (No experience)
1. Read: **LOVEBLE_ADMIN.md** (understand what bot does)
2. Read: **LOVEBLE_SETUP.md** (do the setup)
3. Test: Make a sale in Loveble POS
4. Read: **LOVEBLE_QUICK_START.md** (for troubleshooting if needed)

**Total time:** 25 minutes

---

### Basic User (Used similar bots)
1. Skim: **LOVEBLE_SETUP.md** (already know most)
2. Quick scan: **LOVEBLE_QUICK_START.md** (check syntax)
3. Do setup and test

**Total time:** 10 minutes

---

### Developer (Want full understanding)
1. Read: **LOVEBLE_INTEGRATION.md** (complete guide)
2. Study: **LOVEBLE_EXAMPLES.md** (see real examples)
3. Reference: **LOVEBLE_QUICK_START.md** (for debugging)
4. Deploy: **LOVEBLE_INTEGRATION.md - Section 8** (production)

**Total time:** 60 minutes

---

### Troubleshooting (Something is wrong)
1. Check: **LOVEBLE_QUICK_START.md - Common Issues** (quick fixes)
2. Debug: **LOVEBLE_INTEGRATION.md - Section 7** (detailed errors)
3. Test: **LOVEBLE_QUICK_START.md - Debugging Commands** (manual test)
4. Review: **LOVEBLE_ADMIN.md - Section 4** (troubleshooting guide)

**Total time:** 15-30 minutes

---

## 🆘 Getting Help

### Error Messages
**Error:** "Invalid webhook signature"
→ See: **LOVEBLE_QUICK_START.md - Common Issues**

**Error:** "Product not found"
→ See: **LOVEBLE_SETUP.md - Step 5**

**Error:** "Connection refused"
→ See: **LOVEBLE_QUICK_START.md - Common Issues**

### Understanding Concepts
**What is a webhook?**
→ See: **LOVEBLE_INTEGRATION.md - Section 1**

**What is HMAC signature?**
→ See: **LOVEBLE_EXAMPLES.md - Webhook Signature Example**

**How does bot process sales?**
→ See: **LOVEBLE_ADMIN.md - Section 1 & LOVEBLE_EXAMPLES.md - Flow Diagram**

### Features & Commands
**Available Telegram commands?**
→ See: **LOVEBLE_ADMIN.md - Section 2**

**How to view reports?**
→ See: **LOVEBLE_ADMIN.md - Section 2**

**How to track inventory?**
→ See: **LOVEBLE_ADMIN.md - Section 2**

---

## ✨ Pro Tips

1. **Keep config.py private** - Contains API keys!
2. **Monitor coffee_bot.log** - Check for errors regularly
3. **Test webhooks manually** - Use curl for debugging
4. **Verify products match** - Loveble product IDs must match config.py
5. **Check at 23:00** - Daily diagnostic automatically sent
6. **Backup database** - Run `cp coffee.db coffee.db.backup` regularly

---

## 📞 Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| LOVEBLE_SETUP.md | Initial setup | 5 min |
| LOVEBLE_ADMIN.md | Admin guide | 10 min |
| LOVEBLE_QUICK_START.md | Quick reference | 2 min |
| LOVEBLE_EXAMPLES.md | Examples & diagrams | 15 min |
| LOVEBLE_INTEGRATION.md | Complete guide | 30 min |
| LOVEBLE_INDEX.md | Navigation (this file) | 5 min |

---

## 🎯 Most Common Tasks

### Task 1: First-time setup
```
1. Read: LOVEBLE_SETUP.md
2. Get credentials from Loveble
3. Update config.py
4. Run: python main.py
5. Test: Make sale in Loveble POS
```
**Time:** 15 minutes

### Task 2: Something is broken
```
1. Check: coffee_bot.log
2. Read: LOVEBLE_QUICK_START.md - Common Issues
3. Test: curl http://localhost:8443/health
4. Fix: Update config.py if needed
5. Restart: python main.py
```
**Time:** 10 minutes

### Task 3: Deploy to production
```
1. Read: LOVEBLE_INTEGRATION.md - Section 8
2. Set up Nginx reverse proxy
3. Install systemd service
4. Update webhook URL in Loveble
5. Test: Make real sale
```
**Time:** 30 minutes

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Go to coffee_system directory
cd coffee_system

# 2. Edit config.py - add Loveble credentials
# - LOVEBLE_API_KEY
# - LOVEBLE_WEBHOOK_SECRET
# - LOVEBLE_SHOP_ID
# - Product loveble_ids

# 3. Set webhook in Loveble dashboard
# URL: http://YOUR_IP:8443/webhook/loveble
# Secret: (from config.py)

# 4. Start bot
python main.py

# 5. Test it
curl http://localhost:8443/health

# 6. Make a sale in Loveble POS
# → Should get Telegram notification in 2 seconds!
```

---

## 📚 All Documents at a Glance

| File | Type | Content | Audience |
|------|------|---------|----------|
| **LOVEBLE_SETUP.md** | Guide | Step-by-step setup | Beginners |
| **LOVEBLE_ADMIN.md** | Reference | Features & commands | Admin/Owner |
| **LOVEBLE_QUICK_START.md** | Cheatsheet | Quick lookups | Power users |
| **LOVEBLE_EXAMPLES.md** | Examples | Real payloads & diagrams | Developers |
| **LOVEBLE_INTEGRATION.md** | Manual | Complete documentation | Advanced users |
| **LOVEBLE_INDEX.md** | Navigation | This file - help finding docs | Everyone |

---

**Last Updated:** January 27, 2026
**Status:** ✅ All systems operational
**Version:** 1.0.0

**Need help? Start with:** [LOVEBLE_SETUP.md](LOVEBLE_SETUP.md)
