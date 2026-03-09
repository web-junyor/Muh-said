# -*- coding: utf-8 -*-
"""Jarvis Telegram bot — ilovalar va fayllarni ochish (Windows). Bitta bajarish, bitta javob."""
import ast
import json
import os
import sys
import subprocess
import time
import uuid
import webbrowser
import pyautogui
from typing import Tuple, Union, Optional

from config import (
    MUSIC_FILE,
    DESKTOP_DIR,
    CURSOR_WORKSPACE_PATH,
    CHROME_ACCOUNTS,
    CHROME_EXE,
    CHROME_START_MENU,
    CHATGPT_URL,
    AI_CHROME_ACCOUNT,
    YOUTUBE_APP_PATH,
)

current_chrome_hwnd = None

def _win_open_file(path: str) -> bool:
    """Windows da faylni default ilova bilan ochadi."""
    if sys.platform != "win32":
        try:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False
    if not os.path.isfile(path):
        return False
    try:
        os.startfile(path)
        return True
    except Exception:
        return False


def _win_open_url(url: str) -> bool:
    """URL ni default brauzerda ochadi."""
    try:
        if sys.platform == "win32":
            os.startfile(url)
        else:
            webbrowser.open(url)
        return True
    except Exception:
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False


def _taskkill(exe: str) -> None:
    """Windows da jarayonni yopadi (taskkill /IM exe /F /T)."""
    if sys.platform != "win32":
        return
    try:
        subprocess.run(f"taskkill /IM {exe} /F /T", shell=True, capture_output=True, timeout=5)
    except Exception:
        pass


def _taskkill_returns_success(exe: str) -> bool:
    """Windows da taskkill /IM exe bajaradi; kamida bitta jarayon yopilsa True."""
    if sys.platform != "win32":
        return False
    try:
        r = subprocess.run(
            f"taskkill /IM {exe} /F /T", shell=True, capture_output=True, timeout=5
        )
        return r.returncode == 0
    except Exception:
        return False


def _close_process_by_path(executable_path: str) -> bool:
    """Windows da berilgan exe yo'li bo'yicha jarayon(lar)ni yopadi. Kamida bitta yopilsa True.
    Yo'l env orqali uzatiladi, escape muammosi bo'lmaydi."""
    if sys.platform != "win32" or not (executable_path or "").strip():
        return False
    path = os.path.abspath((executable_path or "").strip())
    if not path:
        return False
    path_norm = os.path.normpath(path)
    env = os.environ.copy()
    env["JARVIS_CLOSE_PATH"] = path_norm
    script = (
        "$p = $env:JARVIS_CLOSE_PATH; if (-not $p) { exit 1 }; "
        "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ExecutablePath -and "
        "($_.ExecutablePath -replace '/','\\') -eq $p } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; exit 0 }; exit 1"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, timeout=10, env=env, text=True,
        )
        if result.returncode == 0:
            return True
    except Exception:
        pass
    script2 = (
        "$p = $env:JARVIS_CLOSE_PATH; "
        "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ExecutablePath -and "
        "([string]$_.ExecutablePath).ToLower() -eq $p.ToLower() } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script2],
            capture_output=True, timeout=10, env=env,
        )
    except Exception:
        pass
    return False


def _close_processes_by_folder(folder_path: str) -> bool:
    """Windows da berilgan papka yo'li bo'yicha jarayonlarni yopadi (ExecutablePath papka ichida).
    Papka mavjud bo'lmasa ham yo'l prefiksi bo'yicha urinadi."""
    if sys.platform != "win32" or not (folder_path or "").strip():
        return False
    path = os.path.abspath((folder_path or "").strip())
    path_norm = os.path.normpath(path)
    if not path_norm:
        return False
    if not path_norm.endswith("\\"):
        path_norm = path_norm + "\\"
    env = os.environ.copy()
    env["JARVIS_CLOSE_PATH"] = path_norm
    script = (
        "$dir = $env:JARVIS_CLOSE_PATH; if (-not $dir) { exit 1 }; $killed = 0; "
        "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ExecutablePath -and "
        "([string]$_.ExecutablePath).ToLower().Replace('/', '\\').StartsWith($dir.ToLower()) } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $killed++ }; "
        "if ($killed -gt 0) { exit 0 } else { exit 1 }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, timeout=12, env=env,
        )
        return r.returncode == 0
    except Exception:
        pass
    return False


