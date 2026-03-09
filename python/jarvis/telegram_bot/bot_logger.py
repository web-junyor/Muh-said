# -*- coding: utf-8 -*-
"""Bot logi — faylga yozish va oxirgi qatorlarni o'qish (data/jarvis_bot.log)."""
import os
from datetime import datetime

from config import BOT_LOG_FILE, BOT_LOG_LINES


def log(log_type: str, message: str = "", detail: str = "") -> None:
    """Bitta yozuvni log fayliga qo'shadi (vaqt, tur, xabar, tafsilot)."""
    d = os.path.dirname(BOT_LOG_FILE)
    if d:
        os.makedirs(d, exist_ok=True)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now} [{log_type}] {message or ''}"
    if detail:
        line += f" | {detail[:200]}"
    line = line.strip() + "\n"
    try:
        with open(BOT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def get_recent_lines(limit: int = None) -> list:
    """Log faylidan oxirgi N qatorni qaytaradi (sukutda BOT_LOG_LINES)."""
    if limit is None:
        limit = BOT_LOG_LINES
    if not os.path.isfile(BOT_LOG_FILE):
        return []
    try:
        with open(BOT_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [s.rstrip() for s in lines[-limit:] if s.strip()]
    except Exception:
        return []
