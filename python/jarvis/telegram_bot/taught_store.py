# -*- coding: utf-8 -*-
"""O'rgatilgan ilovalar va suhbat Q&A — SQLite."""
import os
import sqlite3
from typing import List, Optional, Tuple

from config import TEACHED_DB_PATH, JARVIS_DATA_DIR


def _ensure_db():
    os.makedirs(JARVIS_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(TEACHED_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS taught_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_name TEXT NOT NULL UNIQUE,
            folder_path TEXT NOT NULL,
            app_name TEXT NOT NULL,
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
    conn.commit()
    conn.close()


def add_taught_app(trigger_name: str, folder_path: str, app_name: str) -> Tuple[bool, str]:
    """Ilova o'rgatish: trigger_name (foydalanuvchi yozadi), folder_path, app_name."""
    if not trigger_name or not trigger_name.strip():
        return False, "Ilova nomini kiriting."
    trigger_name = trigger_name.strip()
    folder_path = (folder_path or "").strip()
    app_name = (app_name or "").strip()
    if not folder_path or not app_name:
        return False, "Papka va ilova nomini kiriting."
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    try:
        from datetime import datetime
        conn.execute(
            "INSERT OR REPLACE INTO taught_apps (trigger_name, folder_path, app_name, created_at) VALUES (?, ?, ?, ?)",
            (trigger_name.lower(), folder_path, app_name, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return True, f"«{trigger_name}» ilovasi saqlandi."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_taught_app_path(trigger_name: str) -> Optional[Tuple[str, str]]:
    """trigger_name bo'yicha (folder_path, app_name) yoki None."""
    if not trigger_name or not trigger_name.strip():
        return None
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    cur = conn.execute(
        "SELECT folder_path, app_name FROM taught_apps WHERE LOWER(trigger_name) = ?",
        (trigger_name.strip().lower(),),
    )
    row = cur.fetchone()
    conn.close()
    return (row[0], row[1]) if row else None


def add_taught_qa(question: str, answer: str) -> Tuple[bool, str]:
    """Suhbat Q&A saqlash."""
    question = (question or "").strip()
    answer = (answer or "").strip()
    if not question or not answer:
        return False, "Savol va javobni kiriting."
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    try:
        from datetime import datetime
        conn.execute(
            "INSERT INTO taught_qa (question, answer, created_at) VALUES (?, ?, ?)",
            (question, answer, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return True, "Javob saqlandi."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_taught_answer(question: str) -> Optional[str]:
    """Savolga o'rgatilgan javob bormi — aniq yoki qisman moslik (boshida)."""
    if not question or not question.strip():
        return None
    q = question.strip().lower()
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    cur = conn.execute("SELECT question, answer FROM taught_qa ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    for stored_q, stored_a in rows:
        if stored_q and stored_a:
            if stored_q.strip().lower() == q:
                return stored_a.strip()
            if q.startswith(stored_q.strip().lower()) or stored_q.strip().lower() in q:
                return stored_a.strip()
    return None


def list_taught_apps() -> List[Tuple[str, str, str]]:
    """(trigger_name, folder_path, app_name) ro'yxati."""
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    cur = conn.execute("SELECT trigger_name, folder_path, app_name FROM taught_apps ORDER BY trigger_name")
    rows = cur.fetchall()
    conn.close()
    return list(rows)


def list_taught_qa() -> List[Tuple[str, str]]:
    """(question, answer) ro'yxati."""
    _ensure_db()
    conn = sqlite3.connect(TEACHED_DB_PATH)
    cur = conn.execute("SELECT question, answer FROM taught_qa ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return list(rows)
