# -*- coding: utf-8 -*-
"""O'rgatish ma'lumotlari: ilova yo'llari (JSON) va suhbat Q&A (JSON)."""
import json
import os
from typing import Dict, List, Optional, Tuple

from config import TEACH_APPS_JSON, TEACH_CHAT_JSON


def _load_json(path: str, default: dict) -> dict:
    if not os.path.isfile(path):
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default.copy()


def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ——— Ilovalar: { "normalized_name": { "display": "...", "path": "C:\\...\\app.exe" } } ———
def get_custom_apps() -> Dict[str, dict]:
    """O'rgatilgan ilova yo'llari. Key — normalizatsiya qilingan nom (qidirish uchun)."""
    return _load_json(TEACH_APPS_JSON, {})


def add_custom_app(folder_and_name: str) -> Tuple[bool, str]:
    """
    "C:\\Program Files\\MyApp, myapp.exe" — papka va ilova nomi.
    Qaytish: (success, message)
    """
    s = (folder_and_name or "").strip()
    if not s:
        return False, "Ilova joyi va nomi bo'sh bo'lmasin."
    if "," in s:
        folder, name = s.split(",", 1)
        folder = folder.strip().rstrip("\\/")
        name = name.strip()
    else:
        parts = s.split()
        if len(parts) < 2:
            return False, "Format: papka_yo'li va ilova_nomi (masalan: C:\\Program Files\\MyApp, myapp.exe)"
        name = parts[-1]
        folder = os.path.join(*parts[:-1]) if len(parts) > 1 else parts[0]
    if not name.lower().endswith(".exe"):
        name = name + ".exe"
    path = os.path.join(folder, name)
    if not os.path.isfile(path):
        return False, f"Fayl topilmadi: {path}"
    key = _norm_key(name)
    data = get_custom_apps()
    data[key] = {"display": os.path.splitext(name)[0], "path": path}
    _save_json(TEACH_APPS_JSON, data)
    return True, f"Qo'shildi: {data[key]['display']} → {path}"


def _norm_key(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    for c in " .,-_'":
        s = s.replace(c, " ")
    return " ".join(s.split())


def find_custom_app_path(user_input: str) -> Optional[str]:
    """Foydalanuvchi yozgan matn bo'yicha o'rgatilgan ilova yo'lini qaytaradi (yoki None)."""
    if not user_input or not user_input.strip():
        return None
    apps = get_custom_apps()
    n = _norm_key(user_input)
    n_no_space = n.replace(" ", "")
    if n in apps:
        return apps[n]["path"]
    if n_no_space in apps:
        return apps[n_no_space]["path"]
    for key, val in apps.items():
        if n in key or n_no_space in key or key in n or key in n_no_space:
            return val["path"]
    return None


# ——— Suhbat Q&A: [ {"question": "...", "answer": "..."}, ... ] ———
def get_qa_list() -> List[dict]:
    return _load_json(TEACH_CHAT_JSON, {}).get("items", [])


def add_qa(question: str, answer: str) -> Tuple[bool, str]:
    """Yangi savol-javob qo'shadi."""
    q = (question or "").strip()
    a = (answer or "").strip()
    if not q or not a:
        return False, "Savol va javob bo'sh bo'lmasin."
    data = _load_json(TEACH_CHAT_JSON, {"items": []})
    items = data.get("items", [])
    items.append({"question": q, "answer": a})
    data["items"] = items
    _save_json(TEACH_CHAT_JSON, data)
    return True, "Suhbat javobi saqlandi."


def find_qa_answer(user_text: str) -> Optional[str]:
    """Foydalanuvchi matniga mos javob (aniq yoki qisman). Birinchi moslik qaytariladi."""
    text = (user_text or "").strip().lower()
    if not text:
        return None
    for item in get_qa_list():
        q = (item.get("question") or "").strip().lower()
        if q and (text == q or q in text or text in q):
            return (item.get("answer") or "").strip()
    return None
