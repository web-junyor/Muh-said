# -*- coding: utf-8 -*-
"""Buyruq tarixi — SQLite. Barcha saqlanadigan narsalar bitta DB da (data/jarvis_history.db).
   Jadval strukturalari data/jarvis_schema.sql faylida; dastur shu .sql dan foydalanadi."""
import os
import sqlite3
from datetime import datetime, date
from typing import List, Optional, Tuple

_BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE, "data", "jarvis_history.db")
SCHEMA_PATH = os.path.join(_BASE, "data", "jarvis_schema.sql")


def _ensure_db():
    """data/jarvis_schema.sql faylidan jadval yaratadi, ma'lumotlar data/jarvis_history.db da saqlanadi."""
    data_dir = os.path.dirname(DB_PATH)
    os.makedirs(data_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    if os.path.isfile(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        try:
            conn.execute("ALTER TABLE command_history ADD COLUMN response_text TEXT")
        except sqlite3.OperationalError:
            pass
    else:
        # Schema fayli yo'q bo'lsa — eski usul (inline)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                command_text TEXT NOT NULL,
                result_ok INTEGER NOT NULL,
                result_msg TEXT,
                created_at TEXT NOT NULL
            )
        """)
        try:
            conn.execute("ALTER TABLE command_history ADD COLUMN response_text TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS taught_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                path_or_exe TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS taught_qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                log_type TEXT NOT NULL,
                message TEXT,
                detail TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL,
                fayl TEXT NOT NULL,
                turi TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
    conn.commit()
    conn.close()


def add_command(
    telegram_id: int,
    command_text: str,
    response_text: str,
    result_ok: bool = True,
):
    """Bitta buyruq/suhbatni tarixga qo'shadi (command_text + response_text)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cmd = (command_text or "").strip()
    resp = (response_text or "").strip()
    now = datetime.utcnow().isoformat()
    try:
        conn.execute(
            "INSERT INTO command_history (user_id, command_text, result_ok, result_msg, response_text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (telegram_id, cmd, 1 if result_ok else 0, resp, resp, now),
        )
    except sqlite3.OperationalError:
        conn.execute(
            "INSERT INTO command_history (user_id, command_text, result_ok, result_msg, created_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, cmd, 1 if result_ok else 0, resp, now),
        )
    conn.commit()
    conn.close()


def get_today_commands(user_id: Optional[int] = None) -> List[Tuple[int, int, str, bool, str, str]]:
    """Bugungi buyruqlar. Qaytish: [(id, user_id, command_text, result_ok, result_msg, created_at), ...]"""
    _ensure_db()
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    if user_id is not None:
        cur = conn.execute(
            "SELECT id, user_id, command_text, result_ok, result_msg, created_at FROM command_history WHERE date(created_at) = ? AND user_id = ? ORDER BY id DESC",
            (today, user_id),
        )
    else:
        cur = conn.execute(
            "SELECT id, user_id, command_text, result_ok, result_msg, created_at FROM command_history WHERE date(created_at) = ? ORDER BY id DESC",
            (today,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_commands(user_id: Optional[int] = None, limit: int = 500) -> List[Tuple[int, int, str, bool, str, str]]:
    """Jami buyruqlar."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    if user_id is not None:
        cur = conn.execute(
            "SELECT id, user_id, command_text, result_ok, result_msg, created_at FROM command_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
    else:
        cur = conn.execute(
            "SELECT id, user_id, command_text, result_ok, result_msg, created_at FROM command_history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_today_commands(telegram_id: int) -> int:
    """Bugungi buyruqlarni o'chiradi. O'chirilgan qatorlar soni."""
    _ensure_db()
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("DELETE FROM command_history WHERE date(created_at) = ? AND user_id = ?", (today, telegram_id))
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n


def delete_all_commands(telegram_id: int) -> int:
    """Jami buyruqlarni (shu foydalanuvchi) o'chiradi."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("DELETE FROM command_history WHERE user_id = ?", (telegram_id,))
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n


# ——— taught_apps (ilovalarni o'rgatish) ———
def get_taught_apps() -> List[Tuple[int, str, str, str]]:
    """Ro'yxat: (id, app_name, path_or_exe, created_at)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT id, app_name, path_or_exe, created_at FROM taught_apps ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_taught_app(app_name: str, path_or_exe: str) -> None:
    """Ilova qo'shadi (papka yo'li yoki .exe)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO taught_apps (app_name, path_or_exe, created_at) VALUES (?, ?, ?)",
        ((app_name or "").strip(), (path_or_exe or "").strip(), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def find_taught_app(app_name: str) -> Optional[Tuple[str, str]]:
    """Nomi bo'yicha o'rgatilgan ilova. Qaytish: (app_name, path_or_exe) yoki None. Qismiy moslik qo'llanadi."""
    if not (app_name or "").strip():
        return None
    name = (app_name or "").strip().lower()
    for row in get_taught_apps():
        _id, an, path = row[0], row[1], row[2]
        if not an or not path:
            continue
        an_l = an.strip().lower()
        stem = an_l.replace(".exe", "").replace(".lnk", "")
        if an_l == name or stem == name or name in an_l or name in stem or an_l in name:
            return (an.strip(), path.strip())
    return None


# ——— taught_qa (suhbatlashishni o'rgatish) ———
def get_taught_qa_list() -> List[Tuple[int, str, str, str]]:
    """Ro'yxat: (id, question, answer, created_at)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT id, question, answer, created_at FROM taught_qa ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_taught_qa(question: str, answer: str) -> bool:
    """Savol-javob qo'shadi. Agar shu savol (trim + case-insensitive) mavjud bo'lsa, eski javob yangisi bilan yangilanadi.
    Qaytadi: True = yangilandi, False = yangi qo'shildi."""
    _ensure_db()
    q = (question or "").strip()
    a = (answer or "").strip()
    if not q or not a:
        return False
    conn = sqlite3.connect(DB_PATH)
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        "UPDATE taught_qa SET answer = ?, created_at = ? WHERE LOWER(TRIM(question)) = LOWER(?)",
        (a, now, q),
    )
    updated = cur.rowcount > 0
    if not updated:
        conn.execute(
            "INSERT INTO taught_qa (question, answer, created_at) VALUES (?, ?, ?)",
            (q, a, now),
        )
    conn.commit()
    conn.close()
    return updated


def get_taught_answer(user_text: str) -> Optional[str]:
    """Foydalanuvchi matniga mos javob (aniq yoki qismiy). None bo'lsa javob o'rgatilmagan hisoblanadi."""
    if not (user_text or "").strip():
        return None
    text = (user_text or "").strip().lower()
    for row in get_taught_qa_list():
        q, a = row[1], row[2]
        if not q or not a:
            continue
        ql = q.strip().lower()
        if ql == text or ql in text or text in ql:
            return a.strip()
    return None


# ——— Bot log (qisqacha ishlash logi) ———
def add_bot_log(log_type: str, message: str = "", detail: str = "") -> None:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO bot_log (created_at, log_type, message, detail) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), log_type or "info", (message or "")[:500], (detail or "")[:500]),
    )
    conn.commit()
    conn.close()


