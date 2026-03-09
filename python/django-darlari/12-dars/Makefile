# ==========================
# CONFIG
# ==========================

PY=python
DJANGO_PORT=8001
BACKEND_DIR=.
BOT_DIR=bot

# ==========================
# HELP
# ==========================

.PHONY: help
help:
	@echo ""
	@echo "Available commands:"
	@echo " make install-backend   - Install Django dependencies"
	@echo " make install-bot       - Install Bot dependencies"
	@echo " make migrate           - Make migrations + migrate"
	@echo " make superuser         - Create superuser"
	@echo " make run-backend       - Run Django server"
	@echo " make run-bot           - Run Telegram bot"
	@echo " make up                - Show instructions to run both"
	@echo " make clean             - Remove __pycache__"
	@echo ""

# ==========================
# INSTALL
# ==========================

install-backend:
	pip install -r requirements.txt

install-bot:
	cd $(BOT_DIR) && pip install -r requirements.txt

# ==========================
# DATABASE
# ==========================

migrate:
	$(PY) manage.py makemigrations
	$(PY) manage.py migrate

superuser:
	$(PY) manage.py createsuperuser

# ==========================
# RUN
# ==========================

run-backend:
	$(PY) manage.py runserver 127.0.0.1:$(DJANGO_PORT)

run-bot:
	cd $(BOT_DIR) && $(PY) main.py

# ==========================
# UP
# ==========================

up:
	@echo ""
	@echo "Open TWO terminals:"
	@echo "Terminal 1: make run-backend"
	@echo "Terminal 2: make run-bot"
	@echo ""

# ==========================
# CLEAN
# ==========================

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