def run_close_by_target(target: str) -> Tuple[bool, str]:
    """O'rgatilgan 'yop' buyruqlari uchun: jarayon nomi, exe yo'li yoki papka yo'li.
    True faqat haqiqatan kamida bitta jarayon yopilganda."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    target = (target or "").strip()
    if not target:
        return False, "Yopiladigan jarayon ko'rsatilmagan."
    t_lower = target.lower()
    is_media_file = (
        t_lower.endswith(".mp3") or t_lower.endswith(".wav")
        or t_lower.endswith(".wma") or t_lower.endswith(".mp4")
    )
    if is_media_file:
        for exe in ("wmplayer.exe", "Music.UI.exe", "Music.exe", "GrooveMusic.exe", "Video.UI.exe", "vlc.exe"):
            _taskkill(exe)
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'Music|wmplayer|Groove|VLC|WindowsMediaPlayer' } | Stop-Process -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=5,
            )
        except Exception:
            pass
        return True, "Musiqa ijrochi yopildi."

    has_path = "\\" in target or "/" in target
    path_abs = os.path.abspath(target) if has_path else None
    is_dir = path_abs and os.path.isdir(path_abs)
    is_exe_file = has_path and t_lower.endswith(".exe")

    if has_path:
        if _close_processes_by_folder(target):
            return True, ""
        if is_dir and path_abs:
            try:
                for name in os.listdir(path_abs):
                    if name.lower().endswith(".exe"):
                        if _taskkill_returns_success(name):
                            return True, ""
                        if _taskkill_returns_success(name[:-4]):
                            return True, ""
            except Exception:
                pass

    if has_path and is_exe_file:
        if _close_process_by_path(target):
            return True, ""
        proc_name = target.replace("\\", "/").split("/")[-1].strip()
        if _taskkill_returns_success(proc_name):
            return True, ""
        if _taskkill_returns_success(proc_name.replace(".exe", "")):
            return True, ""

    if has_path:
        proc_name = target.replace("\\", "/").split("/")[-1].strip()
        if not proc_name:
            proc_name = target
    else:
        proc_name = target.replace(".exe", "").strip()
    exe = proc_name if proc_name.lower().endswith(".exe") else proc_name + ".exe"
    proc_name_safe = proc_name.replace(".exe", "").replace("\\", "").replace("'", "''")
    if _taskkill_returns_success(exe):
        return True, ""
    if _taskkill_returns_success(proc_name):
        return True, ""
    first_word = (proc_name_safe.split() or [""])[0]
    if first_word and first_word != proc_name_safe:
        if _taskkill_returns_success(first_word + ".exe"):
            return True, ""
        if _taskkill_returns_success(first_word):
            return True, ""
    _taskkill(exe)
    _taskkill(proc_name)
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"$procs = Get-Process -ErrorAction SilentlyContinue | Where-Object {{ $_.ProcessName -like '*{proc_name_safe}*' }}; if ($procs) {{ $procs | Stop-Process -Force -ErrorAction SilentlyContinue; exit 0 }} else {{ exit 1 }}"],
            capture_output=True, timeout=6,
        )
        if result.returncode == 0:
            return True, ""
    except Exception:
        pass
    return False, ""


def run_music() -> Tuple[bool, str]:
    """Musiqa faylini ochadi (MUSIC_FILE). Agar yo'q bo'lsa Music papkasini ochadi."""
    if sys.platform != "win32":
        try:
            music_dir = os.path.join(os.path.expanduser("~"), "Music")
            if not os.path.isdir(music_dir):
                music_dir = os.path.expanduser("~")
            subprocess.Popen(["xdg-open", music_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Musiqa papkasi ochildi."
        except Exception:
            return False, "Musiqani ochib bo'lmadi."
    if os.path.isfile(MUSIC_FILE):
        if _win_open_file(MUSIC_FILE):
            return True, "Qo'shiq qo'yildi."
        return False, "Faylni ochib bo'lmadi."
    music_dir = os.path.join(os.path.expanduser("~"), "OneDrive", "Music")
    if not os.path.isdir(music_dir):
        music_dir = os.path.join(os.path.expanduser("~"), "Music")
    if os.path.isdir(music_dir):
        try:
            os.startfile(music_dir)
            return True, "Musiqa papkangiz ochildi. Qo'shiq tanlang."
        except Exception:
            pass
    return False, "Musiqa papkasi topilmadi."


def run_calc() -> Tuple[bool, str]:
    """Kalkulyatorni ochadi — avval ilovalar (Desktop/Start Menu) dan qidiradi."""
    if sys.platform == "win32":
        try:
            from app_discovery import find_app_path
            for name in ("calculator", "kalkulyator", "calc", "hisoblagich"):
                found = find_app_path(name)
                if found:
                    _, path = found
                    os.startfile(path)
                    return True, "Kalkulyator ochildi."
        except Exception:
            pass
        try:
            subprocess.Popen(["calc"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Kalkulyator ochildi."
        except Exception:
            try:
                os.system("start calc")
                return True, "Kalkulyator ochildi."
            except Exception:
                return False, "Kalkulyatorni ochib bo'lmadi."
    try:
        subprocess.Popen(
            ["gnome-calculator"] if os.path.exists("/usr/bin/gnome-calculator") else ["calc"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, "Kalkulyator ochildi."
    except Exception:
        return False, "Kalkulyatorni ochib bo'lmadi."


def _sendkeys_escape(s: str) -> str:
    """Windows SendKeys da maxsus belgilarni escape qiladi: + - ^ % ~ ( ) [ ] { }."""
    m = {"+": "{+}", "-": "{-}", "^": "{^}", "%": "{%}", "~": "{~}", "(": "{(}", ")": "{)}", "[": "{[}", "]": "{]}", "{": "{{}", "}": "}}"}
    return "".join(m.get(c, c) for c in s)


def safe_eval_math(expression: str) -> Tuple[bool, Optional[Union[int, float]], str]:
    """
    Faqat berilgan sonlar va + - * / ( ) dan iborat ifodani xavfsiz hisoblaydi.
    Boshqa belgilar yoki kod ishlamaydi. Qaytadi: (muvaffaqiyat, natija yoki None, xabar).
    """
    expr = (expression or "").strip().replace(",", ".")
    if not expr:
        return False, None, "Ifoda bo'sh."
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expr):
        return False, None, "Faqat sonlar va belgilar + - * / ( ) ruxsat etiladi."
    expr_clean = "".join(c for c in expr if c != " ")
    if not expr_clean:
        return False, None, "Ifoda bo'sh."
    try:
        tree = ast.parse(expr_clean, mode="eval")
    except SyntaxError as e:
        return False, None, f"Ifoda xato: {e.msg}"

    _BINOP_MAP = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b if b != 0 else 0,
        ast.Mod: lambda a, b: a % b if b != 0 else 0,
        ast.Pow: lambda a, b: a ** b,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, (int, float)):
                return v
            raise ValueError("Faqat sonlar ruxsat etiladi")
        if isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            op = type(node.op)
            if op not in _BINOP_MAP:
                raise ValueError("Ruxsat etilmagan amal")
            return _BINOP_MAP[op](left, right)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return eval_node(node.operand)
            raise ValueError("Ruxsat etilmagan amal")
        raise ValueError("Faqat arifmetik ifoda ruxsat etiladi")

    try:
        result = eval_node(tree.body)
        if isinstance(result, float) and result == int(result):
            result = int(result)
        return True, result, ""
    except ZeroDivisionError:
        return False, None, "Nolga bo'lish mumkin emas."
    except (ValueError, TypeError) as e:
        return False, None, str(e) if str(e) else "Ifoda xato."


def run_calc_with_expression(expression: str) -> Tuple[bool, str]:
    """Kalkulatorni ochadi, ifodani kiritadi, = va Enter bosadi (masalan: 7+7 -> natija)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    expr = (expression or "").strip()
    if not expr:
        return run_calc()
    try:
        subprocess.Popen(["calc"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2.2)
        sendkeys_str = _sendkeys_escape(expr) + "{=}"
        # Kalkulator oynasini oldinga olib, ifoda + = (bitta bosish, Enter yuborilmaydi)
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$sh = New-Object -ComObject WScript.Shell; "
            "$p = Get-Process -Name CalculatorApp -ErrorAction SilentlyContinue | Select-Object -First 1; "
            "if ($p -and $p.MainWindowHandle -ne 0) { $sh.AppActivate($p.Id) | Out-Null; Start-Sleep -Milliseconds 200 }; "
            "[System.Windows.Forms.SendKeys]::SendWait(" + repr(sendkeys_str) + ")"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            timeout=6,
        )
        return True, f"Kalkulator ochildi, «{expr}» kiritildi, = bosildi."
    except Exception as e:
        try:
            run_calc()
            return True, f"Kalkulator ochildi. Ifodani o'zingiz kiriting: {expr}"
        except Exception:
            return False, f"Kalkulyatorni ochib bo'lmadi: {e}"


