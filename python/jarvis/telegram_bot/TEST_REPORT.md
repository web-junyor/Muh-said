# Jarvis Telegram bot — tekshiruv hisoboti

**Sana:** 2025  
**Tekshiruv turi:** Barcha bo'limlar va buyruqlar (senyor daraja).

---

## 1. Asosiy menyu (keyboards)

| Tugma | Handler | Holat |
|-------|---------|--------|
| Buyruqlar | `text == "Buyruqlar"` → kb_buyruqlar() | ✅ |
| Hamma buyruqlar | `text == "Hamma buyruqlar"` → BUILTIN + custom | ✅ |
| O'rgatish | `text == "O'rgatish"` → kb_orgatish() | ✅ |
| Bot yop | `text == "Bot yop"` → kb_bot_yop() | ✅ |

Ketma-ketlik: Buyruqlar, Hamma buyruqlar, O'rgatish, Bot yop — to'g'ri.

---

## 2. Buyruqlar bo'limi (inline)

| Callback | Vazifa | Holat |
|----------|--------|--------|
| cmd_mode | Buyruq rejimi | ✅ |
| chat_mode | Suhbat rejimi | ✅ |

---

## 3. Hamma buyruqlar

- **Eski (standart):** 31 ta buyruq, har biri uchun `kb_builtin_cmd_row(i)` (Tahrirlash / O'chirish).
- **edit_builtin_ / del_builtin_:** `_run_standard_command(BUILTIN_COMMANDS[i][0])` — buyruq bajariladi.
- **Yangi:** `get_all_custom_commands()`, har biri uchun `kb_cmd_row(cid)`.
- **edit_cmd_ / del_cmd_:** Tahrirlash rejimi va o'chirish ishlaydi.

---

## 4. O'rgatish

| Callback | State / vazifa | Holat |
|----------|----------------|--------|
| teach_app | Ilova qo'shish (path, name) | ✅ |
| teach_chat | Savol-javob qo'shish | ✅ |
| teach_cmd | Buyruq qo'shish (1-och, 2-yop) | ✅ |
| edit_cmd_X | Tahrirlash (nomi, keyin fayl) | ✅ |
| del_cmd_X | O'chirish | ✅ |

---

## 5. Bot yop

| Callback | Vazifa | Holat |
|----------|--------|--------|
| bot_yop | authenticated = False, xabar | ✅ |

---

## 6. Intent → handler mosligi

Barcha `get_intent()` qaytadigan intentlar handle_text va _run_standard_command da qayta ishlanadi:

- music, calc, calendar, notepad, telegram, browser ✅
- chrome_profile, chrome_search ✅
- ai_open, ai_prompt, ai_close ✅
- close_music, screen_off, screen_on, wifi_on, wifi_off ✅
- close_browser, close_calc, close_notepad, close_telegram, close_vscode, close_cursor, close_all ✅
- cursor, vscode ✅
- youtube, youtube_app, youtube_search, open_app, code_save, cursor_prompt, saved_message ✅
- chat (default) → Sun'iy intellekt suhbat ✅

---

## 7. Qisqa test (bajarilgan)

- `get_intent("musiqa och")` → music ✅
- `get_intent("ai och")` → ai_open ✅
- `get_intent("ai yop")` → ai_close ✅
- `get_intent("MS och")` → chrome_profile ✅
- `get_intent("wi-fi yop")` → wifi_off ✅
- `_run_standard_command("musiqa och")` → javob qaytadi ✅
- `_run_standard_command("ai och")` → "Chrome (MS) ochildi." ✅
- Import: config, intents, actions, handlers, history_store — xatosiz ✅

---

## 8. Xulosa

- Barcha menyu tugmalari va callback'lar bog'langan.
- Intentlar to'liq qayta ishlanadi (message handler va _run_standard_command).
- Hamma buyruqlar (eski + yangi) tugmalar orqali ishlaydi.
- O'rgatish (ilova, suhbat, buyruq) va Bot yop rejimi ishlaydi.

**Tavsiya:** Telegram serveriga ulanish va real foydalanuvchi bilan bir marta barcha bo'limlarni qo'lda tekshirish (parol, Buyruqlar, Hamma buyruqlar, O'rgatish, Bot yop va bir nechta buyruq matni).
