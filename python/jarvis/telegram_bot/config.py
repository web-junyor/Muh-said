# -*- coding: utf-8 -*-
import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

# ——— Ma'lumot tashqariga chiqmasin: Sun'iy intellekt (AI) ga suhbat yuborish (true = yuboradi, false = faqat o'rgatilgan javoblar)
GROQ_ALLOWED = os.getenv("JARVIS_GROQ_ALLOWED", "true").strip().lower() in ("1", "true", "yes")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN (yoki BOT_TOKEN) .env da berilmagan")
if GROQ_ALLOWED and not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY .env da berilmagan (yoki JARVIS_GROQ_ALLOWED=false qiling)")

# ——— Kirish: faqat shu ID, parol 197o ———
ALLOWED_TELEGRAM_ID = int(os.getenv("JARVIS_ALLOWED_TELEGRAM_ID", "2109017495"))
BOT_PASSWORD = os.getenv("JARVIS_BOT_PASSWORD", "197o")

# O'rgatilgan ilovalar va Q&A (SQLite bot papkasida data/)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JARVIS_DATA_DIR = os.path.join(_BASE_DIR, "data")
TEACHED_DB_PATH = os.path.join(JARVIS_DATA_DIR, "jarvis_taught.db")

# Ilovalar va fayllar (Windows)
# "Musiqa och" / "usiqa" deganida shu fayl ochiladi
MUSIC_FILE = os.getenv(
    "JARVIS_MUSIC_FILE",
    os.path.join(os.path.expanduser("~"), "OneDrive", "Music", "MINOR   Uzmir   Major - 2012 (128).mp3"),
)
# Telegram Desktop — Desktop papkadagi telegram (lnk yoki papka)
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Desktop")
if not os.path.isdir(DESKTOP_DIR):
    DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

# YouTube ilova (yutub och / yutub yop) — .lnk yoki papka
YOUTUBE_APP_PATH = os.getenv("JARVIS_YOUTUBE_APP", "").strip() or os.path.join(DESKTOP_DIR, "YouTube")

# Cursor ochilganda ochiladigan papka (Python loyihasi — prompt shu papkada kontekstida)
CURSOR_WORKSPACE_PATH = os.getenv(
    "JARVIS_CURSOR_WORKSPACE",
    r"C:\Users\Пользователь\OneDrive\Documents\GitHub\Muh-said\python",
)

# Chrome: hisob nomi -> email (bot "MS och" / "MS yop" / "MS qidir ..." da shu profil)
CHROME_ACCOUNTS = {
    "MS": "muhammad810s6443@gmail.com",
    "SHMS": "shms810s64.43@gmail.com",
    "SOLIH": "muhammad2007solih@gmail.com",
    "SODIQ": "muhammad.shukurullayev011@gmail.com",
}
# Chrome ilova yo'li (bo'sh bo'lsa: Program Files yoki Start Menu "Google Chrome.lnk" dan topiladi)
CHROME_EXE = os.getenv("JARVIS_CHROME_EXE", "").strip() or None
# Start Menu da Chrome shortcut (C:\ProgramData\Microsoft\Windows\Start Menu\Programs)
CHROME_START_MENU = os.getenv("JARVIS_CHROME_START_MENU", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs").strip()

# AI (ChatGPT): MS brauzerida ochiladi, prompt buferga nusxalanadi
CHATGPT_URL = os.getenv("JARVIS_CHATGPT_URL", "https://chatgpt.com/").strip()
AI_CHROME_ACCOUNT = os.getenv("JARVIS_AI_CHROME_ACCOUNT", "MS").strip().upper() or "MS"

# ——— Bot log (oxirgi N qator "Bot log" bo'limida ko'rsatiladi) ———
_BOT_DIR = Path(__file__).resolve().parent
BOT_LOG_FILE = os.getenv("JARVIS_BOT_LOG_FILE", str(_BOT_DIR / "data" / "jarvis_bot.log"))
BOT_LOG_LINES = int(os.getenv("JARVIS_BOT_LOG_LINES", "50"))

# ——— Tarix, o'rgatish, log ———
_BASE_DIR = Path(__file__).resolve().parent
_DATA_DIR = _BASE_DIR / "data"
TEACH_APPS_JSON = os.getenv("JARVIS_TEACH_APPS_JSON", str(_DATA_DIR / "teach_apps.json"))
TEACH_CHAT_JSON = os.getenv("JARVIS_TEACH_CHAT_JSON", str(_DATA_DIR / "teach_chat.json"))
BOT_LOG_FILE = os.getenv("JARVIS_BOT_LOG", str(_DATA_DIR / "jarvis_bot.log"))
