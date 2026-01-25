import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("7989957596:AAFCj_WGugeVeNteRtO58f7-1INy1qtgY6I")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")