def run_notepad() -> Tuple[bool, str]:
    """Bloknotni ochadi."""
    if sys.platform == "win32":
        try:
            subprocess.Popen(["notepad"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Bloknot ochildi."
        except Exception:
            try:
                os.system("start notepad")
                return True, "Bloknot ochildi."
            except Exception:
                return False, "Bloknotni ochib bo'lmadi."
    try:
        subprocess.Popen(["gedit", "--new-window"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Bloknot ochildi."
    except Exception:
        return False, "Bloknotni ochib bo'lmadi."


def run_file_explorer() -> Tuple[bool, str]:
    """Fayl ilovasini (Explorer / Fayl menejer) ochadi."""
    if sys.platform == "win32":
        try:
            subprocess.Popen(["explorer"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Fayl ilovasi ochildi."
        except Exception:
            try:
                os.system("start explorer")
                return True, "Fayl ilovasi ochildi."
            except Exception:
                return False, "Fayl ilovasini ochib bo'lmadi."
    try:
        subprocess.Popen(["nautilus", "--new-window"] if os.path.exists("/usr/bin/nautilus") else ["xdg-open", os.path.expanduser("~")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Fayl ilovasi ochildi."
    except Exception:
        return False, "Fayl ilovasini ochib bo'lmadi."


def run_telegram() -> Tuple[bool, str]:
    """Telegram Desktop ni ochadi."""
    for name in ("telegram", "Telegram", "Telegram.lnk", "telegram.lnk"):
        path = os.path.join(DESKTOP_DIR, name)
        if os.path.isfile(path):
            if _win_open_file(path):
                return True, "Telegram ochildi."
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith((".exe", ".lnk")) and "telegram" in f.lower():
                    full = os.path.join(path, f)
                    if _win_open_file(full):
                        return True, "Telegram ochildi."
            if sys.platform == "win32":
                try:
                    os.startfile(path)
                    return True, "Telegram ochildi."
                except Exception:
                    pass
    return False, "Desktopda Telegram topilmadi. Telegram qisqa yo'lini Desktopga qo'ying."


def _win_get_telegram_pids():
    """Telegram.exe jarayonining PID larini qaytaradi (tasklist orqali, OpenProcess kerak emas)."""
    if sys.platform != "win32":
        return []
    try:
        r = subprocess.run(
            ["tasklist", "/fi", "imagename eq Telegram.exe", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=0x0800 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        if r.returncode != 0 or not r.stdout:
            return []
        pids = []
        for line in r.stdout.strip().splitlines():
            parts = line.split(",")
            if len(parts) >= 2 and "telegram" in (parts[0] or "").lower():
                try:
                    pid_str = parts[1].strip(' "')
                    if pid_str.isdigit():
                        pids.append(int(pid_str))
                except (ValueError, IndexError):
                    pass
        return pids
    except Exception:
        return []


def _win_find_telegram_window():
    """Telegram Desktop oynasini topadi: sarlavha, process nomi (OpenProcess) yoki tasklist PID."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        found_by_title = []
        found_by_process = []
        telegram_pids = set(_win_get_telegram_pids())
        try:
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
        except Exception:
            kernel32 = psapi = None

        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

        def enum_cb(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in telegram_pids:
                r = RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(r)):
                    area = (r.right - r.left) * (r.bottom - r.top)
                    if area > 10000:
                        found_by_process.append((hwnd, area))
            buf = ctypes.create_unicode_buffer(260)
            if user32.GetWindowTextW(hwnd, buf, 260):
                t = buf.value.strip()
                if t and "telegram" in t.lower():
                    found_by_title.append(hwnd)
            if kernel32 and psapi and pid.value and pid.value not in telegram_pids:
                hproc = kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value)
                if hproc:
                    try:
                        name_buf = ctypes.create_unicode_buffer(260)
                        if psapi.GetModuleBaseNameW(hproc, None, name_buf, 260):
                            if "telegram" in name_buf.value.lower():
                                r = RECT()
                                if user32.GetWindowRect(hwnd, ctypes.byref(r)):
                                    area = (r.right - r.left) * (r.bottom - r.top)
                                    if area > 10000:
                                        found_by_process.append((hwnd, area))
                    finally:
                        kernel32.CloseHandle(hproc)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if found_by_title:
            return found_by_title[0]
        if found_by_process:
            found_by_process.sort(key=lambda x: x[1], reverse=True)
            return found_by_process[0][0]
    except Exception:
        pass
    return None


def _win_telegram_bring_foreground_with_attach():
    """Telegram oynasini topadi, AttachThreadInput + SetForegroundWindow bilan oldinga oladi (fon protsessdan ishlashi uchun).
    Qaytaradi: (True, user32, cur_tid, target_tid) — tugmalar yuborilgach detach qilish kerak; yoki (False, None, None, None)."""
    if sys.platform != "win32":
        return False, None, None, None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        hwnd = _win_find_telegram_window()
        if not hwnd:
            return False, None, None, None
        cur = user32.GetForegroundWindow()
        cur_tid = user32.GetWindowThreadProcessId(cur, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, True)
        user32.SetForegroundWindow(hwnd)
        return True, user32, cur_tid, target_tid
    except Exception:
        return False, None, None, None


def _win_telegram_force_focus_then_keybd(contact: str, message: str) -> bool:
    """Oynani topadi, restore + AttachThreadInput + Alt-hack + SetWindowPos + SetForegroundWindow + klik, keyin keybd_event."""
    if sys.platform != "win32":
        return False
    hwnd = _win_find_telegram_window()
    if not hwnd:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002
        VK_CONTROL, VK_K, VK_V, VK_RETURN, VK_MENU = 0x11, 0x4B, 0x56, 0x0D, 0x12
        HWND_TOP, SWP_SHOWWINDOW, SWP_NOSIZE, SWP_NOMOVE = 0, 0x0040, 0x0001, 0x0002
        SW_RESTORE = 9
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.15)
        cur = user32.GetForegroundWindow()
        cur_tid = user32.GetWindowThreadProcessId(cur, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, True)
        try:
            user32.keybd_event(VK_MENU, 0, 0, 0)
            user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            user32.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            time.sleep(0.25)
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.85)
            class RECT(ctypes.Structure):
                _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
            rect = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2
                try:
                    import pyautogui
                    pyautogui.FAILSAFE = False
                    pyautogui.click(cx, cy)
                except Exception:
                    pass
            time.sleep(1.0)
            if not set_clipboard(contact):
                return False
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_K, 0, 0, 0)
            user32.keybd_event(VK_K, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.9)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.6)
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(1.0)
            if not set_clipboard(message):
                return False
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            return True
        finally:
            if cur_tid != target_tid:
                try:
                    user32.AttachThreadInput(cur_tid, target_tid, False)
                except Exception:
                    pass
    except Exception:
        return False
    return False


def _win_telegram_send_via_contacts(contact: str, message: str) -> bool:
    """Kontaklar bo'limiga kiradi, ro'yxatdan kontaktni (masalan ibo) tanlaydi, chat ochiladi, prompt yoziladi, Enter."""
    if sys.platform != "win32":
        return False
    hwnd = _win_find_telegram_window()
    if not hwnd:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return False
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.15
        pyautogui.click(cx, cy)
        time.sleep(0.9)
        # Chap panel: Chats → Kontaklar (odatda 2-chi). Tab sidebar ga, Down Kontaklar ga, Enter
        pyautogui.press("tab", presses=2, interval=0.08)
        time.sleep(0.2)
        pyautogui.press("down", presses=1, interval=0.1)
        time.sleep(0.15)
        pyautogui.press("enter")
        time.sleep(1.2)
        # Kontaklar ro'yxatida kontakt nomini yozamiz (yoki yopishtiramiz), Enter — chat ochiladi
        if not set_clipboard(contact):
            return False
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.8)
        pyautogui.press("enter")
        time.sleep(1.0)
        # Chat oynasida xabar maydoniga prompt ni yozamiz, Enter
        if not set_clipboard(message):
            return False
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.25)
        pyautogui.press("enter")
        return True
    except Exception:
        return False


def _win_telegram_click_then_send(contact: str, message: str) -> bool:
    """Telegram oynasini topadi, oyna markaziga bosadi (fokus uchun), keyin Ctrl+K, Ctrl+V, Enter ketma-ketligini yuboradi."""
    if sys.platform != "win32":
        return False
    hwnd = _win_find_telegram_window()
    if not hwnd:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return False
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.12
        pyautogui.click(cx, cy)
        time.sleep(0.8)
        if not set_clipboard(contact):
            return False
        pyautogui.hotkey("ctrl", "k")
        time.sleep(1.0)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.7)
        pyautogui.press("enter")
        time.sleep(1.0)
        if not set_clipboard(message):
            return False
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        return True
    except Exception:
        return False


def _win_telegram_send_via_pywinauto(contact: str, message: str) -> bool:
    """Pywinauto orqali Telegram oynasiga to'g'ridan-to'g'ri tugmalar yuboradi (handle orqali, fokus shart emas)."""
    if sys.platform != "win32":
        return False
    hwnd = _win_find_telegram_window()
    if not hwnd:
        return False
    try:
        from pywinauto.win32_element_info import HwndElementInfo
        from pywinauto.controls.hwndwrapper import HwndWrapper
        elem = HwndElementInfo(handle=hwnd)
        w = HwndWrapper(elem)
        w.set_focus()
        time.sleep(0.8)
        if not set_clipboard(contact):
            return False
        w.send_keystrokes("^k")
        time.sleep(1.0)
        w.send_keystrokes("^v")
        time.sleep(0.7)
        w.send_keystrokes("{ENTER}")
        time.sleep(1.0)
        if not set_clipboard(message):
            return False
        w.send_keystrokes("^v")
        time.sleep(0.3)
        w.send_keystrokes("{ENTER}")
        return True
    except Exception:
        return False


def _win_telegram_send_via_pyautogui(contact: str, message: str) -> bool:
    """PyAutoGUI orqali joriy oynaga Ctrl+K, Ctrl+V, Enter ketma-ketligini yuboradi. Telegram oldinda bo'lishi kerak."""
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.15
        if not set_clipboard(contact):
            return False
        pyautogui.hotkey("ctrl", "k")
        time.sleep(0.9)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.6)
        pyautogui.press("enter")
        time.sleep(1.0)
        if not set_clipboard(message):
            return False
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.25)
        pyautogui.press("enter")
        return True
    except Exception:
        return False


def _win_telegram_send_via_keybd(contact: str, message: str) -> bool:
    """keybd_event orqali Telegram oynasiga tugmalar yuboradi (AttachThreadInput bilan)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002
        VK_CONTROL, VK_K, VK_V, VK_RETURN = 0x11, 0x4B, 0x56, 0x0D
        hwnd = _win_find_telegram_window()
        if not hwnd:
            return False
        cur = user32.GetForegroundWindow()
        cur_tid = user32.GetWindowThreadProcessId(cur, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        attached = False
        if cur_tid != target_tid:
            attached = user32.AttachThreadInput(cur_tid, target_tid, True)
        user32.SetForegroundWindow(hwnd)
        time.sleep(1.2)
        try:
            if not set_clipboard(contact):
                return False
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_K, 0, 0, 0)
            user32.keybd_event(VK_K, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.7)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.6)
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(1.0)
            if not set_clipboard(message):
                return False
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.25)
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            return True
        finally:
            if attached and cur_tid != target_tid:
                user32.AttachThreadInput(cur_tid, target_tid, False)
    except Exception:
        return False


def _win_telegram_activate_and_send(contact: str, message: str) -> bool:
    """Birinchi: majburiy fokus + keybd_event (barcha tugmalar Telegramga), keyin Kontaklar, click+Ctrl+K, pywinauto, keybd."""
    if _win_telegram_force_focus_then_keybd(contact, message):
        return True
    if _win_telegram_send_via_contacts(contact, message):
        return True
    if _win_telegram_click_then_send(contact, message):
        return True
    if _win_telegram_send_via_pywinauto(contact, message):
        return True
    ok_attach, user32, cur_tid, target_tid = _win_telegram_bring_foreground_with_attach()
    if not ok_attach:
        return False
    time.sleep(1.5)
    try:
        if _win_telegram_send_via_pyautogui(contact, message):
            return True
    finally:
        if user32 is not None and cur_tid != target_tid:
            try:
                user32.AttachThreadInput(cur_tid, target_tid, False)
            except Exception:
                pass
    return _win_telegram_send_via_keybd(contact, message)


def run_telegram_send(contact: str, message: str) -> Tuple[bool, str]:
    """Telegram Desktop ni ochadi; bunga: ... prompt: ... formatida bo'lsa — kontaktga xabar yuborib «Yuborildi» deb javob beradi."""
    if not contact or not message or not message.strip():
        return False, "Kontakt va xabar matnini kiriting. Masalan: telegram och bunga: ibo prompt: salom qalesan"
    msg = message.strip()
    ok_open = run_telegram()[0]
    if not ok_open:
        ok_clip = set_clipboard(msg)
        if ok_clip:
            return False, "Matn clipboardga nusxalandi, lekin Telegram ochilmadi. Telegram ni oching va «" + contact + "» ga Ctrl+V qiling."
        return False, "Telegram ochilmadi. Desktopda Telegram ni oching."
    delays = [4.5, 2.5, 2.5, 2.0]
    for attempt in range(4):
        time.sleep(delays[attempt])
        if _win_telegram_activate_and_send(contact, msg):
            return True, "Yuborildi."
    ok_clip = set_clipboard(msg)
    if ok_clip:
        return True, f"Telegram ochildi. «{contact}» ga o'ting, xabar maydoniga Ctrl+V qiling va Enter bosing."
    return True, f"Telegram ochildi. «{contact}» ga o'ting va matnni yozing: {msg[:80]}{'…' if len(msg) > 80 else ''}"


def _get_vscode_exe_path() -> str:
    """Code.exe yo'lini topadi: standart o'rnatish, keyin Desktop."""
    if sys.platform != "win32":
        return ""
    localappdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    candidates = [
        os.path.join(localappdata, "Programs", "Microsoft VS Code", "Code.exe"),
        os.path.join(program_files, "Microsoft VS Code", "Code.exe"),
        os.path.join(DESKTOP_DIR, "Visual Studio Code", "Code.exe"),
        os.path.join(DESKTOP_DIR, "VS Code", "Code.exe"),
    ]
    for exe in candidates:
        if exe and os.path.isfile(exe):
            return exe
    for name in ("Visual Studio Code", "VS Code"):
        folder = os.path.join(DESKTOP_DIR, name)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f == "Code.exe" or (f.lower().endswith(".exe") and "code" in f.lower()):
                    return os.path.join(folder, f)
    return ""


def run_vscode() -> Tuple[bool, str]:
    """Visual Studio Code ni Python papkasi (workspace) bilan ochadi."""
    workspace = _get_python_workspace() or (CURSOR_WORKSPACE_PATH or "").strip()
    if sys.platform != "win32":
        return False, "VS Code faqat Windows da qo'llab-quvvatlanadi."
    exe_path = _get_vscode_exe_path()
    if exe_path:
        try:
            if workspace and os.path.isdir(workspace):
                subprocess.Popen(
                    [exe_path, workspace],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=os.path.dirname(exe_path),
                )
                return True, "VS Code ochildi (Python papkasi bilan). Yangi fayl uchun: fayl_nomi cod: kod"
            subprocess.Popen(
                [exe_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(exe_path),
            )
            return True, "VS Code ochildi. \"fayl_nomi cod: kod\" yozib faylga saqlang."
        except Exception as e:
            try:
                os.startfile(exe_path)
                return True, "VS Code ochildi."
            except Exception:
                return False, f"VS Code ni ochib bo'lmadi: {e}"
    for name in ("Visual Studio Code", "Visual Studio Code.lnk", "VS Code", "VS Code.lnk"):
        path = os.path.join(DESKTOP_DIR, name)
        if os.path.isfile(path):
            try:
                os.startfile(path)
                return True, "VS Code ochildi. Python papkasini File → Open Folder dan oching."
            except Exception:
                pass
        if os.path.isdir(path):
            try:
                os.startfile(path)
                return True, "VS Code ochildi."
            except Exception:
                pass
    return False, "VS Code topilmadi. O'rnating: https://code.visualstudio.com"


def _get_python_workspace() -> str:
    """Kod saqlash uchun Python papkasi — config yoki bot papkasining ustidagi python."""
    if CURSOR_WORKSPACE_PATH and os.path.isdir(CURSOR_WORKSPACE_PATH):
        return CURSOR_WORKSPACE_PATH
    try:
        from pathlib import Path
        bot_dir = Path(__file__).resolve().parent
        python_dir = bot_dir.parent.parent
        if python_dir.is_dir():
            return str(python_dir)
    except Exception:
        pass
    return ""


def run_save_code(filename: str, code: str) -> Tuple[bool, str]:
    """Kodni Python papkasidagi faylga yozadi. Yangi fayl bo'lsa yaratadi."""
    workspace = _get_python_workspace()
    if not workspace:
        return False, "Python papkasi topilmadi. .env da JARVIS_CURSOR_WORKSPACE ni to'g'ri kiriting."
    filename = (filename or "").strip()
    code = (code or "").strip()
    if not code:
        return False, "Kod bo'sh. Masalan: main.py cod: print(\"Hello World\")"
    if not filename:
        filename = "cod_output.py"
    if not filename.endswith(".py"):
        filename = filename + ".py"
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        return False, "Faqat fayl nomi bering (masalan: main.py), yo'l emas."
    filepath = os.path.join(workspace, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return True, f"Kod «{filename}» fayliga saqlandi."
    except Exception as e:
        return False, f"Saqlab bo'lmadi: {e}"


def run_browser(url: Union[str, None] = None) -> Tuple[bool, str]:
    """Brauzerni ochadi. url berilsa shu sahifani ochadi."""
    target = url or "https://www.google.com"
    if _win_open_url(target):
        return True, "Brauzer ochildi." if not url else "Sahifa ochildi."
    return False, "Brauzerni ochib bo'lmadi."


def run_browser_search(query: str) -> Tuple[bool, str]:
    """Brauzerni ochadi va Google da qidiruvni ochadi."""
    from urllib.parse import quote_plus
    query = (query or "").strip()
    if not query:
        return run_browser("https://www.google.com")
    url = "https://www.google.com/search?q=" + quote_plus(query)
    if _win_open_url(url):
        return True, f"Brauzerda «{query[:50]}{'…' if len(query) > 50 else ''}» qidirildi."
    return False, "Brauzerni ochib bo'lmadi."


def _get_chrome_exe() -> str:
    """Chrome ilova yo'lini qaytaradi (config, Program Files yoki Start Menu 'Google Chrome.lnk')."""
    if CHROME_EXE and os.path.isfile(CHROME_EXE):
        return CHROME_EXE
    for path in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ):
        if os.path.isfile(path):
            return path
    # Start Menu dan "Google Chrome" shortcut orqali (C:\ProgramData\...\Programs\Google Chrome.lnk)
    if sys.platform == "win32" and CHROME_START_MENU:
        for name in ("Google Chrome.lnk", "Chrome.lnk"):
            lnk = os.path.join(CHROME_START_MENU, name)
            if os.path.isfile(lnk):
                try:
                    ps = f'(New-Object -ComObject WScript.Shell).CreateShortcut("{lnk.replace(chr(92), chr(92)+chr(92))}").TargetPath'
                    r = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", ps],
                        capture_output=True, text=True, timeout=5,
                    )
                    if r.returncode == 0 and r.stdout and os.path.isfile(r.stdout.strip()):
                        return r.stdout.strip()
                except Exception:
                    pass
    return "chrome.exe"


def _get_chrome_profile_dir(email: str) -> str:
    """Chrome Local State dan berilgan email ga mos profile papka nomini qaytaradi (Default, Profile 1, ...)."""
    if sys.platform != "win32":
        return "Default"
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    local_state = os.path.join(local_app_data, "Google", "Chrome", "User Data", "Local State")
    if not os.path.isfile(local_state):
        return "Default"
    try:
        import json
        with open(local_state, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        info = (data.get("profile") or {}).get("info_cache") or {}
        email_lower = (email or "").strip().lower()
        for profile_dir, prof in info.items():
            if isinstance(prof, dict) and (prof.get("user_name") or "").strip().lower() == email_lower:
                return profile_dir
    except Exception:
        pass
    return "Default"


def run_chrome_profile(account_key: str, url: Union[str, None] = None) -> Tuple[bool, str]:
    """Berilgan hisob (MS, SHMS, SOLIH, SODIQ) bilan Chrome ni ochadi. url bo'lsa shu sahifa."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    key = (account_key or "").strip().upper()
    email = CHROME_ACCOUNTS.get(key)
    if not email:
        return False, f"Bunday hisob yo'q: {account_key}. Mavjud: MS, SHMS, SOLIH, SODIQ."
    profile_dir = _get_chrome_profile_dir(email)
    chrome = _get_chrome_exe()
    target = url or "https://www.google.com"
    try:
        subprocess.Popen(
            [chrome, f"--profile-directory={profile_dir}", target],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        try:
            windows = pyautogui.getWindowsWithTitle("Google Chrome")
            if windows:
                global current_chrome_hwnd
                current_chrome_hwnd = windows[-1].hwnd
        except Exception:
            pass
        return True, f"Chrome ({key}) ochildi."
    except Exception as e:
        return False, f"Chrome ochilmadi: {e}"


def run_chrome_search(account_key: str, query: str) -> Tuple[bool, str]:
    """Berilgan hisobda Chrome ni ochib Google qidiruvini ochadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    from urllib.parse import quote_plus
    query = (query or "").strip()
    if not query:
        return run_chrome_profile(account_key, "https://www.google.com")
    url = "https://www.google.com/search?q=" + quote_plus(query)
    return run_chrome_profile(account_key, url)


def run_chrome_search_in_open(query: str) -> Tuple[bool, str]:
    """Ochiq Chrome oynasida qidiruv amalga oshiradi."""
    global current_chrome_hwnd
    if not current_chrome_hwnd:
        return False, "Chrome ochilmagan."
    try:
        win = pyautogui.Window(current_chrome_hwnd)
        win.activate()
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        pyautogui.typewrite(query, interval=0.05)
        pyautogui.press('enter')
        return True, f"Qidirildi: {query}"
    except Exception as e:
        return False, f"Qidiruvda xatolik: {e}"


def run_ai_open() -> Tuple[bool, str]:
    """ChatGPT ni MS (yoki sozlangan) Chrome hisobida ochadi."""
    return run_chrome_profile(AI_CHROME_ACCOUNT, CHATGPT_URL)


def _win_activate_ai_window_and_paste() -> bool:
    """ChatGPT oynasini topadi, oldinga oladi, chat maydoniga fokus beradi (klik + Tab), keyin Ctrl+V va Enter."""
    if sys.platform != "win32":
        return False
    VK_TAB = 0x09
    VK_V = 0x56
    VK_RETURN = 0x0D
    VK_CONTROL = 0x11
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    KEYEVENTF_KEYUP = 0x0002
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        SW_RESTORE = 9
        found = []

        def enum_cb(hwnd, _):
            buf = ctypes.create_unicode_buffer(512)
            if user32.IsWindowVisible(hwnd) and user32.GetWindowTextW(hwnd, buf, 512):
                t = buf.value.strip().lower()
                if t and ("chatgpt" in t or "openai" in t or "chat gpt" in t):
                    found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if not found:
            return False
        hwnd = found[0]
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.4)
        cur = user32.GetForegroundWindow()
        cur_tid = user32.GetWindowThreadProcessId(cur, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, True)
        user32.SetForegroundWindow(hwnd)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, False)
        time.sleep(4.0)
        # Oyna pastiga klik (chat input joyida) — ikki marta, fokus aniqroq o‘tsin
        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            cx = (rect.left + rect.right) // 2
            cy = rect.bottom - 70
            user32.SetCursorPos(cx, cy)
            time.sleep(0.08)
            for _ in range(2):
                user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.04)
                user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0)
                time.sleep(0.15)
        time.sleep(0.7)
        # Sahifada Tab — chat input (textarea) ga fokus o‘tkazish
        for _ in range(10):
            user32.keybd_event(VK_TAB, 0, 0, 0)
            user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.06)
        time.sleep(0.4)
        # Ctrl+V (keybd_event — brauzerda barqaror ishlashi uchun)
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.6)
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False


def run_ai_prompt(prompt_text: str) -> Tuple[bool, str]:
    """Promptni buferga nusxalaydi, AI (ChatGPT) ni ochadi va promptni AI oynasiga yozadi (Ctrl+V, Enter)."""
    if not prompt_text or not prompt_text.strip():
        return False, "Prompt matnini yozing. Masalan: prompt: python darslik yoz"
    if not set_clipboard(prompt_text.strip()):
        return False, "Buferga nusxalab bo'lmadi."
    ok, _ = run_chrome_profile(AI_CHROME_ACCOUNT, CHATGPT_URL)
    time.sleep(6.5)
    if _win_activate_ai_window_and_paste():
        return True, "✅ AI ochildi, prompt yozildi va yuborildi."
    if ok:
        return True, "✅ AI ochildi. Sahifada Ctrl+V bosing — prompt yoziladi."
    return True, "✅ Prompt buferga nusxalandi. ChatGPT ni oching va Ctrl+V bosing."


def run_ai_close() -> Tuple[bool, str]:
    """ChatGPT/brauzer oynasini yopadi (sarlavhada chatgpt, openai yoki chrome + chatgpt)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        found = []
        # Sarlavhada quyidagilardan biri bo'lsa — ChatGPT oynasi (Chrome/Edge format: "ChatGPT - Google Chrome")
        key_substrings = ("chatgpt", "chat gpt", "openai")

        def enum_cb(hwnd, _):
            if not u32.IsWindowVisible(hwnd):
                return True
            buf = ctypes.create_unicode_buffer(1024)
            if u32.GetWindowTextW(hwnd, buf, 1024):
                title = buf.value.strip().lower()
                if title and any(k in title for k in key_substrings):
                    found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        # Avval oldingi oyna (fokusdagi) — tez yopish
        fg = u32.GetForegroundWindow()
        if fg:
            buf_fg = ctypes.create_unicode_buffer(1024)
            if u32.GetWindowTextW(fg, buf_fg, 1024):
                t = buf_fg.value.strip().lower()
                if t and any(k in t for k in key_substrings):
                    u32.PostMessageW(fg, WM_CLOSE, 0, 0)
                    return True, "ChatGPT (brauzer) oynasi yopildi."
        u32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        closed = 0
        for hwnd in found:
            try:
                u32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                closed += 1
            except Exception:
                pass
        if closed:
            return True, "ChatGPT (brauzer) oynasi yopildi."
        # Fallback: PowerShell orqali Chrome jarayonlarida MainWindowTitle da chatgpt/openai bo'lganini yopish
        try:
            ps_script = """
            $closed = $false
            Get-Process -Name chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match 'chatgpt|openai|chat gpt' } | ForEach-Object { $closed = $closed -or $_.CloseMainWindow() }
            if ($closed) { Write-Output 'OK' }
            """
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, timeout=6,
            )
            if r.returncode == 0 and "OK" in (r.stdout or ""):
                return True, "ChatGPT (brauzer) oynasi yopildi."
        except Exception:
            pass
        return False, "ChatGPT oynasi topilmadi. Brauzerda chatgpt.com ochiq oynani yoping va qayta urinib ko'ring."
    except Exception as e:
        return False, f"ChatGPT yopilmadi: {e}"


def close_music() -> Tuple[bool, str]:
    """Musiqa / qo'shiq ijrochisini yopadi (barcha ma'lum ijrochilar)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    # 1) taskkill orqali barcha exe lar
    for exe in (
        "wmplayer.exe", "WMP.exe",
        "Music.UI.exe", "Music.exe", "GrooveMusic.exe",
        "Video.UI.exe", "Video.exe",
        "vlc.exe", "Spotify.exe", "iTunes.exe",
        "MediaPlayer.exe", "Winamp.exe", "foobar2000.exe", "AIMP.exe",
        "Films.exe", "TV.exe", "Mp3Player.exe",
    ):
        _taskkill(exe)
    # 2) PowerShell: jarayon nomi Music, Media, Player, Film, Video va h.k. bo'lganlarni yopish
    for pattern in (
        "Music|WMP|VLC|Groove|wmplayer|Video|Spotify|iTunes|MediaPlayer|Media\\.Player",
        "Film|Films|TV|Movie|Playback|Player",
    ):
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"Get-Process -ErrorAction SilentlyContinue | Where-Object {{ $_.ProcessName -match '{pattern}' }} | Stop-Process -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=6,
            )
        except Exception:
            pass
    # 3) taskkill /IM nomi.exe (qisqa)
    for name in ("wmplayer", "Music", "VLC", "Spotify", "iTunes", "Video", "MediaPlayer"):
        try:
            subprocess.run(f"taskkill /IM {name}.exe /F /T", shell=True, capture_output=True, timeout=2)
        except Exception:
            pass
    return True, "Musiqa yopildi."


def screen_off() -> Tuple[bool, str]:
    """Notebook/kompyuter ekranini o'chiradi (monitor off)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        import ctypes
        HWND_BROADCAST = 0xFFFF
        WM_SYSCOMMAND = 0x0112
        SC_MONITORPOWER = 0xF170
        MONITOR_OFF = 2
        ctypes.windll.user32.PostMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF)
        return True, "Ekran o'chirildi."
    except Exception as e:
        return False, f"Ekran o'chirilmadi: {e}"


def screen_on() -> Tuple[bool, str]:
    """Ekranni yoqadi: monitor on, mikro harakat, Enter bosish (uyg'otish / qulflovchi oynani o'tkazish)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        import ctypes
        u32 = ctypes.windll.user32
        HWND_BROADCAST = 0xFFFF
        WM_SYSCOMMAND = 0x0112
        SC_MONITORPOWER = 0xF170
        MONITOR_ON = -1
        KEYEVENTF_KEYUP = 0x0002
        # 1) Monitor yoqish
        u32.PostMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON)
        # 2) Sichqoncha mikro harakati — ekranni uyg'otadi
        MOUSEEVENTF_MOVE = 0x0001
        u32.mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, None)
        u32.mouse_event(MOUSEEVENTF_MOVE, -1, 0, 0, None)
        # 3) F24 (ba'zi tizimlarda ekran uyg'otadi)
        VK_F24 = 0x87
        u32.keybd_event(VK_F24, 0, 0, 0)
        u32.keybd_event(VK_F24, 0, KEYEVENTF_KEYUP, 0)
        # 4) Enter — qulflovchi oyna yoki dialogni o'tkazish
        VK_RETURN = 0x0D
        u32.keybd_event(VK_RETURN, 0, 0, 0)
        u32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        return True, "Ekran yoqildi."
    except Exception as e:
        return False, f"Ekran yoqilmadi: {e}"


def wifi_connect(ssid: str) -> Tuple[bool, str]:
    """Berilgan nomli Wi-Fi tarmoqiga ulanadi (netsh wlan connect)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    ssid = (ssid or "").strip()
    if not ssid:
        return False, "Wi-Fi tarmoq nomi berilmadi. Masalan: wi-fi yoq nomi: MW"
    try:
        r = subprocess.run(
            ["netsh", "wlan", "connect", f"name={ssid}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if r.returncode == 0:
            return True, f"Wi-Fi «{ssid}» ga ulandi."
        err = (r.stderr or r.stdout or "").strip() or "Noma'lum xato"
        return False, f"Wi-Fi ga ulanmadi: {err[:200]}"
    except subprocess.TimeoutExpired:
        return False, "Wi-Fi ga ulanish vaqti tugadi."
    except Exception as e:
        return False, f"Wi-Fi ga ulanmadi: {e}"


def wifi_disconnect() -> Tuple[bool, str]:
    """Wi-Fi ni uzadi (notebookdan wi-fi ni o'chiradi)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        r = subprocess.run(
            ["netsh", "wlan", "disconnect"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return True, "Wi-Fi uzildi (o'chirildi)."
    except Exception as e:
        return False, f"Wi-Fi uzilmadi: {e}"


def close_browser() -> Tuple[bool, str]:
    """Brauzerni yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    for exe in ("msedge.exe", "chrome.exe", "firefox.exe", "iexplore.exe", "browser.exe"):
        _taskkill(exe)
    return True, "Brauzer yopildi."


def close_chrome_profile(account_key: str) -> Tuple[bool, str]:
    """Berilgan hisob (MS, SHMS, SOLIH, SODIQ) uchun Chrome oynasini yopadi (qidiruv oynasi ham).
    Hozircha barcha Chrome yopiladi; hisob nomi xabar uchun ishlatiladi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    key = (account_key or "").strip().upper()
    if key not in CHROME_ACCOUNTS:
        return False, f"Bunday hisob yo'q: {account_key}. Mavjud: MS, SHMS, SOLIH, SODIQ."
    _taskkill("chrome.exe")
    global current_chrome_hwnd
    current_chrome_hwnd = None
    return True, f"Chrome ({key}) yopildi."


def close_calc() -> Tuple[bool, str]:
    """Kalkulyatorni yopadi (Windows: CalculatorApp, Calculator, calc)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    _taskkill("CalculatorApp.exe")
    _taskkill("Calculator.exe")
    _taskkill("calc.exe")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^Calculator(App)?$|^calc$' } | Stop-Process -Force -ErrorAction SilentlyContinue"],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass
    return True, "Kalkulyator yopildi."


def close_notepad() -> Tuple[bool, str]:
    """Bloknotni yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    _taskkill("notepad.exe")
    return True, "Bloknot yopildi."


def close_file_explorer() -> Tuple[bool, str]:
    """Fayl ilovasi (ochiq papka oynalari) ni yopadi. Ishlar stoli saqlanadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        # Shell.Application orqali faqat ochiq Explorer oynalari yopiladi (ish stoli qoladi)
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$s = New-Object -ComObject Shell.Application; $n = $s.Windows().Count; $s.Windows() | ForEach-Object { $_.Quit() }; exit 0"],
            capture_output=True, text=True, timeout=8,
        )
        if r.returncode == 0:
            return True, "Fayl ilovasi (ochiq papka oynalari) yopildi."
    except Exception:
        pass
    # Fallback: explorer.exe ni to'xtatish (Windows odatda qayta ishga tushiradi)
    _taskkill("explorer.exe")
    return True, "Fayl ilovasi yopildi."


def close_telegram() -> Tuple[bool, str]:
    """Telegram Desktop ni yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    for exe in ("Telegram.exe", "telegram.exe"):
        _taskkill(exe)
    return True, "Telegram yopildi."


def close_vscode() -> Tuple[bool, str]:
    """VS Code ni yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    _taskkill("Code.exe")
    return True, "VS Code yopildi."


def close_cursor() -> Tuple[bool, str]:
    """Cursor ni yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    _taskkill("Cursor.exe")
    return True, "Cursor yopildi."


def close_all() -> Tuple[bool, str]:
    """Hamma ilovalarni yopadi (musiqa, brauzer, kalkulyator, bloknot, telegram, Cursor)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    for exe in (
        "wmplayer.exe", "Music.UI.exe", "Music.exe", "GrooveMusic.exe", "Video.UI.exe", "vlc.exe",
        "CalculatorApp.exe", "calc.exe", "notepad.exe",
        "msedge.exe", "chrome.exe", "firefox.exe", "iexplore.exe",
        "Telegram.exe", "Code.exe", "Cursor.exe",
    ):
        _taskkill(exe)
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match 'Music|Chrome|Edge|Firefox|Calculator|notepad|Telegram|Code|Cursor'} | Stop-Process -Force -ErrorAction SilentlyContinue"],
            capture_output=True, timeout=8,
        )
    except Exception:
        pass
    return True, "Hamma ilovalar yopildi."


def run_youtube_app() -> Tuple[bool, str]:
    """YouTube ilovasini ochadi (config YOUTUBE_APP_PATH yoki Desktop/YouTube)."""
    # Avval sozlangan yo'l (masalan C:\...\Desktop\YouTube yoki YouTube.lnk)
    for path in (YOUTUBE_APP_PATH, YOUTUBE_APP_PATH + ".lnk"):
        if os.path.isfile(path):
            try:
                os.startfile(path)
                return True, "YouTube ochildi."
            except Exception:
                pass
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith((".exe", ".lnk")) and "youtube" in f.lower():
                    try:
                        os.startfile(os.path.join(path, f))
                        return True, "YouTube ochildi."
                    except Exception:
                        pass
            try:
                os.startfile(path)
                return True, "YouTube ochildi."
            except Exception:
                pass
    for name in ("YouTube", "YouTube.lnk", "youtube", "youtube.lnk"):
        path = os.path.join(DESKTOP_DIR, name)
        if os.path.isfile(path):
            try:
                os.startfile(path)
                return True, "YouTube ochildi."
            except Exception:
                pass
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith((".exe", ".lnk")) and "youtube" in f.lower():
                    try:
                        os.startfile(os.path.join(path, f))
                        return True, "YouTube ochildi."
                    except Exception:
                        pass
            try:
                os.startfile(path)
                return True, "YouTube ochildi."
            except Exception:
                pass
    return False, "YouTube topilmadi. .env da JARVIS_YOUTUBE_APP=... qiling (masalan: C:\\...\\Desktop\\YouTube)."


def close_youtube() -> Tuple[bool, str]:
    """YouTube oynasini yopadi (sarlavhada YouTube bo'lgan oyna)."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        found = []

        def enum_cb(hwnd, _):
            if not u32.IsWindowVisible(hwnd):
                return True
            buf = ctypes.create_unicode_buffer(1024)
            if u32.GetWindowTextW(hwnd, buf, 1024):
                title = buf.value.strip().lower()
                if title and "youtube" in title:
                    found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        fg = u32.GetForegroundWindow()
        if fg:
            buf_fg = ctypes.create_unicode_buffer(1024)
            if u32.GetWindowTextW(fg, buf_fg, 1024):
                t = buf_fg.value.strip().lower()
                if t and "youtube" in t:
                    u32.PostMessageW(fg, WM_CLOSE, 0, 0)
                    return True, "YouTube oynasi yopildi."
        u32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        for hwnd in found:
            try:
                u32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            except Exception:
                pass
        if found:
            return True, "YouTube oynasi yopildi."
        # Jarayon orqali: YouTube.exe yoki YouTube nomi
        _taskkill("YouTube.exe")
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'YouTube|youtube' } | Stop-Process -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=4,
            )
        except Exception:
            pass
        return True, "YouTube yopildi."
    except Exception as e:
        return False, f"YouTube yopilmadi: {e}"


def run_youtube_search(query: str) -> Tuple[bool, str]:
    """YouTube da qidiruv — brauzerda search natijalarini ochadi."""
    if not query or not query.strip():
        return False, "Qidiruv matnini yozing. Masalan: yutub \"qo'shiq nomi\""
    from urllib.parse import quote
    url = "https://www.youtube.com/results?search_query=" + quote(query.strip())
    if _win_open_url(url):
        return True, "YouTube da qidiruv ochildi."
    return False, "Brauzerni ochib bo'lmadi."


def run_youtube(url: str) -> Tuple[bool, str]:
    """YouTube yoki boshqa URL ni brauzerda ochadi."""
    if _win_open_url(url):
        return True, "Qo'shiq (sahifa) ochildi. Brauzerda tinglang."
    return False, "Sahifani ochib bo'lmadi."


def run_calendar() -> Tuple[bool, str]:
    """Windows Kalendar ilovasini ochadi."""
    if sys.platform != "win32":
        try:
            subprocess.Popen(["xdg-open", "https://calendar.google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Kalendar ochildi."
        except Exception:
            return False, "Kalendarni ochib bo'lmadi."
    try:
        subprocess.Popen(["cmd", "/c", "start", "outlookcal:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
        return True, "Kalendar ochildi."
    except Exception:
        try:
            os.system("start outlookcal:")
            return True, "Kalendar ochildi."
        except Exception:
            return False, "Kalendarni ochib bo'lmadi."


def _get_alarms_json_path() -> str:
    """Windows Alarms & Clock ilovasi Alarms.json yo'li."""
    if sys.platform != "win32":
        return ""
    local = os.environ.get("LOCALAPPDATA", "")
    return os.path.join(
        local,
        "Packages",
        "Microsoft.WindowsAlarms_8wekyb3d8bbwe",
        "LocalState",
        "Alarms",
        "Alarms.json",
    )


def _win_close_clock_app() -> None:
    """Clock / Alarms & Clock ilovasini yopadi (sarlavha orqali) — Alarms.json yozishdan oldin."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        found = []

        def enum_cb(hwnd, _):
            buf = ctypes.create_unicode_buffer(512)
            if u32.IsWindowVisible(hwnd) and u32.GetWindowTextW(hwnd, buf, 512):
                t = buf.value.strip().lower()
                if t and any(k in t for k in (
                    "alarm", "clock", "soat", "budilnik", "часы", "будильник", "alarms & clock", "alarms and clock"
                )):
                    found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        u32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        for hwnd in found:
            try:
                u32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            except Exception:
                pass
        if found:
            time.sleep(1.2)
    except Exception:
        pass


def close_clock() -> Tuple[bool, str]:
    """Clock / Alarms & Clock ilovasini yopadi."""
    if sys.platform != "win32":
        return False, "Faqat Windows da."
    _win_close_clock_app()
    return True, "Clock yopildi."


def _win_write_alarm_to_json(hour: int, minute: int) -> bool:
    """Alarms.json ga yangi budilnik qo'shadi (Clock ilova yopilgan bo'lishi kerak)."""
    path = _get_alarms_json_path()
    if not path:
        return False
    alarms_dir = os.path.dirname(path)
    try:
        if alarms_dir and not os.path.isdir(alarms_dir):
            os.makedirs(alarms_dir, exist_ok=True)
        new_alarm = {
            "AlarmId": str(uuid.uuid4()).upper().replace("-", ""),
            "Hour": hour,
            "Minute": minute,
            "IsEnabled": True,
            "Recurrence": 0,
            "Label": "Budilnik",
        }
        data = None
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = None
        if data is not None and isinstance(data, dict):
            alarms = data.get("Alarms", data.get("alarms", []))
            if not isinstance(alarms, list):
                alarms = [alarms] if alarms else []
        elif data is not None and isinstance(data, list):
            alarms = list(data)
        else:
            alarms = []
        alarms.append(new_alarm)
        if data is not None and isinstance(data, dict):
            out = {**data, "Alarms": alarms}
        else:
            out = {"Alarms": alarms}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _win_send_key_sequence(vk_codes: list, user32) -> None:
    """Tugma kodlari ro'yxatini ketma-ket yuboradi (har biri keydown/keyup)."""
    KEYEVENTF_KEYUP = 0x0002
    for vk in vk_codes:
        try:
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
        except Exception:
            pass


def _win_activate_clock_and_add_alarm(hour: int, minute: int) -> bool:
    """Clock oynasini topadi, Alarm bo'limiga o'tadi, Add alarm, soat (12h AM/PM), Save."""
    if sys.platform != "win32":
        return False
    VK_TAB = 0x09
    VK_ENTER = 0x0D
    VK_DOWN = 0x28
    KEYEVENTF_KEYUP = 0x0002
    VK_0 = 0x30
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        SW_RESTORE = 9
        found = []

        def enum_cb(hwnd, _):
            buf = ctypes.create_unicode_buffer(512)
            if user32.IsWindowVisible(hwnd) and user32.GetWindowTextW(hwnd, buf, 512):
                t = buf.value.strip().lower()
                if t and any(k in t for k in (
                    "alarm", "clock", "soat", "budilnik", "часы", "будильник", "alarms & clock", "alarms and clock"
                )):
                    found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if not found:
            return False
        hwnd = found[0]
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.35)
        cur = user32.GetForegroundWindow()
        cur_tid = user32.GetWindowThreadProcessId(cur, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, True)
        user32.SetForegroundWindow(hwnd)
        if cur_tid != target_tid:
            user32.AttachThreadInput(cur_tid, target_tid, False)
        time.sleep(2.0)
        # Chap panel: 1.Focus 2.Time 3.Alarm 4.Stopwatch 5.World clock.
        # Alarm (3-chi) ga: 3 marta Tab (birinchi/ikkinchi/uchinchi = Alarm), keyin Enter
        for _ in range(3):
            user32.keybd_event(VK_TAB, 0, 0, 0)
            user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.12)
        time.sleep(0.2)
        user32.keybd_event(VK_ENTER, 0, 0, 0)
        user32.keybd_event(VK_ENTER, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(1.5)
        # Alarm bo'limida + (Add alarm): Tab orqali + ga fokus, Enter — vaqt so'rovchi kichkina oyna ochiladi
        for _ in range(3):
            user32.keybd_event(VK_TAB, 0, 0, 0)
            user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        user32.keybd_event(VK_ENTER, 0, 0, 0)
        user32.keybd_event(VK_ENTER, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(2.2)
        # Botdan kelgan vaqt (HH:MM 24h) ni dialog formatiga: soat 1-12, minut, AM/PM (user formatida mas. 7:34 PM)
        hour_12 = 12 if (hour % 12) == 0 else (hour % 12)
        is_pm = hour >= 12
        # Soat maydoni: hour_12, Tab, minut (2 xona), Tab, AM/PM (PM bo'lsa Down)
        for digit in str(hour_12):
            vk = VK_0 + (ord(digit) - ord("0"))
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.08)
        user32.keybd_event(VK_TAB, 0, 0, 0)
        user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.12)
        for digit in f"{minute:02d}":
            vk = VK_0 + (ord(digit) - ord("0"))
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.08)
        time.sleep(0.15)
        user32.keybd_event(VK_TAB, 0, 0, 0)
        user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        if is_pm:
            user32.keybd_event(VK_DOWN, 0, 0, 0)
            user32.keybd_event(VK_DOWN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.08)
        time.sleep(0.4)
        # Save: Tab 4 marta, Enter
        for _ in range(4):
            user32.keybd_event(VK_TAB, 0, 0, 0)
            user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.07)
        user32.keybd_event(VK_ENTER, 0, 0, 0)
        user32.keybd_event(VK_ENTER, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False


def run_alarm_open(time_str: Optional[str] = None) -> Tuple[bool, str]:
    """Clock ilovasini ochadi. time_str (HH:MM) berilsa: ilovani yopib Alarms.json ga yozadi, keyin ilovani ochadi; UI orqali ham sinab ko'radi."""
    if sys.platform != "win32":
        try:
            subprocess.Popen(["xdg-open", "https://www.google.com/search?q=alarm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Brauzerda budilnik qidiruv ochildi."
        except Exception:
            return False, "Faqat Windows da Clock ilovasi qo'llab-quvvatlanadi."
    hour, minute = 0, 0
    if time_str:
        try:
            parts = time_str.strip().split(":")
            hour = int(parts[0]) % 24
            minute = int(parts[1]) % 60 if len(parts) > 1 else 0
        except (ValueError, IndexError):
            pass
        _win_close_clock_app()
        time.sleep(0.5)
        _win_write_alarm_to_json(hour, minute)
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "ms-clock:alarms"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except Exception:
        try:
            os.system("start ms-clock:alarms")
        except Exception:
            return False, "Clock ilovasini ochib bo'lmadi."
    if time_str:
        time.sleep(5.5)
        if _win_activate_clock_and_add_alarm(hour, minute):
            hour_12 = 12 if (hour % 12) == 0 else (hour % 12)
            am_pm = "PM" if hour >= 12 else "AM"
            return True, f"Clock ochildi. Alarm bo'limida budilnik {hour_12}:{minute:02d} {am_pm} ga qo'yildi va saqlandi."
        hour_12 = 12 if (hour % 12) == 0 else (hour % 12)
        am_pm = "PM" if hour >= 12 else "AM"
        return True, f"Clock ochildi. Alarm bo'limida {hour_12}:{minute:02d} {am_pm} — ro'yxatni tekshiring; kerak bo'lsa qo'lda kiriting."
    return True, "Clock ochildi, Alarm bo'limi."


def _get_cursor_exe_path() -> str:
    """Cursor.exe yo'lini topadi: AppData, keyin Desktop."""
    if sys.platform != "win32":
        return ""
    # Standart o'rnatilgan joylar (faqat Python papkasi bilan ochish uchun exe kerak)
    localappdata = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        os.path.join(localappdata, "Programs", "cursor", "Cursor.exe"),
        os.path.join(localappdata, "cursor", "Cursor.exe"),
        os.path.join(DESKTOP_DIR, "Cursor", "Cursor.exe"),
    ]
    for exe in candidates:
        if exe and os.path.isfile(exe):
            return exe
    # Desktop dagi Cursor papkasida boshqa exe nomi bo'lishi mumkin
    desktop_cursor = os.path.join(DESKTOP_DIR, "Cursor")
    if os.path.isdir(desktop_cursor):
        for f in os.listdir(desktop_cursor):
            if f.lower().endswith(".exe") and "cursor" in f.lower():
                return os.path.join(desktop_cursor, f)
    return ""


def run_cursor() -> Tuple[bool, str]:
    """Cursor ni faqat Python papkasi (workspace) bilan ochadi. Prompt shu papkada AI ga yoziladi."""
    workspace = (CURSOR_WORKSPACE_PATH or "").strip()
    if sys.platform != "win32":
        return False, "Cursor faqat Windows da qo'llab-quvvatlanadi."
    if not workspace or not os.path.isdir(workspace):
        return False, "Python papkasi (JARVIS_CURSOR_WORKSPACE) topilmadi. .env da to'g'ri yo'l bering."
    exe_path = _get_cursor_exe_path()
    if exe_path:
        try:
            subprocess.Popen(
                [exe_path, workspace],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(exe_path),
            )
            return True, "Ochildi."
        except Exception:
            try:
                os.startfile(exe_path)
                return True, "Ochildi."
            except Exception:
                pass
    # exe topilmasa — Desktop dagi lnk yoki papkani ochamiz (workspace bo'lmaydi)
    for name in ("Cursor", "Cursor.lnk", "cursor.lnk"):
        path = os.path.join(DESKTOP_DIR, name)
        if os.path.isfile(path):
            try:
                os.startfile(path)
                return True, "Ochildi."
            except Exception:
                pass
        if os.path.isdir(path):
            try:
                os.startfile(path)
                return True, "Ochildi."
            except Exception:
                pass
    return False, "Cursor topilmadi. Cursor ni o'rnating yoki Desktopga Cursor qisqa yo'lini qo'ying."


def set_clipboard(text: str) -> bool:
    """Matnni clipboardga nusxalaydi (Cursor AI ga yopishtirish uchun)."""
    if not text or not text.strip():
        return False
    try:
        import pyperclip  # type: ignore[import-untyped]
        pyperclip.copy(text.strip())
        return True
    except Exception:
        if sys.platform == "win32":
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                    f.write(text.strip())
                    tmp = f.name
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", f"Get-Content -Path \"{tmp}\" -Raw | Set-Clipboard"],
                    capture_output=True,
                    timeout=5,
                )
                try:
                    os.unlink(tmp)
                except Exception:
                    pass
                return True
            except Exception:
                pass
        return False


def _win_send_key(user32, vk: int, control: bool = False) -> None:
    """Bitta tugma yoki Ctrl+key yuboradi (keybd_event)."""
    KEYEVENTF_KEYUP = 0x0002
    VK_CONTROL = 0x11
    if control:
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    if control:
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def _win_send_input_key(vk: int, control: bool = False) -> bool:
    """SendInput orqali bitta tugma — boshqa protsess oynasiga ishlatish uchun yaxshiroq."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        KEYEVENTF_KEYUP = 0x0002
        INPUT_KEYBOARD = 1
        VK_CONTROL = 0x11
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
        class INPUT_UNION(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]
        class INPUT(ctypes.Structure):
            _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]
        def send_vk(vk_code, key_up=False):
            extra = ctypes.pointer(ctypes.c_ulong(0))
            inp = INPUT(INPUT_KEYBOARD, INPUT_UNION(KEYBDINPUT(vk_code, 0, KEYEVENTF_KEYUP if key_up else 0, 0, extra)))
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        if control:
            send_vk(VK_CONTROL)
        send_vk(vk)
        send_vk(vk, key_up=True)
        if control:
            send_vk(VK_CONTROL, key_up=True)
        return True
    except Exception:
        return False


def _win_activate_cursor_and_paste() -> bool:
    """Cursor oynasini oldinga oladi, Ctrl+L (AI Chat), Ctrl+V (prompt), Enter (yuborish)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002
        VK_CONTROL = 0x11
        VK_L = 0x4C
        VK_V = 0x56
        VK_RETURN = 0x0D
        found = []

        def enum_cb(hwnd, _):
            buf = ctypes.create_unicode_buffer(260)
            if user32.IsWindowVisible(hwnd) and user32.GetWindowTextW(hwnd, buf, 260):
                t = buf.value.strip()
                if t and "cursor" in t.lower() and "setup" not in t.lower():
                    found.append((hwnd, t))
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if not found:
            return False
        found.sort(key=lambda x: len(x[1]), reverse=True)
        hwnd = found[0][0]
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.7)
        if not _win_send_input_key(VK_L, control=True):
            _win_send_key(user32, VK_L, control=True)
        time.sleep(1.3)
        if not _win_send_input_key(VK_V, control=True):
            _win_send_key(user32, VK_V, control=True)
        time.sleep(0.5)
        if not _win_send_input_key(VK_RETURN, control=False):
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False


def run_cursor_prompt(prompt_text: str) -> Tuple[bool, str]:
    """Promptni Cursor AI ga yuboradi: clipboard + Cursor oynasiga Ctrl+L, Ctrl+V, Enter."""
    if not prompt_text or not prompt_text.strip():
        return False, "Prompt matnini yozing. Masalan: prompt: bu funksiyani tuzat"
    if not set_clipboard(prompt_text):
        return False, "Clipboardga nusxalab bo'lmadi."
    if sys.platform != "win32":
        return True, "✅ Prompt clipboardga nusxalandi. Cursor da Ctrl+L, keyin Ctrl+V va Enter bosing."
    if _win_activate_cursor_and_paste():
        return True, "✅ Prompt Cursor AI ga yuborildi — chatga tushgan bo‘ladi."
    return True, "✅ Prompt clipboardga nusxalandi. Cursor ochiq bo‘lsa: Ctrl+L (chat), keyin Ctrl+V va Enter bosing."
