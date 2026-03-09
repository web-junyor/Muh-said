import os
import sys
import time
import random
import datetime
import subprocess
import webbrowser

# Mikrofon uchun PyAudio kerak — boshida tekshirish
try:
    import pyaudio  # noqa: F401
except ImportError:
    print("\n[xato] PyAudio o'rnatilmagan. Mikrofon ishlashi uchun quyidagini bajaring:")
    print("        pip install pyaudio")
    print("      Agar xato bersa: pip install pipwin   keyin   pipwin install pyaudio\n")
    sys.exit(1)

import speech_recognition as sr
from fuzzywuzzy import fuzz
import pyttsx3

# Kamida shunchalik o'xshashlik bo'lsagina buyruq qabul qilinadi
MIN_CMD_MATCH = 50

# Sizning muzika faylingiz — "musiqa och" deganingizda shu qo'shiq ochiladi
MUSIC_FILE = os.path.join(os.path.expanduser("~"), "OneDrive", "Music", "MINOR   Uzmir   Major - 2012 (128).mp3")
# Telegram — Desktop ichidagi telegram (qisqa yo'l yoki papka)
TELEGRAM_PATH = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Desktop", "telegram")

# Chrome profillar: ovozda aytiladigan ism -> Chrome profil papkasi (Default, Profile 2, Profile 3 ...)
# Chrome da chrome://version ochib "Profil yo'li" ni ko'ring va oxiridagi papka nomini shu yerga yozing
CHROME_PROFILES = {
    "m": "Default",        # M yoki M MS akkaunt
    "shms": "Profile 2",   # SHMS akkaunt
    "abdurahmon": "Profile 3",  # Abdurahmon akkaunt
}

# Ovoz (TTS) faqat asosiy threadda ishlashi uchun — callback dan matn shu yerga yoziladi
speak_queue = []
speak_engine = None  # main() da pyttsx3.init() bilan to'ldiriladi

opts = {
    "alias": ('jarvis', 'jar', 'jorvis', 'jarviz', 'yorvik', 'yarvis'),
    "tbr": ('aytginchi', 'ko`rsatchi', 'korsat', 'necha', 'aytchi'),
    "cmds": {
        "ctime": ('xozirgi vaqt', 'soat necha', 'xozirgi soat'),
        "radio": ('muzikani qo`y', 'radioni yoq', 'radiyoni qo`sh', 'musiqani och', 'muzika ilovasini och', 'muzikani och'),
        "close_music": ('musiqani yop', 'muzikani yop', 'musiqani o\'chir', 'muzikani o\'chir', 'musiqani to\'xtat', 'musiqani to\'xtat'),
        "close_browser": ('brauzerni yop', 'brauzerni o\'chir', 'internetni yop'),
        "close_calc": ('kalkulyatorni yop', 'kalkulyatorni o\'chir'),
        "close_notepad": ('bloknotni yop', 'bloknotni o\'chir'),
        "close_telegram": ('telegramni yop', 'telegramni o\'chir', 'telegram yop', 'telegram o\'chir'),
        "open_browser": ('brauzerni och', 'brauzerni ochib ber', 'brauzer', 'internetni och', 'chrome och', 'chrome ni och', 'chromeni och'),
        "open_browser_google": ('google akkaunt och', 'google account och', 'brauzer och google', 'chrome och google', 'google och'),
        "open_browser_microsoft": ('microsoft akkaunt och', 'microsoft account och', 'brauzer och microsoft', 'chrome och microsoft', 'microsoft och'),
        "open_chrome_m": ('m och', 'm akkaunt och', 'm ms och', 'm ms', 'microsoft akkaunt chrome', 'm chrome'),
        "open_chrome_shms": ('shms och', 'shms akkaunt och', 'shms chrome', 'shms brauzer'),
        "open_chrome_abdurahmon": ('abdurahmon och', 'abdurahmon akkaunt och', 'abdurahmon chrome', 'abdurahmon brauzer'),
        "open_calc": ('kalkulyatorni och', 'kalkulyatorni ochib ber', 'kalkulyator', 'hisoblagich'),
        "open_notepad": ('bloknotni och', 'bloknotni ochib ber', 'bloknot', 'notepad'),
        "open_telegram": ('telegram ochib ber', 'telegramni och', 'telegram och', 'telegram', 'telegramga xabar yoz', 'telegram xabar yubor'),
        "open_vscode": ('vs code och', 'vscode och', 'visual studio code och', 'kodni och'),
        "close_all_apps": ('hamma ilovalarni o\'chir', 'hamma ilovani yop', 'ilovani yop', 'ilovani o\'chir', 'ilovalarni yop', 'barcha ilovalarni yop', 'ilovalarni o\'chir', 'hamma ilovani yopilsin', 'yop hamma', 'hammani yop', 'yop'),
        "open_all_apps": ('hamma ilovalarni och', 'hamma ilovani och', 'barcha ilovalarni och', 'ilovalarni och', 'hamma ilovalarimni ochsin', 'bir narsani och', 'narsani och', 'ilovani och', 'bitanarsani och'),
        "stupid1": ('latifa aytib ber', 'meni kuldir', 'Latifa aytishni bilasanmi')
    }
}


def speak(what):
    """Matnni ekranga yozadi va ovozda aytadi (TTS)."""
    print(what)
    if speak_engine is None:
        return
    # Uzun matnni jumlalarga bo'lib ovozda aniq aytish uchun
    for part in str(what).replace("!", ".").replace("?", ".").split("."):
        part = part.strip()
        if part:
            speak_engine.say(part)
            speak_engine.runAndWait()
    speak_engine.stop()


def callback(recognizer, audio):
    try:
        voice = recognizer.recognize_google(audio, language="uz").lower()
        print("[log] Aytildi: " + voice)

        # Avval "Jarvis" bor bo'lsa olib tashlaymiz, keyin buyruqni tanlaymiz
        cmd = voice
        for x in opts['alias']:
            cmd = cmd.replace(x, "").strip()
        for x in opts['tbr']:
            cmd = cmd.replace(x, "").strip()
        # "Jarvis" demasdan ham buyruq berish mumkin — to'g'ridan-to'g'ri tanlaymiz
        if not cmd:
            cmd = voice
        rc = recognize_cmd(cmd)
        if rc['cmd']:
            execute_cmd(rc['cmd'])

    except sr.UnknownValueError:
        print("[log] Tushunarsiz gap!")
    except sr.RequestError:
        print("[log] Internetni tekshiring!")


def recognize_cmd(cmd):
    """Yop/Och ni ajratish. Musiqa faqat 'muzika'/'musiqa'/'radio' aytilganda qo'yiladi."""
    yop_keywords = ('yop', "o'chir", 'yopilsin', 'yopish', 'to\'xtat')
    och_keywords = ('och', 'ochib', 'oching', 'qo\'y', 'yoq')
    music_keywords = ('muzika', 'musiqa', 'radio', 'radioni', 'radiyoni')
    cmd_lower = cmd.lower()
    is_yop = any(k in cmd_lower for k in yop_keywords)
    is_och = any(k in cmd_lower for k in och_keywords)
    has_music_word = any(k in cmd_lower for k in music_keywords)

    RC = {'cmd': '', 'percent': 0}
    for c, v in opts['cmds'].items():
        if is_yop and c.startswith('open'):
            continue
        if is_och and c.startswith('close'):
            continue
        # Musiqa faqat "muzika"/"musiqa"/"radio" aytilganda — boshqa so'zlar musiqa qo'ymasin
        if c == 'radio' and not has_music_word:
            continue
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > RC['percent']:
                RC['cmd'] = c
                RC['percent'] = vrt
    if RC['percent'] < MIN_CMD_MATCH:
        RC['cmd'] = ''
    return RC


def _taskkill(exe):
    """Windows da ilovani yopadi (shell orqali, /T = bolalari ham)."""
    if sys.platform != "win32":
        return
    try:
        subprocess.run(f'taskkill /IM {exe} /F /T', shell=True, capture_output=True, timeout=5)
    except Exception:
        pass


def _get_chrome_path():
    """Chrome.exe yo'lini qaytaradi, topilmasa None."""
    if sys.platform != "win32":
        return None
    for base in (os.environ.get('ProgramFiles', 'C:\\Program Files'), os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')):
        p = os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe')
        if os.path.isfile(p):
            return p
    return None


def _chrome_open_url(url, success_msg):
    """Chrome da berilgan URL ni ochadi (faqat shu sahifa)."""
    if sys.platform == "win32":
        p = _get_chrome_path()
        if p:
            subprocess.Popen([p, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            speak_queue.append(success_msg)
            return
        os.system(f'start chrome "{url}"')
    else:
        os.system(f'google-chrome "{url}" 2>/dev/null || xdg-open "{url}"')
    speak_queue.append(success_msg)


def _chrome_open_profile(profile_dir, success_msg):
    """Chrome ni ma'lum profil bilan ochadi (shu akkauntdagi Chrome)."""
    if sys.platform != "win32":
        os.system('google-chrome 2>/dev/null || xdg-open https://accounts.google.com')
        speak_queue.append(success_msg)
        return
    p = _get_chrome_path()
    if p:
        subprocess.Popen([p, f'--profile-directory={profile_dir}', 'https://accounts.google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        os.system(f'start chrome --profile-directory={profile_dir}')
    speak_queue.append(success_msg)


def execute_cmd(cmd):
    """Buyruqni bajaradi. Ovoz chiqarish kerak bo'lsa speak_queue ga qo'shadi (asosiy threadda so'zlashadi)."""
    if cmd == 'ctime':
        now = datetime.datetime.now()
        speak_queue.append("Hozirgi vaqt " + str(now.hour) + " soat " + str(now.minute) + " daqiqa.")

    elif cmd == 'radio':
        # MUSIC_FILE bor bo'lsa uni qo'yadi; yo'q bo'lsa Music papkadagi fayllarni sanab, kerak bo'lsa so'raydi
        music_ext = ('.mp3', '.m4a', '.wav', '.flac', '.ogg', '.aac')
        music_folder = os.path.join(os.path.expanduser("~"), "OneDrive", "Music")
        if not os.path.isdir(music_folder):
            music_folder = os.path.join(os.path.expanduser("~"), "Music")
        if not os.path.isdir(music_folder):
            music_folder = os.path.join(os.path.expanduser("~"), "Documents")

        if sys.platform == "win32":
            if os.path.isfile(MUSIC_FILE):
                os.startfile(MUSIC_FILE)
                speak_queue.append("Muzika qo'yildi.")
            else:
                try:
                    files = [f for f in os.listdir(music_folder) if f.lower().endswith(music_ext)]
                except Exception:
                    files = []
                if len(files) == 0:
                    os.startfile(music_folder)
                    speak_queue.append("Muzika papkangiz ochildi. Qo'shiq qo'shing.")
                elif len(files) == 1:
                    os.startfile(os.path.join(music_folder, files[0]))
                    speak_queue.append("Muzika qo'yildi.")
                else:
                    os.startfile(music_folder)
                    speak_queue.append(f"Papkada {len(files)} ta qo'shiq bor. Qaysi birini qo'yay? Papkani ochdim, o'zingiz tanlang.")
        else:
            if os.path.isfile(MUSIC_FILE):
                subprocess.Popen(['xdg-open', MUSIC_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                speak_queue.append("Muzika qo'yildi.")
            else:
                try:
                    files = [f for f in os.listdir(music_folder) if f.lower().endswith(music_ext)]
                except Exception:
                    files = []
                if len(files) == 1:
                    subprocess.Popen(['xdg-open', os.path.join(music_folder, files[0])], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    speak_queue.append("Muzika qo'yildi.")
                else:
                    os.system(f'xdg-open "{music_folder}" 2>/dev/null || open "{music_folder}" 2>/dev/null')
                    speak_queue.append(f"Papkada {len(files)} ta qo'shiq bor. Papkani ochdim, tanlang." if files else "Muzika papkangiz ochildi.")

    elif cmd == 'close_music':
        if sys.platform == "win32":
            # Avval PowerShell orqali barcha muzika jarayonlarini yopish (nomida Music, WMP, VLC, Groove, Video bor)
            try:
                subprocess.run(
                    ['powershell', '-NoProfile', '-Command',
                     "Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'Music|WMP|VLC|Groove|wmplayer|Video|Spotify|iTunes' } | Stop-Process -Force -ErrorAction SilentlyContinue"],
                    capture_output=True, timeout=8
                )
            except Exception:
                pass
            # Keyin aniq exe nomlari bilan taskkill
            for exe in (
                'wmplayer.exe', 'Music.UI.exe', 'Music.exe', 'GrooveMusic.exe',
                'Video.UI.exe', 'vlc.exe', 'Spotify.exe', 'iTunes.exe'
            ):
                _taskkill(exe)
            speak_queue.append("Musiqa o'chirildi.")
        else:
            subprocess.run(['pkill', '-f', 'vlc'], capture_output=True)
            subprocess.run(['pkill', '-f', 'rhythmbox'], capture_output=True)
            speak_queue.append("Musiqa o'chirildi.")

    elif cmd == 'close_browser':
        if sys.platform == "win32":
            for exe in ('msedge.exe', 'chrome.exe', 'firefox.exe', 'iexplore.exe', 'browser.exe'):
                _taskkill(exe)
            speak_queue.append("Brauzer yopildi.")
        else:
            os.system('pkill -f firefox; pkill -f chrome; pkill -f chromium 2>/dev/null')
            speak_queue.append("Brauzer yopildi.")

    elif cmd == 'close_calc':
        if sys.platform == "win32":
            _taskkill('CalculatorApp.exe')
            _taskkill('calc.exe')
            speak_queue.append("Kalkulyator yopildi.")
        else:
            os.system('pkill -f gnome-calculator 2>/dev/null')
            speak_queue.append("Kalkulyator yopildi.")

    elif cmd == 'close_notepad':
        if sys.platform == "win32":
            _taskkill('notepad.exe')
            speak_queue.append("Bloknot yopildi.")
        else:
            os.system('pkill -f gedit 2>/dev/null')
            speak_queue.append("Bloknot yopildi.")

    elif cmd == 'close_telegram':
        if sys.platform == "win32":
            for exe in ('Telegram.exe', 'telegram.exe'):
                _taskkill(exe)
            speak_queue.append("Telegram yopildi.")
        else:
            os.system('pkill -f telegram 2>/dev/null')
            speak_queue.append("Telegram yopildi.")

    elif cmd == 'close_all_apps':
        if sys.platform == "win32":
            for exe in (
                'wmplayer.exe', 'Music.UI.exe', 'Music.exe', 'GrooveMusic.exe', 'Video.UI.exe', 'vlc.exe',
                'CalculatorApp.exe', 'calc.exe', 'notepad.exe',
                'msedge.exe', 'chrome.exe', 'firefox.exe', 'iexplore.exe',
                'Telegram.exe', 'Code.exe'
            ):
                _taskkill(exe)
            try:
                subprocess.run(
                    ['powershell', '-Command',
                     "Get-Process | Where-Object {$_.ProcessName -match 'Music|Chrome|Edge|Firefox|Calculator|notepad|Telegram|Code'} | Stop-Process -Force -ErrorAction SilentlyContinue"],
                    capture_output=True, timeout=8
                )
            except Exception:
                pass
            speak_queue.append("Hamma ilovalar yopildi.")
        else:
            os.system('pkill -f wmplayer; pkill -f gnome-calculator; pkill -f gedit; pkill -f firefox; pkill -f chrome; pkill -f telegram 2>/dev/null')
            speak_queue.append("Hamma ilovalar yopildi.")

    elif cmd == 'open_all_apps':
        # Hamma ilovalarni ochadi: muzika, brauzer, kalkulyator, bloknot
        if sys.platform == "win32":
            if os.path.isfile(MUSIC_FILE):
                os.startfile(MUSIC_FILE)
            else:
                music_folder = os.path.join(os.path.expanduser("~"), "OneDrive", "Music")
                if not os.path.isdir(music_folder):
                    music_folder = os.path.join(os.path.expanduser("~"), "Music")
                if os.path.isdir(music_folder):
                    os.startfile(music_folder)
            os.system('start https://www.google.com')
            os.system('start calc')
            os.system('start notepad')
        else:
            webbrowser.open('https://www.google.com')
            subprocess.Popen(['gnome-calculator'] if os.path.exists('/usr/bin/gnome-calculator') else ['calc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.Popen(['gedit', '--new-window'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.isfile(MUSIC_FILE):
                subprocess.Popen(['xdg-open', MUSIC_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        speak_queue.append("Hamma ilovalar ochildi.")

    elif cmd == 'open_browser':
        # Faqat Google akkaunt — bitta sahifa, o'z voshimcha yo'q
        try:
            _chrome_open_url("https://accounts.google.com", "Google akkaunt ochildi.")
        except Exception:
            try:
                os.system('start https://accounts.google.com' if sys.platform == "win32" else 'xdg-open https://accounts.google.com')
                speak_queue.append("Google akkaunt ochildi.")
            except Exception:
                speak_queue.append("Brauzerni ochib bo'lmadi.")

    elif cmd == 'open_browser_google':
        try:
            _chrome_open_url("https://accounts.google.com", "Google akkaunt ochildi.")
        except Exception:
            os.system('start https://accounts.google.com' if sys.platform == "win32" else 'xdg-open https://accounts.google.com')
            speak_queue.append("Google akkaunt ochildi.")

    elif cmd == 'open_browser_microsoft':
        try:
            _chrome_open_url("https://account.microsoft.com", "Microsoft akkaunt ochildi.")
        except Exception:
            os.system('start https://account.microsoft.com' if sys.platform == "win32" else 'xdg-open https://account.microsoft.com')
            speak_queue.append("Microsoft akkaunt ochildi.")

    elif cmd == 'open_chrome_m':
        profile_dir = CHROME_PROFILES.get("m", "Default")
        _chrome_open_profile(profile_dir, "M akkauntdagi Chrome ochildi.")

    elif cmd == 'open_chrome_shms':
        profile_dir = CHROME_PROFILES.get("shms", "Profile 2")
        _chrome_open_profile(profile_dir, "SHMS akkauntdagi Chrome ochildi.")

    elif cmd == 'open_chrome_abdurahmon':
        profile_dir = CHROME_PROFILES.get("abdurahmon", "Profile 3")
        _chrome_open_profile(profile_dir, "Abdurahmon akkauntdagi Chrome ochildi.")

    elif cmd == 'open_calc':
        if sys.platform == "win32":
            os.system('start calc')
            speak_queue.append("Kalkulyator ochildi.")
        else:
            subprocess.Popen(['gnome-calculator'] if os.path.exists('/usr/bin/gnome-calculator') else ['calc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            speak_queue.append("Kalkulyator ochildi.")

    elif cmd == 'open_notepad':
        if sys.platform == "win32":
            os.system('start notepad')
            speak_queue.append("Bloknot ochildi.")
        else:
            subprocess.Popen(['gedit', '--new-window'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            speak_queue.append("Matn muharriri ochildi.")

    elif cmd == 'open_telegram':
        # Desktop ichidagi telegram (qisqa yo'l yoki papka)
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Desktop")
        if not os.path.isdir(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        opened = False
        for name in ('telegram', 'Telegram', 'Telegram.lnk', 'telegram.lnk'):
            path = os.path.join(desktop, name)
            if os.path.isfile(path):
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                opened = True
                break
            if os.path.isdir(path):
                # Papka ichida Telegram.exe yoki .lnk qidirish
                for f in os.listdir(path):
                    if f.lower().endswith(('.exe', '.lnk')) and 'telegram' in f.lower():
                        if sys.platform == "win32":
                            os.startfile(os.path.join(path, f))
                        else:
                            subprocess.Popen(['xdg-open', os.path.join(path, f)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        opened = True
                        break
                if not opened:
                    if sys.platform == "win32":
                        os.startfile(path)
                    else:
                        subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                opened = True
                break
        if opened:
            speak_queue.append("Telegram ochildi. Saqlangan yoki so'nggi chatga o'ting va xabaringizni o'zingiz yozing.")
        else:
            speak_queue.append("Desktopda Telegram topilmadi. Desktop papkasiga telegram qisqa yo'lini qo'ying.")

    elif cmd == 'open_vscode':
        # Desktop ichidagi "Visual Studio Code" (qisqa yo'l yoki papka)
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "Desktop")
        if not os.path.isdir(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        opened = False
        for name in ('Visual Studio Code', 'Visual Studio Code.lnk', 'vs code', 'VSCode.lnk'):
            path = os.path.join(desktop, name)
            if os.path.isfile(path):
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                opened = True
                break
            if os.path.isdir(path):
                # Papka ichida Code.exe qidirish
                for f in os.listdir(path):
                    if f == 'Code.exe' or (f.lower().endswith('.exe') and 'code' in f.lower()):
                        if sys.platform == "win32":
                            os.startfile(os.path.join(path, f))
                        else:
                            subprocess.Popen(['xdg-open', os.path.join(path, f)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        opened = True
                        break
                if not opened:
                    if sys.platform == "win32":
                        os.startfile(path)
                    else:
                        subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                opened = True
                break
        if opened:
            speak_queue.append("Visual Studio Code ochildi.")
        else:
            speak_queue.append("Desktopda Visual Studio Code topilmadi. Desktop papkasiga VS Code qisqa yo'lini qo'ying.")

    elif cmd == 'stupid1':
        latifalar = [
            "Bitta afandi Bahriddin_99 profiliga obuna bo'lmagan ekan, proyektlari o'chib ketibdi! Ha ha ha!",
            "O'qituvchi so'radi: Ikki qushda nechta qanot? O'quvchi javob berdi: To'rt ta! O'qituvchi: Yo'q, sakkiz ta. O'quvchi: Siz ikkalasini ham hisoblab oldingiz, men faqat birini.",
            "Bola otasiga: Papa, maktabda meni eng aqlli deb tanladilar. Ota: Nega? Bola: Savol berishdi, javobni men bilmadim, boshqalar ham bilmadilar.",
        ]
        speak_queue.append(random.choice(latifalar))

    else:
        print('Tushunarsiz gap!')



def get_microphone():
    """Mikrofonni avtomatik tanlaydi: avval 0, keyin 1, hato bo'lsa keyingisi."""
    for idx in [0, 1, 2]:
        try:
            m = sr.Microphone(device_index=idx)
            with m as source:
                pass
            print(f"[log] Mikrofon ishlatilmoqda: device_index={idx}")
            return m
        except (OSError, AttributeError):
            continue
    print("[xato] Hech qanday mikrofon topilmadi. device_index=0 bilan urinib ko'ring.")
    return sr.Microphone(device_index=0)


def main():
    global speak_engine
    r = sr.Recognizer()
    m = get_microphone()

    with m as source:
        r.adjust_for_ambient_noise(source, duration=0.5)

    speak_engine = pyttsx3.init()
    voices = speak_engine.getProperty('voices')
    if voices:
        speak_engine.setProperty('voice', voices[0].id)
    # Ovoz tezligi: kichikroq = sekinroq (odatda 200, 130–150 = sekinroq)
    speak_engine.setProperty('rate', 130)

    print("\n  >>> BUYRUQ BERISH: avval \"Jarvis\" deb ayting, keyin buyruq (masalan: soat necha, telegram och, musiqani yop)\n")
    speak("Salom. Men Jarvis.")
    speak("Buyruq bering.")

    stop_listening = r.listen_in_background(m, callback)
    try:
        while True:
            # Navbatdagi matnlarni asosiy threadda ovozda aytish (pyttsx3 boshqa threadda ishlamaydi)
            while speak_queue:
                text = speak_queue.pop(0)
                speak(text)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nJarvis to'xtatildi.")


if __name__ == "__main__":
    main()