def get_bot_logs(limit: int = 50) -> List[Tuple[int, str, str, str, str]]:
    """Oxirgi N ta log. Qaytish: [(id, created_at, log_type, message, detail), ...]"""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT id, created_at, log_type, message, detail FROM bot_log ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ——— custom_commands (Hamma buyruqlar: foydalanuvchi qo'shgan och/yop) ———
def _ensure_custom_commands_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomi TEXT NOT NULL,
            fayl TEXT NOT NULL,
            turi TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)


def get_all_custom_commands() -> List[Tuple[int, str, str, str, str]]:
    """Ro'yxat: (id, nomi, fayl, turi, created_at)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    _ensure_custom_commands_table(conn)
    cur = conn.execute("SELECT id, nomi, fayl, turi, created_at FROM custom_commands ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_custom_command(nomi: str, fayl: str, turi: str) -> None:
    """Buyruq qo'shadi. turi = 'open' | 'close'."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    _ensure_custom_commands_table(conn)
    conn.execute(
        "INSERT INTO custom_commands (nomi, fayl, turi, created_at) VALUES (?, ?, ?, ?)",
        ((nomi or "").strip(), (fayl or "").strip(), (turi or "open").strip().lower()[:10], datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def update_custom_command(cmd_id: int, nomi: str, fayl: str) -> bool:
    """Buyruqni yangilaydi. Muvaffaqiyat bo'lsa True."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    _ensure_custom_commands_table(conn)
    cur = conn.execute(
        "UPDATE custom_commands SET nomi = ?, fayl = ? WHERE id = ?",
        ((nomi or "").strip(), (fayl or "").strip(), cmd_id),
    )
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n > 0


def delete_custom_command(cmd_id: int) -> bool:
    """Buyruqni o'chiradi. Muvaffaqiyat bo'lsa True."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    _ensure_custom_commands_table(conn)
    cur = conn.execute("DELETE FROM custom_commands WHERE id = ?", (cmd_id,))
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n > 0


def delete_custom_command_by_nomi(nomi: str) -> bool:
    """Berilgan nomiga mos birinchi custom buyruqni o'chiradi (standartni tiklash uchun)."""
    if not (nomi or "").strip():
        return False
    key = (nomi or "").strip().lower()
    for row in get_all_custom_commands():
        if (row[1] or "").strip().lower() == key:
            return delete_custom_command(row[0])
    return False


def _normalize_cmd(s: str) -> str:
    """Buyruq matnini solishtirish uchun: trim + ichidagi ketma-ket bo'shliqlarni bittaga."""
    if not s:
        return ""
    return " ".join((s or "").strip().split()).lower()


def find_custom_command(user_text: str) -> Optional[Tuple[int, str, str, str]]:
    """Foydalanuvchi matniga mos buyruq. Avval aniq (exact) moslik, keyin eng uzun qismiy. Qaytish: (id, nomi, fayl, turi) yoki None."""
    if not (user_text or "").strip():
        return None
    text = _normalize_cmd(user_text)
    if not text:
        return None
    for row in get_all_custom_commands():
        cid, nomi, fayl, turi = row[0], row[1], row[2], row[3]
        if not nomi:
            continue
        n = _normalize_cmd(nomi)
        if n and text == n:
            return (cid, nomi.strip(), fayl.strip(), (turi or "open").strip().lower())
    best = None
    best_nomi_len = -1
    for row in get_all_custom_commands():
        cid, nomi, fayl, turi = row[0], row[1], row[2], row[3]
        if not nomi:
            continue
        n = _normalize_cmd(nomi)
        if not n:
            continue
        if text != n and n not in text and text not in n:
            continue
        if len(n) <= best_nomi_len:
            continue
        best_nomi_len = len(n)
        best = (cid, nomi.strip(), fayl.strip(), (turi or "open").strip().lower())
    return best


def get_custom_command_by_id(cmd_id: int) -> Optional[Tuple[int, str, str, str, str]]:
    """Id bo'yicha buyruq. (id, nomi, fayl, turi, created_at) yoki None."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    _ensure_custom_commands_table(conn)
    cur = conn.execute("SELECT id, nomi, fayl, turi, created_at FROM custom_commands WHERE id = ?", (cmd_id,))
    row = cur.fetchone()
    conn.close()
    return row if row else None
