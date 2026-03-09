# -*- coding: utf-8 -*-
"""Foydalanuvchi xabaridan buyruq aniqlash — bitta so'rov, bitta javob."""
import re
from typing import Optional, Tuple

# Intent nomi -> (action_key, extracted_value)
# action_key: music, calc, notepad, telegram, browser, youtube, saved_message, chat
# extracted_value: youtube uchun URL, saved_message uchun matn, boshqalari None

# YouTube link pattern
YOUTUBE_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+(?:\S*)?",
    re.IGNORECASE,
)
# "yutub \"qidiruv\"" yoki "youtube \"qidiruv\"" — YouTube da qidirish
YOUTUBE_SEARCH_PATTERN = re.compile(
    r"(?:yutub|youtube)\s+[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)

# "telegramda saqlanganga X deb yozib ber" — X ni ajratish
SAVED_PATTERN = re.compile(
    r"telegram(?:da)?\s+saqlanganga\s+(.+?)\s+deb\s+yozib\s+ber",
    re.IGNORECASE | re.DOTALL,
)
SAVED_PATTERN_ALT = re.compile(
    r"saqlanganga\s+(.+?)\s+deb\s+yoz(?:ib)?\s*ber",
    re.IGNORECASE | re.DOTALL,
)

# Kalit so'zlar (kichik harf)
MUSIC_KEYWORDS = (
    "musiqa", "muzika", "usiqa", "qo'shiq", "qoshiq", "radio", "muzikani och",
    "musiqani och", "qo'shiq qo'y", "qoshiq qoy", "muzika qo'y", "musiqa qo'y",
)
CALC_KEYWORDS = (
    "kalkulyator", "kalkulator", "hisoblagich", "calc", "kalkulyatorni och", "kalkulatorni och", "hisoblagichni och",
)
CALENDAR_KEYWORDS = (
    "kalendar", "calendar", "kalendarni och", "kalendar ilovasini och",
)
NOTEPAD_KEYWORDS = (
    "bloknot", "notepad", "bloknotni och", "notepad och",
)
TELEGRAM_KEYWORDS = (
    "telegram och", "telegramni och", "telegramga", "telegram",
)
BROWSER_KEYWORDS = (
    "brauzer", "brauzerni och", "chrome", "internet", "internetni och", "google och",
)
CURSOR_KEYWORDS = (
    "cursor och", "cursorni och", "botga cursorni och", "cursor ilovasini och",
)
VS_CODE_KEYWORDS = (
    "vs code och", "vscode och", "visual studio code och", "vs cod och",
)

# Faylga kod yozish — "cod: kod", "fayl_nomi cod: kod", "yangi fayl X cod: ...", "X ga yoz cod: ..."
CODE_SAVE_PATTERN_ONLY = re.compile(r"^cod:\s*(.+)$", re.IGNORECASE | re.DOTALL)
CODE_SAVE_PATTERN_WITH_FILE = re.compile(r"^(.+?)\s+cod:\s*(.+)$", re.IGNORECASE | re.DOTALL)
CODE_SAVE_YANGI = re.compile(r"yangi\s+fayl\s+(.+?)\s+(?:yarat|yoz|ga\s+yoz).*?cod:\s*(.+)", re.IGNORECASE | re.DOTALL)
CODE_SAVE_GA_YOZ = re.compile(r"^(.+?)\s+ga\s+yoz\s+cod:\s*(.+)$", re.IGNORECASE | re.DOTALL)
CODE_SAVE_YOZ = re.compile(r"yoz\s+cod:\s*(.+)$", re.IGNORECASE | re.DOTALL)

# "prompt: ..." yoki "deb ..." — Cursor AI ga yuborish uchun matn (clipboard)
CURSOR_PROMPT_PREFIXES = ("prompt:", "prompt：", "deb ")

# "X ga yuborasan M" / "X ga yoz M" — kontakt va xabar (value = "contact|||message")
TELEGRAM_SEND_PATTERNS = [
    re.compile(r"^(.+?)\s+ga\s+yuborasan\s+(.+)$", re.IGNORECASE | re.DOTALL),
    re.compile(r"^(.+?)\s+ga\s+yoz\s+(.+)$", re.IGNORECASE | re.DOTALL),
    re.compile(r"^(.+?)\s+ga\s+yubor\s+(.+)$", re.IGNORECASE | re.DOTALL),
]

# "X ilovasini och" / "X ni ochib ber" — X ni ajratish
OPEN_APP_PATTERNS = [
    re.compile(r"^(.+?)\s+ilovasini\s+och\s*$", re.IGNORECASE),
    re.compile(r"^(.+?)\s+ilovani\s+och\s*$", re.IGNORECASE),
    re.compile(r"^(.+?)\s+ni\s+ochib\s+ber\s*$", re.IGNORECASE),
    re.compile(r"^(.+?)\s+ilovasini\s+ochib\s+ber\s*$", re.IGNORECASE),
]


def _normalize(t: str) -> str:
    return (t or "").strip().lower()


def get_intent(text: str) -> Tuple[str, Optional[str]]:
    """
    Xabar bo'yicha intent qaytaradi.
    Qaytish: (action_key, value)
    action_key: 'music' | 'calc' | 'notepad' | 'telegram' | 'browser' | 'youtube' | 'saved_message' | 'chat'
    value: youtube uchun URL, saved_message uchun matn, boshqalari None
    """
    raw = (text or "").strip()
    n = _normalize(raw)
    if not n:
        return "chat", None

    # 1) YouTube link bormi?
    match = YOUTUBE_PATTERN.search(raw)
    if match:
        return "youtube", match.group(0).strip()

    # 1b) "yutub \"qidiruv\"" yoki "yutub qidir X" — YouTube da qidirish
    m = YOUTUBE_SEARCH_PATTERN.search(raw)
    if m:
        query = m.group(1).strip()
        if query:
            return "youtube_search", query
    if ("yutub" in n or "youtube" in n) and ("qidir" in n or "qidiruv" in n):
        for sep in ("qidir", "qidiruv", "da qidir"):
            if sep in raw.lower():
                pos = raw.lower().find(sep) + len(sep)
                query = raw[pos:].strip()
                if query:
                    return "youtube_search", query
                break

    # 1c) "yutub och" / "youtube och" — Desktop dagi YouTube ilovasini ochish
    if ("yutub" in n or "youtube" in n) and ("och" in n or "ochib" in n):
        return "youtube_app", None

    # 2) Saqlanganga ... deb yozib ber
    for pat in (SAVED_PATTERN, SAVED_PATTERN_ALT):
        m = pat.search(raw)
        if m:
            saved_text = m.group(1).strip()
            if saved_text:
                return "saved_message", saved_text

    # 2a) "telegram och bunga: ibo prompt: salom" yoki ko'p qatorli: telegram och\nbunga: ibo\nprompt: salol qalesan?
    if "bunga" in n and "prompt" in n:
        idx_b = raw.lower().find("bunga:")
        idx_p = raw.lower().find("prompt:")
        if idx_b != -1 and idx_p > idx_b:
            contact = " ".join(raw[idx_b + 6 : idx_p].strip().split())
            message = raw[idx_p + 7 :].strip()
            if contact and message:
                return "telegram_send", contact + "|||" + message

    # 2b) "X ga yuborasan M" / "X ga yoz M" — Telegram ga kimga yuborish + matn
    for pat in TELEGRAM_SEND_PATTERNS:
        m = pat.search(raw)
        if m:
            contact = m.group(1).strip()
            msg = m.group(2).strip()
            for prefix in ("mana yuboradigan matn:", "yuboradigan matn:", "matn:"):
                if msg.lower().startswith(prefix.lower()):
                    msg = msg[len(prefix):].strip()
                    break
            if contact and msg:
                return "telegram_send", contact + "|||" + msg

    # 2c) Yopish buyruqlari — "yop" / "o'chir" avval tekshiriladi
    if "yop" in n or "o'chir" in n or "yopilsin" in n or "to'xtat" in n:
        if "hamma" in n or "barcha" in n or ("ilova" in n and ("yop" in n or "o'chir" in n)):
            return "close_all", None
        # Chrome hisob bo'yicha yopish: MS yop, SHMS yop, SOLIH yop, SODIQ yop (uzun nomlar avval — "ms" "shms" ichida bo'lmasin)
        for key in ("shms", "solih", "sodiq", "ms"):
            if key in n:
                return "chrome_close_profile", key.upper()
        if "vs code" in n or "vscode" in n or "visual studio code" in n:
            return "close_vscode", None
        if "cursor" in n:
            return "close_cursor", None
        if "musiqa" in n or "muzika" in n or "musqani" in n or "musiqani" in n:
            return "close_music", None
        if "ai" in n or "chatgpt" in n or "chat gpt" in n:
            return "ai_close", None
        if "yutub" in n or "youtube" in n:
            return "close_youtube", None
        if "brauzer" in n or "chrome" in n or "internet" in n:
            return "close_browser", None
        if "kalkulyator" in n or "kalkulator" in n or "calc" in n or "hisoblagich" in n:
            return "close_calc", None
        if "bloknot" in n or "notepad" in n:
            return "close_notepad", None
        if "clock" in n or "soat" in n or "budink" in n or "budunk" in n or "bufink" in n or "budilnik" in n:
            return "close_clock", None
        if "fayl" in n:
            return "close_file_explorer", None
        if "telegram" in n:
            return "close_telegram", None
        if "ekran" in n or "monitor" in n or "displey" in n:
            return "screen_off", None
        if "wi-fi" in n or "wifi" in n:
            return "wifi_off", None

    # 2d) Wi-Fi yoqish — "wi-fi yoq nomi: MW"
    if ("wi-fi" in n or "wifi" in n) and ("yoq" in n or "och" in n) and "nomi:" in raw.lower():
        pos = raw.lower().find("nomi:")
        ssid = raw[pos + 5 :].strip()
        if ssid:
            return "wifi_on", ssid

    # 2e) Ekran yoqish — "ekrani yoq", "ekran och"
    if ("yoq" in n or "och" in n) and ("ekran" in n or "monitor" in n or "displey" in n):
        return "screen_on", None

    # 3) Qisqa buyruqlar (ochish)
    if any(k in n for k in MUSIC_KEYWORDS):
        return "music", None
    # hisobla: 1991-1970 yoki kalkulator och hisobla: 5+5 — faqat berilgan sonlarni hisoblash
    for sep in ("hisobla:", "hisobla ", "hisoblash:", "hisoblash "):
        if sep in raw.lower():
            pos = raw.lower().find(sep) + len(sep)
            expr = raw[pos:].strip()
            if expr:
                return "calc_expression", expr
            break
    if any(k in n for k in CALC_KEYWORDS):
        return "calc", None
    if any(k in n for k in CALENDAR_KEYWORDS):
        return "calendar", None
    # Budilnik: "Budink och qo'y 4:45 PM", "qo'y 7:34 PM" — bot formatida vaqt (X:XX AM/PM), Alarm bo'limida + dan keyin shu format yoziladi
    raw_lower = raw.strip().lower()
    am_pm_match = re.search(r"(\d{1,2})\s*:\s*(\d{1,2})\s*(am|pm)", raw_lower)
    if am_pm_match and ("qo'y" in n or "qoʻy" in n or "budink" in n or "budunk" in n or "bufink" in n or "budilnik" in n):
        h12, m = int(am_pm_match.group(1)), int(am_pm_match.group(2))
        is_pm = am_pm_match.group(3) == "pm"
        if 1 <= h12 <= 12 and 0 <= m <= 59:
            h24 = 0 if (h12 == 12 and not is_pm) else (12 if (h12 == 12 and is_pm) else (h12 + 12 if is_pm else h12))
            return "alarm_open", f"{h24:02d}:{m:02d}"
    if "budink" in n or "budunk" in n or "bufink" in n or "budilnik" in n or "budilnikni" in n:
        # 5:45 PM yoki 5:45 AM format (yuqorida qoplanmagan)
        if not am_pm_match:
            am_pm_match = re.search(r"(\d{1,2})\s*:\s*(\d{1,2})\s*(am|pm)", raw_lower)
        if am_pm_match:
            h12, m = int(am_pm_match.group(1)), int(am_pm_match.group(2))
            is_pm = am_pm_match.group(3) == "pm"
            if 1 <= h12 <= 12 and 0 <= m <= 59:
                h24 = 0 if (h12 == 12 and not is_pm) else (12 if (h12 == 12 and is_pm) else (h12 + 12 if is_pm else h12))
                return "alarm_open", f"{h24:02d}:{m:02d}"
        time_match = re.search(r"qo['']?y\s*:\s*(\d{1,2})\s*:\s*(\d{1,2})", raw, re.IGNORECASE)
        if not time_match:
            time_match = re.search(r"qo['']?y\s+(\d{1,2})\s*:\s*(\d{1,2})", raw, re.IGNORECASE)
        if not time_match:
            time_match = re.search(r"(\d{1,2})\s*:\s*(\d{1,2})", raw)
        if time_match:
            h, m = int(time_match.group(1)), int(time_match.group(2))
            if 0 <= h <= 23 and 0 <= m <= 59:
                return "alarm_open", f"{h:02d}:{m:02d}"
        if "och" in n or "ochib" in n:
            return "alarm_open", None
    if any(k in n for k in NOTEPAD_KEYWORDS):
        return "notepad", None
    # Fayl ilovasi (Explorer): fayl och, fayl ilovasini och
    if "fayl" in n and ("och" in n or "ochib" in n):
        return "file_explorer", None
    # Brauzerda qidiruv — avval tekshir (keyin oddiy "brauzer och")
    if ("brauzer" in n or "chrome" in n or "google" in n) and ("qidir" in n or "qidiruv" in n):
        for sep in ("qidir", "qidiruv", "da qidir", "va qidir"):
            if sep in raw.lower():
                pos = raw.lower().find(sep) + len(sep)
                query = raw[pos:].strip()
                if query:
                    return "browser_search", query
                break
    if any(k in n for k in BROWSER_KEYWORDS):
        return "browser", None
    # AI (ChatGPT) ochish — MS brauzerida chatgpt.com
    if ("ai" in n or "chatgpt" in n or "chat gpt" in n) and ("och" in n or "ochib" in n):
        return "ai_open", None
    # Chrome hisob bilan ochish: MS och, SHMS ochib ber, SOLIH och, SODIQ och (uzun nomlar avval — "ms" "shms" ichida bo'lmasin)
    for key in ("shms", "solih", "sodiq", "ms"):
        if key in n and ("och" in n or "ochib" in n):
            return "chrome_profile", key.upper()
    # Chrome hisobda qidiruv: MS qidir X, MS da qidir X, SHMS qidir ...
    for key in ("shms", "solih", "sodiq", "ms"):
        if key in n and ("qidir" in n or "qidiruv" in n):
            # "MS qidir python darslik" -> query = "python darslik"
            for sep in ("qidir", "qidiruv", "da qidir"):
                if sep in raw.lower():
                    pos = raw.lower().find(sep) + len(sep)
                    query = raw[pos:].strip()
                    if query:
                        return "chrome_search", key.upper() + "|||" + query
                    break
    # Telegram: "telegram och" yoki "telegramni och" — lekin "telegramda saqlanganga" emas
    if "saqlanganga" not in n and any(k in n for k in TELEGRAM_KEYWORDS):
        return "telegram", None
    # Cursor och
    if any(k in n for k in CURSOR_KEYWORDS):
        return "cursor", None
    # VS Code och
    if any(k in n for k in VS_CODE_KEYWORDS):
        return "vscode", None
    # Faylga kod saqlash — "cod: ...", "fayl_nomi cod: ...", "yangi fayl X cod: ...", "X ga yoz cod: ..."
    if "cod:" in n:
        m = CODE_SAVE_PATTERN_ONLY.search(raw)
        if m:
            code = m.group(1).strip()
            if code:
                return "code_save", "|||" + code
        m = CODE_SAVE_GA_YOZ.search(raw)
        if m:
            fname, code = m.group(1).strip(), m.group(2).strip()
            if code and fname:
                return "code_save", fname + "|||" + code
        m = CODE_SAVE_YANGI.search(raw)
        if m:
            fname, code = m.group(1).strip(), m.group(2).strip()
            if code and fname:
                return "code_save", fname + "|||" + code
        if "yoz" in n:
            m = CODE_SAVE_YOZ.search(raw)
            if m:
                code = m.group(1).strip()
                if code:
                    return "code_save", "|||" + code
        m = CODE_SAVE_PATTERN_WITH_FILE.search(raw)
        if m:
            fname, code = m.group(1).strip(), m.group(2).strip()
            if code and fname.lower() not in ("cod", "cod:") and (fname.endswith(".py") or len(fname.split()) <= 3):
                return "code_save", fname + "|||" + code
    # prompt: ... yoki prompt ... — faqat AI (ChatGPT) uchun: buferga nusxala + ChatGPT och (Cursor ga yozilmaydi)
    raw_strip = raw.strip()
    if raw_strip.lower().startswith("prompt:") and len(raw_strip) > 7:
        prompt_text = raw_strip[7:].strip()
        if prompt_text:
            return "ai_prompt", prompt_text
    if raw_strip.lower().startswith("prompt ") and len(raw_strip) > 6:
        prompt_text = raw_strip[6:].strip()
        if prompt_text:
            return "ai_prompt", prompt_text

    # 4) "X ilovasini och" / "X ni ochib ber" — kompyuterdagi istalgan ilova
    for pat in OPEN_APP_PATTERNS:
        m = pat.search(raw)
        if m:
            app_name = m.group(1).strip()
            if app_name:
                return "open_app", app_name

    return "chat", None
