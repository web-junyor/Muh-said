#!/bin/bash

# Coffee Bot Server Deploy Script
# Serverga botni to'liq o'rnatishi uchun

set -e  # Xatoda to'xtash

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🍵 COFFEE BOT DEPLOY SCRIPT 🍵                    ║"
echo "╚════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   echo -e "${RED}❌ ERROR: Ushbu skript root sifatida ishlatilishi kerak${NC}"
   echo "   Qayta urinib ko'ring: sudo bash deploy.sh"
   exit 1
fi

echo -e "${YELLOW}📌 1/7: System paketlarini yangilash...${NC}"
apt update && apt upgrade -y > /dev/null 2>&1
apt install -y python3 python3-pip python3-venv git curl wget certbot > /dev/null 2>&1
echo -e "${GREEN}✅ System paketlari o'rnatildi${NC}"

echo -e "${YELLOW}📌 2/7: Papkalar yaratilmoqda...${NC}"
mkdir -p /home/coffee-bot
mkdir -p /var/log/coffee-bot
chmod 755 /var/log/coffee-bot
echo -e "${GREEN}✅ Papkalar yaratildi${NC}"

echo -e "${YELLOW}📌 3/7: Virtual environment yaratilmoqda...${NC}"
cd /home/coffee-bot/coffee_system || exit 1
python3 -m venv venv > /dev/null 2>&1
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Virtual environment tayyor${NC}"

echo -e "${YELLOW}📌 4/7: Config fayli tekshirilmoqda...${NC}"
if grep -q "YOUR_LOVEBLE_API_KEY_HERE" config.py; then
    echo -e "${RED}⚠️  WARNING: Config'da placeholder qiymatlari bor!${NC}"
    echo "   Iltimos, config.py'da Loveble credentials qo'shib qo'ying:"
    echo "   - LOVEBLE_API_KEY"
    echo "   - LOVEBLE_WEBHOOK_SECRET"
    echo "   - LOVEBLE_SHOP_ID"
    echo "   - PRODUCTS section'dagi barcha loveble_id'lar"
    echo ""
    read -p "   Davom ettirish uchun 'yes' yozing: " confirm
    if [ "$confirm" != "yes" ]; then
        echo "   Cancel qilindi."
        exit 1
    fi
fi
echo -e "${GREEN}✅ Config tekshirildi${NC}"

echo -e "${YELLOW}📌 5/7: Systemd service yaratilmoqda...${NC}"
cat > /etc/systemd/system/coffee-bot.service << 'EOF'
[Unit]
Description=Coffee Shop Bot with Loveble Integration
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/coffee-bot/coffee_system
ExecStart=/home/coffee-bot/coffee_system/venv/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/coffee-bot/coffee_bot.log
StandardError=append:/var/log/coffee-bot/coffee_bot.log
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd service yaratildi${NC}"

echo -e "${YELLOW}📌 6/7: Firewall o'rnatilmoqda...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 8443/tcp > /dev/null 2>&1
    ufw allow 22/tcp > /dev/null 2>&1
    echo -e "${GREEN}✅ Firewall: 8443 va 22 portlari ochildi${NC}"
else
    echo -e "${YELLOW}⚠️  UFW o'rnatilmagan. Manual ravishda qo'shib qo'ying${NC}"
fi

echo -e "${YELLOW}📌 7/7: Service ishga tushirilmoqda...${NC}"
systemctl enable coffee-bot > /dev/null 2>&1
systemctl start coffee-bot > /dev/null 2>&1
sleep 2

# Check service status
if systemctl is-active --quiet coffee-bot; then
    echo -e "${GREEN}✅ Service muvaffaqiyatli ishga tushdi${NC}"
else
    echo -e "${RED}❌ Service ishga tushmadi! Logs ko'ring:${NC}"
    systemctl status coffee-bot
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           ✅ DEPLOY COMPLETED SUCCESSFULLY ✅          ║"
echo "╚════════════════════════════════════════════════════════╝"

echo ""
echo -e "${GREEN}📊 System Status:${NC}"
systemctl status coffee-bot --no-pager | head -5

echo ""
echo -e "${GREEN}📝 Keyingi qadamlar:${NC}"
echo "1. Loveble Dashboard'da webhook URL'ni qo'shish:"
echo "   https://YOUR_SERVER_IP:8443/webhook/loveble"
echo ""
echo "2. Logs ko'rish:"
echo "   tail -f /var/log/coffee-bot/coffee_bot.log"
echo ""
echo "3. Service boshqarish:"
echo "   systemctl restart coffee-bot    # Qayta ishga tushirish"
echo "   systemctl stop coffee-bot       # To'xtirish"
echo "   systemctl status coffee-bot     # Status tekshirish"
echo ""
echo "4. Webhook test qilish:"
echo "   python3 test_webhook.py"
echo ""
echo -e "${YELLOW}🔐 SSL Certificate (HTTPS uchun):${NC}"
echo "   certbot certonly --standalone -d your-domain.com"
echo ""
