# -*- coding: utf-8 -*-
"""Claude javobidan kod bloklarini ajratib, .zip fayl yaratadi."""
import os
import re
import tempfile
import zipfile
from pathlib import Path


# ``` python main.py ``` yoki ```html yoki ```javascript
CODE_BLOCK = re.compile(
    r"```(?:\s*(\w+)\s+([^\s\n]+)\s*\n)?(.*?)```",
    re.DOTALL | re.IGNORECASE,
)

EXT_MAP = {
    "python": ".py",
    "py": ".py",
    "html": ".html",
    "css": ".css",
    "javascript": ".js",
    "js": ".js",
    "json": ".json",
    "markdown": ".md",
    "md": ".md",
    "text": ".txt",
    "txt": ".txt",
    "sql": ".sql",
    "bash": ".sh",
    "shell": ".sh",
}


def _ext_for_lang(lang: str) -> str:
    return EXT_MAP.get((lang or "").strip().lower(), ".txt")


def build_zip_from_response(response_text: str) -> str | None:
    """
    Claude javob matnidan ``` ... ``` bloklarni ajratadi, fayllarga yozadi, zip qiladi.
    Qaytaradi: zip fayl yo'li yoki None (hech qanday blok bo'lmasa).
    """
    if not (response_text or "").strip():
        return None
    blocks = list(CODE_BLOCK.finditer(response_text))
    if not blocks:
        return None
    tmpdir = tempfile.mkdtemp(prefix="jarvis_cod_")
    try:
        for i, m in enumerate(blocks):
            lang, fname, code = m.group(1), m.group(2), (m.group(3) or "").strip()
            if not code:
                continue
            if fname and not fname.startswith("."):
                base = fname.strip()
            else:
                ext = _ext_for_lang(lang) if lang else ".txt"
                base = f"file_{i + 1}{ext}"
            if not base.endswith((".py", ".html", ".css", ".js", ".json", ".md", ".txt", ".sql", ".sh")):
                base += _ext_for_lang(lang)
            path = os.path.join(tmpdir, base)
            parent = os.path.dirname(path)
            if parent and parent != tmpdir:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
        # To'liq javobni ham qo'shamiz
        readme = os.path.join(tmpdir, "javob_toliq.txt")
        with open(readme, "w", encoding="utf-8") as f:
            f.write(response_text)
        zip_path = os.path.join(tempfile.gettempdir(), f"jarvis_cod_{os.getpid()}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tmpdir):
                for name in files:
                    full = os.path.join(root, name)
                    arc = os.path.relpath(full, tmpdir)
                    zf.write(full, arc)
        return zip_path
    finally:
        try:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass
