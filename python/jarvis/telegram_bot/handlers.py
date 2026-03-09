# -*- coding: utf-8 -*-
"""Jarvis Telegram bot — bitta so'rov, bitta javob. Faqat ruxsatli ID, paroldan keyin ishlaydi."""
import os
from telegram import Update
from telegram.ext import ContextTypes

from config import ALLOWED_TELEGRAM_ID, BOT_PASSWORD, MUSIC_FILE
from intents import get_intent
from actions import (
    run_music,
    run_calc,
    run_calc_with_expression,
    run_notepad,
    run_file_explorer,
    run_telegram,
    run_telegram_send,
    run_browser,
    run_browser_search,
    run_chrome_profile,
    run_chrome_search,
    run_chrome_search_in_open,
    run_ai_open,
    run_ai_prompt,
    run_ai_close,
    run_youtube,
    run_youtube_app,
    run_youtube_search,
    close_youtube,
    run_calendar,
    run_alarm_open,
    run_cursor,
    run_vscode,
    run_save_code,
    close_music,
    screen_off,
    screen_on,
    wifi_connect,
    wifi_disconnect,
    close_browser,
    close_chrome_profile,
    close_calc,
    close_clock,
    close_notepad,
    close_file_explorer,
    close_telegram,
    close_vscode,
    close_cursor,
    close_all,
    run_close_by_target,
)
from app_discovery import run_app_by_name
from history_store import (
    add_bot_log,
    find_taught_app,
    add_taught_app,
    get_taught_answer,
    add_taught_qa,
    get_all_custom_commands,
    add_custom_command,
    update_custom_command,
    delete_custom_command,
    delete_custom_command_by_nomi,
    find_custom_command,
    get_custom_command_by_id,
)
from keyboards import MAIN_MENU, kb_buyruqlar, kb_orgatish, kb_bot_yop, kb_cmd_row, kb_builtin_cmd_row, kb_suhbat

MAX_HISTORY = 10

# Standart (eski) buyruqlar — Hamma buyruqlar bo'limida ko'rsatiladi
BUILTIN_COMMANDS = [
    ("musiqa och", MUSIC_FILE if MUSIC_FILE else "— qo'shiq fayli (config)"),
    ("musiqa yop", "musiqa ijrochisini yopadi (Windows Media Player, VLC va b.)"),
    ("kalkulator och", "Calculator"),
    ("kalkulator yop", "CalculatorApp.exe"),
    ("brauzer och", "Brauzer"),
    ("brauzer qidir ...", "Brauzerda Google qidiruv"),
    ("brauzer yop", "Chrome / Edge / Firefox yopiladi"),
    ("yutub och", "YouTube ilovasi (Desktop/YouTube)"),
    ("yutub yop", "YouTube oynasini yopadi"),
    ("yutub qidir ...", "YouTube da qidiruv"),
    ("MS och", "Chrome — muhammad810s6443@gmail.com"),
    ("SHMS och", "Chrome — shms810s64.43@gmail.com"),
    ("SOLIH och", "Chrome — muhammad2007solih@gmail.com"),
    ("SODIQ och", "Chrome — muhammad.shukurullayev011@gmail.com"),
    ("MS yop", "Chrome (MS) va qidiruv oynasini yopadi"),
    ("SHMS yop", "Chrome (SHMS) va qidiruv oynasini yopadi"),
    ("SOLIH yop", "Chrome (SOLIH) va qidiruv oynasini yopadi"),
    ("SODIQ yop", "Chrome (SODIQ) va qidiruv oynasini yopadi"),
    ("MS qidir ...", "Chrome (MS) da Google qidiruv"),
    ("SHMS qidir ...", "Chrome (SHMS) da Google qidiruv"),
    ("SOLIH qidir ...", "Chrome (SOLIH) da Google qidiruv"),
    ("SODIQ qidir ...", "Chrome (SODIQ) da Google qidiruv"),
    ("ai och", "ChatGPT (chatgpt.com) — MS brauzerida"),
    ("ai yop", "ChatGPT oynasini (MS brauzerida) yopadi"),
    ("prompt: ...", "Matn buferga nusxalanadi, ChatGPT ochiladi — sahifada Ctrl+V"),
    ("kalkulator och hisobla: 5+5", "Kalkulator ochiladi, ifoda kiritiladi, = bosiladi"),
    ("bloknot och", "Notepad"),
    ("bloknot yop", "notepad.exe"),
    ("fayl och", "Fayl ilovasi (Explorer)"),
    ("fayl yop", "Fayl ilovasi (ochiq papka oynalari) yopiladi"),
    ("telegram och", "Telegram Desktop"),
    ("telegram och bunga: ibo prompt: salom qalesan", "Telegram ochiladi, «ibo» ga xabar yuboriladi, bot «Yuborildi» deb javob beradi"),
    ("telegram yop", "Telegram.exe"),
    ("kalendar och", "Windows Kalendar"),
    ("budink och", "Clock ilovasi, Alarm bo'limi"),
    ("budink och qo'y: 02:04", "Clock ochiladi, berilgan vaqtga budilnik qo'yiladi"),
    ("clock yop", "Clock / Alarms & Clock ilovasini yopadi"),
    ("budink yop", "Clock ilovasini yopadi (budink yop / bufink yop)"),
    ("cursor och", "Cursor (Python papkasi)"),
    ("cursor yop", "Cursor.exe"),
    ("vs code och", "VS Code"),
    ("vs code yop", "Code.exe"),
    ("hamma yop", "barcha ilovalar (musiqa, brauzer, kalkulator, ...)"),
    ("ekrani yop", "notebook/kompyuter ekranini o'chiradi"),
    ("ekrani yoq", "ekranni yoqadi, Enter bosadi (uyg'otadi)"),
    ("ekran och", "ekranni yoqadi, Enter bosadi (ekrani yoq bilan bir xil)"),
    ("wi-fi yoq nomi: MW", "Wi-Fi ga ulash (MW o'rniga tarmoq nomingizni yozing)"),
    ("wi-fi yop", "Wi-Fi ni uzish (o'chirish)"),
]


def _run_standard_command(text: str) -> str:
    """Standart buyruq matnini bajaradi va javob xabarini qaytaradi (tugma yoki matn uchun)."""
    intent, value = get_intent(text)
    if intent == "music":
        ok, msg = run_music()
        return msg
    if intent == "calc":
        ok, msg = run_calc()
        return msg
    if intent == "calc_expression" and value:
        ok, msg = run_calc_with_expression(value)
        return msg
    if intent == "calendar":
        ok, msg = run_calendar()
        return msg
    if intent == "alarm_open":
        ok, msg = run_alarm_open(value)
        return msg
    if intent == "notepad":
        ok, msg = run_notepad()
        return msg
    if intent == "file_explorer":
        ok, msg = run_file_explorer()
        return msg
    if intent == "telegram":
        ok, msg = run_telegram()
        return msg
    if intent == "browser":
        ok, msg = run_browser()
        return msg
    if intent == "browser_search" and value:
        ok, msg = run_browser_search(value)
        return msg
    if intent == "youtube_search" and value:
        ok, msg = run_youtube_search(value)
        return msg
    if intent == "close_youtube":
        ok, msg = close_youtube()
        return msg
    if intent == "chrome_profile" and value:
        ok, msg = run_chrome_profile(value)
        return msg
    if intent == "chrome_close_profile" and value:
        ok, msg = close_chrome_profile(value)
        return msg
    if intent == "chrome_search" and value and "|||" in value:
        key, query = value.split("|||", 1)
        key, query = key.strip(), query.strip()
        ok, msg = run_chrome_search(key, query)
        return msg
    if intent == "ai_open":
        ok, msg = run_ai_open()
        return msg
    if intent == "ai_prompt" and value:
        ok, msg = run_ai_prompt(value)
        return msg
    if intent == "ai_close":
        ok, msg = run_ai_close()
        return msg
    if intent == "close_music":
        ok, msg = close_music()
        return msg
    if intent == "screen_off":
        ok, msg = screen_off()
        return msg
    if intent == "screen_on":
        ok, msg = screen_on()
        return msg
    if intent == "wifi_on" and value:
        ok, msg = wifi_connect(value)
        return msg
    if intent == "wifi_off":
        ok, msg = wifi_disconnect()
        return msg
    if intent == "close_browser":
        ok, msg = close_browser()
        return msg
    if intent == "close_youtube":
        ok, msg = close_youtube()
        return msg
    if intent == "close_calc":
        ok, msg = close_calc()
        return msg
    if intent == "close_clock":
        ok, msg = close_clock()
        return msg
    if intent == "close_notepad":
        ok, msg = close_notepad()
        return msg
    if intent == "close_file_explorer":
        ok, msg = close_file_explorer()
        return msg
    if intent == "close_telegram":
        ok, msg = close_telegram()
        return msg
    if intent == "close_vscode":
        ok, msg = close_vscode()
        return msg
    if intent == "close_cursor":
        ok, msg = close_cursor()
        return msg
    if intent == "close_all":
        ok, msg = close_all()
        return msg
    if intent == "cursor":
        ok, msg = run_cursor()
        return msg
    if intent == "vscode":
        ok, msg = run_vscode()
        return msg
    return "Bu buyruq bajarilmadi."


def _get_history(context: ContextTypes.DEFAULT_TYPE) -> list:
    if "jarvis_history" not in context.user_data:
        context.user_data["jarvis_history"] = []
    return context.user_data["jarvis_history"]


def _add_to_history(history: list, role: str, content: str):
    history.append({"role": role, "content": content})
    while len(history) > MAX_HISTORY:
        history.pop(0)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else 0
    if user_id != ALLOWED_TELEGRAM_ID:
        await update.message.reply_text("🚫 Sizga botdan foydalanish ruxsati yo'q.")
        return
    _get_history(context).clear()
    context.user_data["authenticated"] = False
    context.user_data.pop("teach_state", None)
    context.user_data.pop("teach_question", None)
    await update.message.reply_text("👋 Assalomu alaykum. Botdan foydalanish uchun parolni kiriting.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else 0
    if user_id != ALLOWED_TELEGRAM_ID:
        await update.message.reply_text("🚫 Sizga botdan foydalanish ruxsati yo'q.")
        return

    text = (update.message.text or "").strip()

    # Parol tekshiruvi — parol kiritilmaguncha hech narsa bajarmaydi
    if not context.user_data.get("authenticated"):
        if text == BOT_PASSWORD:
            context.user_data["authenticated"] = True
            context.user_data["mode"] = "command"
            try:
                await update.message.delete()
            except Exception:
                pass
            await update.message.reply_text(
                "✅ Kirish muvaffaqiyatli. Quyidagi menyudan bo'limni tanlang.",
                reply_markup=MAIN_MENU,
            )
            return
        await update.message.reply_text("❌ Noto'g'ri parol. To'g'ri parolni kiriting.")
        return

    user_id = update.effective_user.id if update.effective_user else 0

    # ——— Asosiy menyu (tugma matni emoji bilan yoki emojisiz bo'lishi mumkin) ———
    if text in ("Buyruqlar", "📋 Buyruqlar"):
        await update.message.reply_text("📋 Buyruqlar:", reply_markup=kb_buyruqlar())
        return
    if text in ("O'rgatish", "📚 O'rgatish"):
        await update.message.reply_text("📚 O'rgatish:", reply_markup=kb_orgatish())
        return
    if text in ("Bot yop", "🔒 Bot yop"):
        await update.message.reply_text(
            "🔒 Botni qulflash uchun quyidagi tugmani bosing. Keyin bot yana parol so'raydi.",
            reply_markup=kb_bot_yop(),
        )
        return
    if text in ("Hamma buyruqlar", "📜 Hamma buyruqlar"):
        # Eski (standart) buyruqlar — har biriga Tahrirlash / O'chirish tugmalari
        await update.message.reply_text("📜 Eski (standart) buyruqlar:")
        for i, (nomi, fayl) in enumerate(BUILTIN_COMMANDS):
            await update.message.reply_text(
                f"nomi: {nomi}\nfayl: {fayl}",
                reply_markup=kb_builtin_cmd_row(i),
            )
        # Yangi (qo'shilgan) buyruqlar
        commands = get_all_custom_commands()
        await update.message.reply_text("➕ Yangi (qo'shilgan) buyruqlar:")
        if not commands:
            await update.message.reply_text("📭 Buyruq yo'q. O'rgatish bo'limiga o'ting.")
        else:
            for row in commands:
                cid, nomi, fayl, turi, _ = row[0], row[1], row[2], row[3], row[4]
                await update.message.reply_text(
                    f"nomi: {nomi}\nfayl: {fayl}",
                    reply_markup=kb_cmd_row(cid),
                )
        return

    # ——— O'rgatish rejimi (state) ———
    teach_state = context.user_data.get("teach_state")
    if teach_state == "teach_app":
        context.user_data.pop("teach_state", None)
        await update.message.reply_text("Bu bo'lim o'chirilgan. Iltimos, boshqa bo'limlardan foydalaning.")
        return
    if teach_state == "teach_chat_question":
        context.user_data["teach_question"] = text
        context.user_data["teach_state"] = "teach_chat_answer"
        await update.message.reply_text("💬 Bot javobini yozing (masalan: Assalomu alaykum, nima gap yaxshimisiz?)")
        return
    if teach_state == "teach_chat_answer":
        context.user_data.pop("teach_state", None)
        q = context.user_data.pop("teach_question", "")
        if not q:
            await update.message.reply_text("❌ Savol saqlanmagan. Qaytadan o'rgatishni boshlang.")
            return
        updated = add_taught_qa(q, text)
        add_bot_log("teach_chat", "Q&A yangilandi" if updated else "Q&A saqlandi", "")
        await update.message.reply_text(
            "✅ Suhbat javobi yangilandi." if updated else "✅ Suhbat javobi saqlandi."
        )
        return
    if teach_state == "teach_cmd_type":
        context.user_data.pop("teach_state", None)
        if text.strip() == "1":
            context.user_data["teach_state"] = "teach_cmd_och_nomi"
            await update.message.reply_text("✏️ Buyruq nomini kiriting (masalan: musiqa och):")
            return
        if text.strip() == "2":
            context.user_data["teach_state"] = "teach_cmd_yop_nomi"
            await update.message.reply_text("✏️ Buyruq nomini kiriting (masalan: musiqa yop):")
            return
        await update.message.reply_text("❓ 1 yoki 2 kiriting.")
        return
    if teach_state == "teach_cmd_och_nomi":
        context.user_data["teach_cmd_nomi"] = text
        context.user_data["teach_state"] = "teach_cmd_och_fayl"
        await update.message.reply_text("📁 Fayl yoki ilova yo'lini kiriting (masalan: C:\\Users\\...\\file.mp3 yoki ilova.exe):")
        return
    if teach_state == "teach_cmd_och_fayl":
        context.user_data.pop("teach_state", None)
        nomi = context.user_data.pop("teach_cmd_nomi", "")
        if not nomi:
            await update.message.reply_text("❌ Nomi saqlanmagan. Qaytadan: O'rgatish → Buyruq qo'shish (och/yop).")
            return
        add_custom_command(nomi, text, "open")
        add_bot_log("teach_cmd", "Ochish", "")
        await update.message.reply_text(f"✅ Buyruq qo'shildi: «{nomi}» → ochadi.")
        return
    if teach_state == "teach_cmd_yop_nomi":
        context.user_data["teach_cmd_nomi"] = text
        context.user_data["teach_state"] = "teach_cmd_yop_fayl"
        await update.message.reply_text(
            "📁 Yopiladigan ilova joylashuvini (yoki jarayon nomini) kiriting:\n"
            "Masalan: C:\\Program Files\\Ilova\\app.exe yoki notepad"
        )
        return
    if teach_state == "teach_cmd_yop_fayl":
        context.user_data.pop("teach_state", None)
        nomi = context.user_data.pop("teach_cmd_nomi", "")
        if not nomi:
            await update.message.reply_text("❌ Nomi saqlanmagan. Qaytadan: O'rgatish → Buyruq qo'shish (och/yop).")
            return
        # saqlanadigan qiymat foydalanuvchi kiritganidek bo'lsin (to'liq yo'l yoki nom)
        target = text.strip()
        add_custom_command(nomi, target, "close")
        add_bot_log("teach_cmd", "Yopish", "")
        await update.message.reply_text(f"✅ Buyruq qo'shildi: «{nomi}» → yopadi ({target}).")
        return
    if teach_state and teach_state.startswith("edit_cmd_"):
        try:
            cmd_id = int(teach_state.replace("edit_cmd_", ""))
        except ValueError:
            context.user_data.pop("teach_state", None)
            await update.message.reply_text("❌ Xato. Qaytadan urinib ko'ring.")
            return
        step = context.user_data.get("edit_cmd_step", 1)
        if step == 1:
            context.user_data["edit_cmd_nomi"] = text
            context.user_data["edit_cmd_step"] = 2
            await update.message.reply_text("📁 Yangi fayl/yo'l kiriting:")
            return
        if step == 2:
            context.user_data.pop("teach_state", None)
            context.user_data.pop("edit_cmd_step", None)
            nomi = context.user_data.pop("edit_cmd_nomi", "")
            if update_custom_command(cmd_id, nomi, text):
                add_bot_log("edit_cmd", "Yangilandi", "")
                await update.message.reply_text("✅ Buyruq yangilandi.")
            else:
                await update.message.reply_text("❌ Buyruq topilmadi yoki yangilanmadi.")
            return

    if teach_state and teach_state.startswith("edit_builtin_"):
        try:
            idx = int(teach_state.replace("edit_builtin_", ""))
        except ValueError:
            context.user_data.pop("teach_state", None)
            context.user_data.pop("edit_builtin_step", None)
            context.user_data.pop("edit_builtin_turi", None)
            await update.message.reply_text("❌ Xato. Qaytadan urinib ko'ring.")
            return
        if idx < 0 or idx >= len(BUILTIN_COMMANDS):
            context.user_data.pop("teach_state", None)
            await update.message.reply_text("❌ Buyruq topilmadi.")
            return
        step = context.user_data.get("edit_builtin_step", 1)
        nomi_builtin, _ = BUILTIN_COMMANDS[idx]
        if step == 1:
            context.user_data["edit_builtin_nomi"] = text.strip()
            context.user_data["edit_builtin_step"] = 2
            turi = context.user_data.get("edit_builtin_turi", "open")
            if turi == "close":
                await update.message.reply_text("🔴 Yopiladigan jarayon nomini kiriting (masalan: CalculatorApp, wmplayer, notepad):")
            else:
                await update.message.reply_text("📁 Fayl yoki ilova yo'lini kiriting (masalan: C:\\...\\file.exe yoki ilova yo'li):")
            return
        if step == 2:
            context.user_data.pop("teach_state", None)
            context.user_data.pop("edit_builtin_step", None)
            nomi = (context.user_data.pop("edit_builtin_nomi", "") or nomi_builtin).strip()
            turi = context.user_data.pop("edit_builtin_turi", "open")
            if not nomi:
                nomi = nomi_builtin
            add_custom_command(nomi, text.strip(), turi)
            add_bot_log("command", "builtin_override", nomi)
            await update.message.reply_text(f"✅ Buyruq saqlandi. «{nomi}» endi siz kiritgan yo'l/jarayon bilan ishlaydi (standart ustidan yozildi).")
            return

    if not text:
        await update.message.reply_text("✍️ Xabaringizni yozing.")
        return

    mode = context.user_data.get("mode", "command")

    # ——— Suhbat rejimi: tozalash so'zi yoki avval o'rgatilgan javob, keyin AI ———
    if mode == "chat":
        chat_submode = context.user_data.get("chat_submode")

        # Agar submode tanlanyutgan bo'lmasa — tugmalarga qaytarish
        if not chat_submode:
            await update.message.reply_text(
                "💬 Suhbat bo'limini tanlang:",
                reply_markup=kb_suhbat(),
            )
            return

        # ——— BILIM OL: faqat o'rgatish bo'limidagi o'rgatilgan javoblar, tashqi Sun'iy intellekt ishlatilmaydi ———
        if chat_submode == "bilim":
            clear_cmd = (text or "").strip().lower() in ("suhbatni tozalash", "tarixni tozalash", "tozalash", "yangi suhbat", "orqaga", "back")
            if clear_cmd:
                context.user_data.pop("chat_submode", None)
                _get_history(context).clear()
                await update.message.reply_text(
                    "💬 Suhbat. Quyidagi bo'limlardan birini tanlang:",
                    reply_markup=kb_suhbat(),
                )
                return

            ans = get_taught_answer(text)
            if ans is not None:
                add_bot_log("chat", "taught_bilim", "")
                await update.message.reply_text(ans)
                return

            add_bot_log("chat", "taught_not_found", "")
            await update.message.reply_text(
                "❌ Bu savol uchun javob o'rgatilmagan.\n"
                "📚 O'rgatish → Suhbatlashishni o'rgatish bo'limida javob qo'shing."
            )
            return

        return

    # ——— Buyruq rejimi: avval maxsus buyruqlar (Hamma buyruqlar dan), keyin standart ———
    custom = find_custom_command(text)
    if custom:
        cid, nomi, fayl, turi = custom
        if turi == "open":
            try:
                os.startfile(fayl)
                msg = f"«{nomi}» bajarildi."
            except Exception:
                msg = f"«{nomi}» bajarilmadi (fayl/yo'l xato)."
            add_bot_log("command", "custom_open", "")
            await update.message.reply_text(msg)
            return
        if turi == "close":
            nomi_l = (nomi or "").strip().lower()
            fayl_trim = (fayl or "").strip()
            if not fayl_trim:
                await update.message.reply_text("❌ Bu yop buyruqida jarayon ko'rsatilmagan. O'rgatishdan qayta kiriting.")
                return
            is_music = "musiqa" in nomi_l or "muzika" in nomi_l or "music" in nomi_l
            if is_music:
                ok, _ = close_music()
            else:
                ok, _ = run_close_by_target(fayl_trim)
            add_bot_log("command", "custom_close", "")
            reply = f"«{nomi}» bajarildi." if ok else f"«{nomi}» bajarilmadi."
            await update.message.reply_text(reply)
            return

    intent, value = get_intent(text)

    # ——— Buyruq: ilova/fayl ochish — bitta javob ———
    def _log_and_reply(ok, msg):
        add_bot_log("command", "bajarildi", "")

    if intent == "music":
        ok, msg = run_music()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "calc":
        ok, msg = run_calc()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "calc_expression" and value:
        ok, msg = run_calc_with_expression(value)
        add_bot_log("command", "hisobla", value)
        await update.message.reply_text(msg)
        return
    if intent == "calendar":
        ok, msg = run_calendar()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "alarm_open":
        ok, msg = run_alarm_open(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "notepad":
        ok, msg = run_notepad()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "file_explorer":
        ok, msg = run_file_explorer()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "telegram":
        ok, msg = run_telegram()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "telegram_send" and value and "|||" in value:
        contact, message = value.split("|||", 1)
        contact, message = contact.strip(), message.strip()
        if contact and message:
            ok, msg = run_telegram_send(contact, message)
            _log_and_reply(ok, msg)
            await update.message.reply_text(msg)
            return
    if intent == "browser":
        ok, msg = run_browser()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "browser_search" and value:
        ok, msg = run_browser_search(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "chrome_profile" and value:
        ok, msg = run_chrome_profile(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        context.user_data["current_chrome_profile"] = value
        return
    if intent == "chrome_close_profile" and value:
        ok, msg = close_chrome_profile(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        context.user_data["current_chrome_profile"] = None
        return
    if intent == "chrome_search" and value and "|||" in value:
        key, query = value.split("|||", 1)
        key, query = key.strip(), query.strip()
        ok, msg = run_chrome_search(key, query)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "ai_open":
        ok, msg = run_ai_open()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "ai_prompt" and value:
        ok, msg = run_ai_prompt(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "ai_close":
        ok, msg = run_ai_close()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "youtube" and value:
        ok, msg = run_youtube(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "youtube_app":
        ok, msg = run_youtube_app()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "youtube_search" and value:
        ok, msg = run_youtube_search(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_youtube":
        ok, msg = close_youtube()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "open_app" and value:
        taught = find_taught_app(value)
        if taught:
            _, path = taught
            try:
                os.startfile(path)
                ok, msg = True, f"{value} ochildi."
            except Exception:
                ok, msg = False, f"{value} ni ochib bo'lmadi."
        else:
            ok, msg = run_app_by_name(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_music":
        ok, msg = close_music()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "screen_off":
        ok, msg = screen_off()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "screen_on":
        ok, msg = screen_on()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "wifi_on" and value:
        ok, msg = wifi_connect(value)
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "wifi_off":
        ok, msg = wifi_disconnect()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_browser":
        ok, msg = close_browser()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_calc":
        ok, msg = close_calc()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_clock":
        ok, msg = close_clock()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_notepad":
        ok, msg = close_notepad()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_file_explorer":
        ok, msg = close_file_explorer()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_telegram":
        ok, msg = close_telegram()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_vscode":
        ok, msg = close_vscode()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_cursor":
        ok, msg = close_cursor()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "close_all":
        ok, msg = close_all()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "cursor":
        ok, msg = run_cursor()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "vscode":
        ok, msg = run_vscode()
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        return
    if intent == "code_save" and value:
        if "|||" in value:
            filename, code = value.split("|||", 1)
            filename, code = filename.strip(), code.strip()
            if not filename:
                filename = "cod_output.py"
        else:
            filename, code = "cod_output.py", value.strip()
        if code:
            ok, msg = run_save_code(filename, code)
            _log_and_reply(ok, msg)
            await update.message.reply_text(msg)
            return

    # ——— Saqlanganga ... deb yozib ber — bitta xabar (matn) ———
    if intent == "saved_message" and value:
        await update.message.reply_text(
            value + "\n\n📌 Ushbu matnni nusxalab Telegram → Saqlangan xabarlarga yuboring."
        )
        return

    # Check for chrome search if profile is open
    current_profile = context.user_data.get("current_chrome_profile")
    if current_profile and text.strip():
        ok, msg = run_chrome_search_in_open(text.strip())
        _log_and_reply(ok, msg)
        await update.message.reply_text(msg)
        context.user_data["current_chrome_profile"] = None
        return

    # ——— Buyruq topilmadi (rejim: buyruq) ———
    await update.message.reply_text("❓ Bu buyruq yo'q. Suhbatlashish uchun: 📋 Buyruqlar → 💬 Suhbatlashish ni bosing.")
    add_bot_log("command", "topilmadi", "")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugmalar: rejim, tarix, o'chirish, o'rgatish."""
    user_id = update.effective_user.id if update.effective_user else 0
    if user_id != ALLOWED_TELEGRAM_ID:
        await update.callback_query.answer("🚫 Ruxsat yo'q.")
        return
    data = (update.callback_query.data or "").strip()
    await update.callback_query.answer()

    if data == "cmd_mode":
        context.user_data["mode"] = "command"
        await update.callback_query.edit_message_text(
            "⚡ Buyruq rejimi. Endi buyruq yuboring: musiqa och, kalkulator och, brauzer och va h.k."
        )
        return
    if data == "chat_mode":
        context.user_data["mode"] = "chat"
        context.user_data.pop("chat_submode", None)
        _get_history(context).clear()
        await update.callback_query.edit_message_text(
            "💬 Suhbat. Quyidagi bo'limlardan birini tanlang:",
            reply_markup=kb_suhbat(),
        )
        return
    if data == "chat_bilim_ol":
        context.user_data["chat_submode"] = "bilim"
        _get_history(context).clear()
        await update.callback_query.edit_message_text(
            "💡 Bilim ol rejimi.\n\nSaid siz bilan nima kerak?",
        )
        return
    if data == "teach_app":
        context.user_data.pop("teach_state", None)
        await update.callback_query.edit_message_text(
            "Bu bo'lim o'chirilgan. Iltimos, «Suhbatlashishni o'rgatish» yoki «Buyruq qo'shish (och/yop)» dan foydalaning."
        )
        return
    if data == "teach_chat":
        context.user_data["teach_state"] = "teach_chat_question"
        await update.callback_query.edit_message_text(
            "💬 Suhbatlashishni o'rgatish. Savolni yozing (foydalanuvchi nimadesa, masalan: Assalomu alaykum)."
        )
        return
    if data == "teach_cmd":
        context.user_data["teach_state"] = "teach_cmd_type"
        await update.callback_query.edit_message_text(
            "➕ Buyruq qo'shish (och/yop).\n1 — Ochish buyruqi (masalan: musiqa och)\n2 — Yopish buyruqi (masalan: musiqa yop)\n\n1 yoki 2 kiriting:"
        )
        return

    if data == "bot_yop":
        context.user_data["authenticated"] = False
        add_bot_log("bot", "qulflandi", "Bot yop")
        await update.callback_query.edit_message_text(
            "🔒 Bot qulflandi. Qayta ishlatish uchun parolni kiriting."
        )
        return

    if data.startswith("edit_builtin_"):
        try:
            idx = int(data.replace("edit_builtin_", ""))
        except ValueError:
            await update.callback_query.edit_message_text("❌ Xato.")
            return
        if idx < 0 or idx >= len(BUILTIN_COMMANDS):
            await update.callback_query.edit_message_text("❌ Buyruq topilmadi.")
            return
        nomi, fayl = BUILTIN_COMMANDS[idx]
        turi = "close" if " yop" in (nomi or "").lower() else "open"
        context.user_data["teach_state"] = f"edit_builtin_{idx}"
        context.user_data["edit_builtin_step"] = 1
        context.user_data["edit_builtin_turi"] = turi
        add_bot_log("command", "builtin_edit_btn", "")
        await update.callback_query.edit_message_text(
            f"✏️ Standart buyruqni o'zgartirish (ustidan yoziladi).\n\n"
            f"1-qadam: Buyruq nomini kiriting (joriy: «{nomi}»). O'zgartirmasangiz — xuddi shu nomni yozing:"
        )
        return
    if data.startswith("del_builtin_"):
        try:
            idx = int(data.replace("del_builtin_", ""))
        except ValueError:
            await update.callback_query.edit_message_text("❌ Xato.")
            return
        if idx < 0 or idx >= len(BUILTIN_COMMANDS):
            await update.callback_query.edit_message_text("❌ Buyruq topilmadi.")
            return
        nomi = BUILTIN_COMMANDS[idx][0]
        if delete_custom_command_by_nomi(nomi):
            add_bot_log("command", "builtin_restore", nomi)
            await update.callback_query.edit_message_text(
                f"✅ «{nomi}» uchun o'zgartirish olib tashlandi. Buyruq yana standart holatda ishlaydi."
            )
        else:
            await update.callback_query.edit_message_text(
                f"ℹ️ «{nomi}» ustida o'zgartirish yo'q, allaqachon standart holatda."
            )
        return

    if data.startswith("edit_cmd_"):
        try:
            cmd_id = int(data.replace("edit_cmd_", ""))
        except ValueError:
            await update.callback_query.edit_message_text("❌ Xato.")
            return
        cmd = get_custom_command_by_id(cmd_id)
        if not cmd:
            await update.callback_query.edit_message_text("❌ Buyruq topilmadi.")
            return
        context.user_data["teach_state"] = f"edit_cmd_{cmd_id}"
        context.user_data["edit_cmd_step"] = 1
        await update.callback_query.edit_message_text(
            "✏️ Buyruq tahrirlash. Yangi nomini kiriting (masalan: musiqa och):"
        )
        return

    if data.startswith("del_cmd_"):
        try:
            cmd_id = int(data.replace("del_cmd_", ""))
        except ValueError:
            await update.callback_query.edit_message_text("❌ Xato.")
            return
        cmd = get_custom_command_by_id(cmd_id)
        if cmd:
            delete_custom_command(cmd_id)
            add_bot_log("cmd", "o'chirildi", "")
        await update.callback_query.edit_message_text("🗑️ Buyruq o'chirildi. Buyruqlar bo'limida bu buyruq endi ishlamaydi.")
        return
