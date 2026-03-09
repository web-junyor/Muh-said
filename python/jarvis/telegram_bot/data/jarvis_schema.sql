-- -*- coding: utf-8 -*-
-- Jarvis bot: barcha saqlanadigan ma'lumotlar uchun schema.
-- SQLite da ishlatiladi. Ma'lumotlar data/jarvis_history.db da.

-- Buyruq tarixi (musiqa och, kalkulator och va boshqa bajarilgan buyruqlar)
CREATE TABLE IF NOT EXISTS command_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    command_text TEXT NOT NULL,
    result_ok INTEGER NOT NULL,
    result_msg TEXT,
    response_text TEXT,
    created_at TEXT NOT NULL
);

-- O'rgatilgan ilovalar (ilovalarni o'rgatish bo'limi)
CREATE TABLE IF NOT EXISTS taught_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT NOT NULL,
    path_or_exe TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- O'rgatilgan suhbat javoblari (suhbatlashishni o'rgatish)
CREATE TABLE IF NOT EXISTS taught_qa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Bot logi (qisqacha ishlash logi)
CREATE TABLE IF NOT EXISTS bot_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    log_type TEXT NOT NULL,
    message TEXT,
    detail TEXT
);

-- Foydalanuvchi qo'shgan buyruqlar (Hamma buyruqlar bo'limi: och/yop)
CREATE TABLE IF NOT EXISTS custom_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomi TEXT NOT NULL,
    fayl TEXT NOT NULL,
    turi TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Indekslar (tez qidirish uchun)
CREATE INDEX IF NOT EXISTS idx_command_history_created ON command_history(created_at);
CREATE INDEX IF NOT EXISTS idx_command_history_user ON command_history(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_log_created ON bot_log(created_at);
