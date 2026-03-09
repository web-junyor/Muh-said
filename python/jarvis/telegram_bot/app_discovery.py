# -*- coding: utf-8 -*-
"""Kompyuterdagi ilovalar joylashuvi — Desktop va Start Menu. 'X ilovasini och' uchun."""
import os
import sys
from typing import Dict, Optional, Tuple

# Cache: normalized_name -> (display_name, path)
_app_cache: Optional[Dict[str, Tuple[str, str]]] = None


def _norm(s: str) -> str:
    """Ilova nomini qidirish uchun normalizatsiya."""
    if not s:
        return ""
    s = s.lower().strip()
    for c in " .,-_'":
        s = s.replace(c, " ")
    return " ".join(s.split())


def _scan_folder(folder: str, extensions: Tuple[str, ...], result: Dict[str, Tuple[str, str]]) -> None:
    """Papkada .lnk va .exe fayllarni yig'adi. result ga (norm_key -> (display_name, path)) qo'shadi."""
    if not os.path.isdir(folder):
        return
    try:
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and name.lower().endswith(extensions):
                stem = os.path.splitext(name)[0]
                if not stem:
                    continue
                key = _norm(stem)
                key_no_space = key.replace(" ", "")
                if key and key not in result:
                    result[key] = (stem, path)
                if key_no_space and key_no_space not in result:
                    result[key_no_space] = (stem, path)
            elif os.path.isdir(path):
                _scan_folder(path, extensions, result)
    except (PermissionError, OSError):
        pass


def _build_cache() -> Dict[str, Tuple[str, str]]:
    """Desktop va Start Menu dan barcha ilovalar ro'yxatini yig'adi."""
    global _app_cache
    if _app_cache is not None:
        return _app_cache
    result: Dict[str, Tuple[str, str]] = {}
    if sys.platform != "win32":
        _app_cache = result
        return _app_cache

    extensions = (".lnk", ".exe")
    # Desktop
    for desktop in (
        os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Desktop"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
    ):
        _scan_folder(desktop, extensions, result)
    # Start Menu — foydalanuvchi
    start_user = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    _scan_folder(start_user, extensions, result)
    # Start Menu — tizim
    start_all = os.path.join(os.environ.get("PROGRAMDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    _scan_folder(start_all, extensions, result)

    _app_cache = result
    return _app_cache


def find_app_path(user_input: str) -> Optional[Tuple[str, str]]:
    """
    Foydalanuvchi yozgan matn bo'yicha ilova topadi.
    Qaytish: (display_name, path) yoki None
    """
    if not user_input or not user_input.strip():
        return None
    cache = _build_cache()
    n = _norm(user_input)
    n_no_space = n.replace(" ", "")
    if not n and not n_no_space:
        return None
    # Aniq moslik
    if n in cache:
        return cache[n]
    if n_no_space in cache:
        return cache[n_no_space]
    # Qismiy: user "chrome" yozsa, "Google Chrome" ni topamiz
    for key, (display_name, path) in cache.items():
        if n in key or n_no_space in key:
            return (display_name, path)
        if key in n or key in n_no_space:
            return (display_name, path)
    return None


def run_app_by_name(user_input: str) -> Tuple[bool, str]:
    """
    'X ilovasini och' — X ni qidiradi va ochadi.
    Qaytish: (success, message)
    """
    if sys.platform != "win32":
        return False, "Ilova qidirish faqat Windows da qo'llab-quvvatlanadi."
    found = find_app_path(user_input)
    if not found:
        return False, f"'{user_input}' ilovasi topilmadi. Desktop yoki Start Menu da qisqa yo'l bormi tekshiring."
    display_name, path = found
    try:
        os.startfile(path)
        return True, f"{display_name} ochildi."
    except Exception:
        return False, f"{display_name} ni ochib bo'lmadi."
