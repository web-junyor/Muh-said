import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from docx import Document
from aiogram.types import FSInputFile
import asyncio
import logging
from datetime import time

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ENV =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "developer17")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "344601809")

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_FILE = os.path.join(BASE_DIR, "logs.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Template fayllari (UZB va RUS uchun)
TEMPLATES = {
    "missing_days_uz": os.path.join(BASE_DIR, "Tushuntirish xati.docx"),
    "missing_days_ru": os.path.join(BASE_DIR, "Объяснительная.docx"),
    "response_uz": os.path.join(BASE_DIR, "Tushuntirish xati J.docx"),
    "response_ru": os.path.join(BASE_DIR, "Объяснительная J.docx"),
    "rmo_uz": os.path.join(BASE_DIR, "Tushuntirish xati RMO.docx"),
    "rmo_ru": os.path.join(BASE_DIR, "Объяснительная RMO.docx"),
    "late_uz": os.path.join(BASE_DIR, "Tushuntirish xati Grafik.docx"),
    "late_ru": os.path.join(BASE_DIR, "Объяснительная График.docx"),
    "explanation": os.path.join(BASE_DIR, "Tushuntirish xati2026.docx"),
}

def format_time(value: int, unit: str) -> str:
    if unit == "minute":
        t = time(minute=value)
        return t.strftime("%H:%M")
    elif unit == "hour":
        t = time(hour=value)
        return t.strftime("%H:%M")
    return "00:00"


# ===== USERS DATABASE =====
def init_users_db():
    """Users database'ni initialize qil va admin user'ni qo'shish"""
    users = {}

    # Agar users.json mavjud bo'lsa, uni load qil
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    # Admin user'ni qo'shish yoki update qilish
    if "admin" not in users:
        users["admin"] = {
            "password": ADMIN_PASSWORD,
            "user_id": ADMIN_ID,
            "is_admin": True
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        logger.info("Admin user created in users.json")

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def add_user(login, password):
    users = load_users()
    if login in users:
        return False
    users[login] = {"password": password, "is_admin": False}
    save_users(users)
    return True

def delete_user(login):
    users = load_users()
    if login in users:
        del users[login]
        save_users(users)
        return True
    return False

def verify_user(login, password):
    users = load_users()
    if login in users and users[login]["password"] == password:
        return True
    return False

def replace_text_in_runs(paragraph, old_text, new_text):
    """Paragraf ichidagi runs'da matn to'liq almashtiriladi, multi-run placeholder'larni ham qoplaydil"""
    # Barcha run'larni birinchi bog'la
    full_text = paragraph.text
    if old_text not in full_text:
        return

    # Yangi matn yaratish
    new_full_text = full_text.replace(old_text, new_text)

    # Barcha runs'ni o'chir va qayta yaratamiz
    for run in paragraph.runs:
        run.text = ""

    # Yangi matn qo'yamiz birinchi runni saqlab
    if paragraph.runs:
        paragraph.runs[0].text = new_full_text
    else:
        paragraph.add_run(new_full_text)

def replace_placeholders_in_doc(doc, replace_map):
    """Dokument ichidagi barcha placeholder'larni almashtir"""
    # Paragraflar ichida
    for paragraph in doc.paragraphs:
        for placeholder, value in replace_map.items():
            replace_text_in_runs(paragraph, placeholder, value)

    # Jadvallar ichida
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in replace_map.items():
                        replace_text_in_runs(paragraph, placeholder, value)

def add_log(user_id, username, action, template):
    logs = []
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as f:
            logs = json.load(f)
    logs.append({
        "user_id": user_id,
        "username": username,
        "action": action,
        "template": template,
        "timestamp": str(__import__('datetime').datetime.now())
    })
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)

# ===== STATES =====
class Auth(StatesGroup):
    login = State()
    password = State()
    language = State()

class MissingDaysForm(StatesGroup):
    fish = State()
    sana_kel = State()
    sabab = State()
    sana_chiq = State()
    sana = State()

class Form(StatesGroup):
    # ... eski state’lar qoladi

    rmo_name = State()
    rmo_day = State()
    rmo_time_unit = State()
    rmo_time_value = State()
    rmo_date = State()

class ResponseForm(StatesGroup):
    fish = State()
    sana_k = State()
    soat = State()
    soat_i = State()
    sana_ch = State()
    sana1 = State()

class LateForm(StatesGroup):
    fish = State()
    sabab = State()
    soat_da = State()
    sana2 = State()

class ExplanationForm(StatesGroup):
    fish = State()
    tx = State()
    sana3 = State()

class AdminAddUser(StatesGroup):
    login = State()
    password = State()

class AdminDeleteUser(StatesGroup):
    login = State()

# ===== BOT & ROUTER =====
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# ===== START =====
@router.message(F.text == "/start")
async def start(msg: Message, state: FSMContext):
    try:
        logger.info(f"User {msg.from_user.id} ({msg.from_user.username}) started bot")
        await msg.answer("🔐 Botga xush kelibsiz!\n🔐 Добро пожаловать!\n\nLoginni kiriting / Введите логин:")
        await state.set_state(Auth.login)
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await msg.answer(f"❌ Xato: {str(e)}")

# ===== AUTH - LOGIN =====
@router.message(Auth.login)
async def auth_login(msg: Message, state: FSMContext):
    try:
        logger.info(f"Login attempt: {msg.text}")
        await state.update_data(login=msg.text)
        await msg.answer("Parolni kiriting / Введите пароль:")
        await state.set_state(Auth.password)
    except Exception as e:
        logger.error(f"Error in auth_login: {e}")
        await msg.answer(f"❌ Xato: {str(e)}")

# ===== AUTH - PASSWORD =====
@router.message(Auth.password)
async def auth_password(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        login = data.get("login", "")
        password = msg.text

        logger.info(f"Password check for login: {login}")

        if not verify_user(login, password):
            logger.warning(f"Failed login attempt: {login}")
            await msg.answer("❌ Login yoki parol xato!\n❌ Неверный логин или пароль!\n\nDastur tugatildi. / Программа завершена.")
            await state.clear()
            return

        logger.info(f"Successful login: {login}")
        await state.update_data(authenticated=True, username=login)

        # Til tanlash
        keyboard = [
            [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский")]
        ]
        await msg.answer(
            "Tilni tanlang / Выберите язык:",
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        )
        await state.set_state(Auth.language)
    except Exception as e:
        logger.error(f"Error in auth_password: {e}")
        await msg.answer(f"❌ Xato: {str(e)}")
        await state.clear()

# ===== AUTH - LANGUAGE =====
@router.message(Auth.language)
async def auth_language(msg: Message, state: FSMContext):
    if "O'zbek" in msg.text:
        lang = "uz"
    elif "Русский" in msg.text:
        lang = "ru"
    else:
        await msg.answer("❌ Tilni to'g'ri tanlang / Выберите язык правильно")
        return

    await state.update_data(lang=lang)
    await show_menu(msg, state)

# ===== MENU =====
async def show_menu(msg: Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username", "User")
    lang = data.get("lang", "uz")
    user_id = msg.from_user.id

    if lang == "uz":
        keyboard = [
            [KeyboardButton(text="1. Kelmagan kuniz")],
            [KeyboardButton(text="2. Javob so'rash")],
            [KeyboardButton(text="3. RMO")],
            [KeyboardButton(text="4. Kechga qolish")],
            [KeyboardButton(text="5. Tushuntirish xati")]
        ]
        menu_text = f"👋 Salom,  {username}!\n\nBo'limni tanlang:"
    else:
        keyboard = [
            [KeyboardButton(text="1. Дни пропусков")],
            [KeyboardButton(text="2. Запрос ответа")],
            [KeyboardButton(text="3. РМО")],
            [KeyboardButton(text="4. Опоздание")],
            [KeyboardButton(text="5. Пояснительная записка")]
        ]
        menu_text = f"👋 Привет, {username}!\n\nВыберите раздел:"

    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(text="🛠 Admin Panel" if lang == "uz" else "🛠 Админ панель")])

    await msg.answer(menu_text, reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))

    # Lang va username'ni state'da saqlab qolamiz
    await state.update_data(lang=lang, username=username)
    await state.set_state(None)

# ===== MENU HANDLERS =====
@router.message(F.text.regexp(r"1\. (Kelmagan kuniz|Дни пропусков)"))
async def missing_days_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "📋 Kelmagan kuniz bo'limi\n\nFamilia Ismi Sharifni kiriting:" if lang == "uz" else "📋 Раздел дней пропусков\n\nВведите ФИО:"
    await msg.answer(text)
    await state.set_state(MissingDaysForm.fish)

@router.message(F.text.regexp(r"2\. (Javob so'rash|Запрос ответа)"))
async def response_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "📋 Javob so'rash bo'limi\n\nFamilia Ismi Sharifni kiriting:" if lang == "uz" else "📋 Раздел запроса ответа\n\nВведите ФИО:"
    await msg.answer(text)
    await state.set_state(ResponseForm.fish)

@router.message(F.text.regexp(r"🕒 RMO"))
async def rmo_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (
        "👤 F.I.SH kiriting:"
        if lang == "uz"
        else "👤 Введите ФИО:"
    )
    await msg.answer(text)
    await state.set_state(Form.rmo_name)
@router.message(Form.rmo_name)
async def rmo_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)

    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (
        "📅 RMO o‘z vaqtida yoqilmagan kunni kiriting:"
        if lang == "uz"
        else "📅 Укажите день, когда RMO не был включён вовремя:"
    )
    await msg.answer(text)
    await state.set_state(Form.rmo_day)
@router.message(Form.rmo_day)
async def rmo_day(msg: Message, state: FSMContext):
    await state.update_data(rmo_day=msg.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏱ Minut"), KeyboardButton(text="⏱ Soat")]
        ],
        resize_keyboard=True
    )

    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (
        "⏳ Qancha kechikdi?"
        if lang == "uz"
        else "⏳ Насколько опоздал?"
    )
    await msg.answer(text, reply_markup=kb)
    await state.set_state(Form.rmo_time_unit)
@router.message(Form.rmo_time_unit)
async def rmo_time_unit(msg: Message, state: FSMContext):
    if "Minut" in msg.text:
        unit = "minute"
    elif "Soat" in msg.text:
        unit = "hour"
    else:
        await msg.answer("❌ Tugmadan tanlang")
        return

    await state.update_data(rmo_time_unit=unit)
    await msg.answer("🔢 Son kiriting (masalan: 7):")
    await state.set_state(Form.rmo_time_value)
@router.message(Form.rmo_time_value)
async def rmo_time_value(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Faqat son kiriting")
        return

    data = await state.get_data()
    formatted = format_time(int(msg.text), data["rmo_time_unit"])

    await state.update_data(rmo_time=formatted)

    lang = data.get("lang", "uz")
    text = (
        "📄 Hujjat yozilgan sanani kiriting:"
        if lang == "uz"
        else "📄 Введите дату документа:"
    )
    await msg.answer(text)
    await state.set_state(Form.rmo_date)
@router.message(Form.rmo_date)
async def rmo_finish(msg: Message, state: FSMContext):
    await state.update_data(rmo_date=msg.text)
    data = await state.get_data()

    lang = data.get("lang", "uz")
    template = (
        TEMPLATES["rmo_uz"]
        if lang == "uz"
        else TEMPLATES["rmo_ru"]
    )

    if not os.path.exists(template):
        await msg.answer("❌ RMO shablon topilmadi")
        await state.clear()
        return

    doc = Document(template)

    replace_map = {
        "(FISH)": data["name"],
        "(kun k)": data["rmo_day"],
        "(minut)": data["rmo_time"],   # 00:05 / 05:00
        "(sana5)": data["rmo_date"],
    }

    # TEXT ALMASHTIRISH
    for p in doc.paragraphs:
        for k, v in replace_map.items():
            if k in p.text:
                for r in p.runs:
                    r.text = r.text.replace(k, v)

    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for k, v in replace_map.items():
                        if k in p.text:
                            for r in p.runs:
                                r.text = r.text.replace(k, v)

    out_path = os.path.join(OUT_DIR, f"RMO_{msg.from_user.id}.docx")
    doc.save(out_path)

    await msg.answer_document(
        FSInputFile(out_path),
        caption="✅ RMO hujjat tayyor \n\n📝 Imzo qo'ysez bo'ldi!"
    )

    await state.clear()


@router.message(F.text.regexp(r"4\. (Kechga qolish|Опоздание)"))
async def late_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "📋 Kechga qolish bo'limi\n\nFamilia Ismi Sharifni kiriting:" if lang == "uz" else "📋 Раздел опоздания\n\nВведите ФИО:"
    await msg.answer(text)
    await state.set_state(LateForm.fish)

@router.message(F.text.regexp(r"5\. (Tushuntirish xati|Пояснительная записка)"))
async def explanation_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "📋 Tushuntirish xati bo'limi\n\nFamilia Ismi Sharifni kiriting:" if lang == "uz" else "📋 Раздел пояснительной записки\n\nВведите ФИО:"
    await msg.answer(text)
    await state.set_state(ExplanationForm.fish)

# ===== RMO STATES =====
class RMOForm(StatesGroup):
    fish = State()
    kun = State()
    vaqt_turi = State()
    vaqt_son = State()
    sana = State()

# ===== RMO START =====
@router.message(F.text.regexp(r"3\. (RMO|РМО)"))
async def rmo_start(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (
        "📄 RMO bo‘limi\n\nF.I.SH kiriting:"
        if lang == "uz"
        else "📄 Раздел РМО\n\nВведите ФИО:"
    )
    await msg.answer(text)
    await state.set_state(RMOForm.fish)

@router.message(RMOForm.fish)
async def rmo_fish(msg: Message, state: FSMContext):
    await state.update_data(fish=msg.text)
    await msg.answer("📅 RMO yoqilmagan kunni kiriting:")
    await state.set_state(RMOForm.kun)

@router.message(RMOForm.kun)
async def rmo_kun(msg: Message, state: FSMContext):
    await state.update_data(kun=msg.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏱ Minut"), KeyboardButton(text="⏱ Soat")]],
        resize_keyboard=True
    )
    await msg.answer("⏰ Qancha vaqt?", reply_markup=kb)
    await state.set_state(RMOForm.vaqt_turi)

@router.message(RMOForm.vaqt_turi)
async def rmo_vaqt_turi(msg: Message, state: FSMContext):
    if msg.text not in ["⏱ Minut", "🕐 Soat"]:
        await msg.answer("❌ Tugmalardan birini tanlang.")
        return

    await state.update_data(vaqt_turi=msg.text)
    await msg.answer("🔢 Son kiriting (masalan: 5):")
    await state.set_state(RMOForm.vaqt_son)

@router.message(RMOForm.vaqt_son)
async def rmo_vaqt_son(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Faqat son kiriting.")
        return

    data = await state.get_data()
    son = int(msg.text)

    if "Minut" in data["vaqt_turi"]:
        vaqt = f"00:{son:02d}"
    else:
        vaqt = f"{son:02d}:00"

    await state.update_data(minut=vaqt)
    await msg.answer("📆 Hujjat yozilgan sana (DD.MM.YYYY):")
    await state.set_state(RMOForm.sana)

@router.message(RMOForm.sana)
async def rmo_finish(msg: Message, state: FSMContext):
    data = await state.get_data()

    template_path = os.path.join(BASE_DIR, "Tushuntirish xati RMO.docx")
    if not os.path.exists(template_path):
        await msg.answer("❌ RMO template topilmadi.")
        await state.clear()
        return

    doc = Document(template_path)

    replace_map = {
        "(FISH)": data.get("fish", ""),
        "(kun k)": data.get("kun", ""),
        "(minut)": data.get("minut", ""),
        "(sana5)": msg.text
    }

    replace_placeholders_in_doc(doc, replace_map)

    filename = f"RMO_{msg.from_user.id}.docx"
    out_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(out_path)

    await msg.answer_document(
        FSInputFile(out_path),
        caption="✅ RMO hujjat tayyor! \n\n📝 Imzo qo'ysez bo'ldi!"
    )

    add_log(msg.from_user.id, msg.from_user.username, "RMO", "Tushuntirish xati RMO.docx")

    await state.clear()
    await show_menu(msg, state)


# ===== MISSING DAYS FORM (Yangi) =====
@router.message(MissingDaysForm.fish)
async def missing_days_fish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(fish=msg.text)
    text = "Kela olmagan sana? (DD.MM.YYYY)" if lang == "uz" else "Дата пропуска? (DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(MissingDaysForm.sana_kel)

@router.message(MissingDaysForm.sana_kel)
async def missing_days_sana_kel(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sana_kel=msg.text)
    text = "Kelmagan sababi?" if lang == "uz" else "Причина пропуска?"
    await msg.answer(text)
    await state.set_state(MissingDaysForm.sabab)

@router.message(MissingDaysForm.sabab)
async def missing_days_sabab(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sabab=msg.text)
    text = "Qachon ishga qaytadi? (DD.MM.YYYY)" if lang == "uz" else "Когда вернётесь на работу? (DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(MissingDaysForm.sana_chiq)

@router.message(MissingDaysForm.sana_chiq)
async def missing_days_sana_chiq(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sana_chiq=msg.text)
    text = "Hujjat yozilgan sana? (DD.MM.YYYY)" if lang == "uz" else "Дата документа? (DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(MissingDaysForm.sana)

@router.message(MissingDaysForm.sana)
async def missing_days_finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    data["sana"] = msg.text

    # Template tanlash
    template_key = "missing_days_uz" if lang == "uz" else "missing_days_ru"
    template_path = TEMPLATES[template_key]

    if not os.path.exists(template_path):
        text = f"❌ Template fayli topilmadi!" if lang == "uz" else f"❌ Файл шаблона не найден!"
        await msg.answer(text)
        await state.clear()
        return

    try:
        doc = Document(template_path)
        replace_map = {
            "(FISH)": data.get("fish", ""),
            "(sana ke)": data.get("sana_kel", ""),
            "(sabab)": data.get("sabab", ""),
            "(sana chiq)": data.get("sana_chiq", ""),
            "(sana)": data.get("sana", ""),
        }

        replace_placeholders_in_doc(doc, replace_map)

        filename = f"missing_days_{msg.from_user.id}_{msg.from_user.username}.docx"
        out_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(out_path)

        caption = "✅ Hujjat tayyor!\n\n📝 Imzo qo'ysez bo'ldi!" if lang == "uz" else "✅ Документ готов!\n\n📝 Подпишите и готово!"
        await msg.answer_document(FSInputFile(out_path), caption=caption)

        # Qo'shimcha xabar
        finish_msg = "✅ Hujjat tayyor!\n\n📝 Imzo qo'ysez bo'ldi!" if lang == "uz" else "✅ Документ готов!\n\n📝 Подпишите и готово!"
        await msg.answer(finish_msg)

        add_log(msg.from_user.id, msg.from_user.username, "missing_days", template_key)
        logger.info(f"Generated: {filename}")
    except Exception as e:
        text = f"❌ Xato: {str(e)}" if lang == "uz" else f"❌ Ошибка: {str(e)}"
        await msg.answer(text)
        logger.error(f"Error in missing_days: {e}")

    await state.clear()
    await show_menu(msg, state)

# ===== RESPONSE FORM =====
@router.message(ResponseForm.fish)
async def response_fish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(fish=msg.text)
    text = "Qachon javob so'rab ketgan? (sana: DD.MM.YYYY)" if lang == "uz" else "Когда запросили ответ? (дата: DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(ResponseForm.sana_k)

@router.message(ResponseForm.sana_k)
async def response_sana_k(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sana_k=msg.text)
    text = "Soat nechida? (00:00)" if lang == "uz" else "Во сколько? (00:00)"
    await msg.answer(text)
    await state.set_state(ResponseForm.soat)

@router.message(ResponseForm.soat)
async def response_soat(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(soat=msg.text)
    text = "Qoldirgan soat nechida? (00:00)" if lang == "uz" else "Оставленный час? (00:00)"
    await msg.answer(text)
    await state.set_state(ResponseForm.soat_i)

@router.message(ResponseForm.soat_i)
async def response_soat_i(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(soat_i=msg.text)
    text = "Qachon ishlab berasiz? (sana: DD.MM.YYYY)" if lang == "uz" else "Когда вернётесь на работу? (дата: DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(ResponseForm.sana_ch)

@router.message(ResponseForm.sana_ch)
async def response_sana_ch(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sana_ch=msg.text)
    text = "Hujjat yozilgan sana? (sana: DD.MM.YYYY)" if lang == "uz" else "Дата документа? (дата: DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(ResponseForm.sana1)

@router.message(ResponseForm.sana1)
async def response_finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    data["sana1"] = msg.text

    template_key = "response_uz" if lang == "uz" else "response_ru"
    template_path = TEMPLATES[template_key]
    if not os.path.exists(template_path):
        text = f"❌ Template fayli topilmadi!" if lang == "uz" else f"❌ Файл шаблона не найден!"
        await msg.answer(text)
        await state.clear()
        return

    try:
        doc = Document(template_path)
        replace_map = {
            "(FISH)": data.get("fish", ""),
            "(sana k)": data.get("sana_k", ""),
            "(soat)": data.get("soat", ""),
            "(soat i)": data.get("soat_i", ""),
            "(sana ch)": data.get("sana_ch", ""),
            "(sana1)": data.get("sana1", ""),
        }

        replace_placeholders_in_doc(doc, replace_map)

        filename = f"response_{msg.from_user.id}_{msg.from_user.username}.docx"
        out_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(out_path)

        caption = "✅ Hujjat tayyor!" if lang == "uz" else "✅ Документ готов!"
        await msg.answer_document(FSInputFile(out_path), caption=caption)

        # Qo'shimcha xabar
        finish_msg = "✅ Hujjat tayyor!\n\n📝 Imzo qo'ysez bo'ldi!" if lang == "uz" else "✅ Документ готов!\n\n📝 Подпишите и готово!"
        await msg.answer(finish_msg)

        add_log(msg.from_user.id, msg.from_user.username, "response", template_key)
        logger.info(f"Generated: {filename}")
    except Exception as e:
        text = f"❌ Xato: {str(e)}" if lang == "uz" else f"❌ Ошибка: {str(e)}"
        await msg.answer(text)
        logger.error(f"Error in response: {e}")

    await state.clear()
    await show_menu(msg, state)

# ===== LATE FORM =====
@router.message(LateForm.fish)
async def late_fish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(fish=msg.text)
    text = "Kech qolgan sababi?" if lang == "uz" else "Причина опоздания?"
    await msg.answer(text)
    await state.set_state(LateForm.sabab)

@router.message(LateForm.sabab)
async def late_sabab(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(sabab=msg.text)
    text = "Daqiqa, soat kech qoldingiz? (00:00)" if lang == "uz" else "На сколько минут опоздали? (00:00)"
    await msg.answer(text)
    await state.set_state(LateForm.soat_da)

@router.message(LateForm.soat_da)
async def late_soat_da(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(soat_da=msg.text)
    text = "Hujjat yozilgan sana? (sana: DD.MM.YYYY)" if lang == "uz" else "Дата документа? (дата: DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(LateForm.sana2)

@router.message(LateForm.sana2)
async def late_finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    data["sana2"] = msg.text

    template_key = "late_uz" if lang == "uz" else "late_ru"
    template_path = TEMPLATES[template_key]
    if not os.path.exists(template_path):
        text = f"❌ Template fayli topilmadi!" if lang == "uz" else f"❌ Файл шаблона не найден!"
        await msg.answer(text)
        await state.clear()
        return

    try:
        doc = Document(template_path)
        replace_map = {
            "(FISH)": data.get("fish", ""),
            "(sabab)": data.get("sabab", ""),
            "(soat,da)": data.get("soat_da", ""),
            "(sana2)": data.get("sana2", ""),
        }

        replace_placeholders_in_doc(doc, replace_map)

        filename = f"late_{msg.from_user.id}_{msg.from_user.username}.docx"
        out_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(out_path)

        caption = "✅ Hujjat tayyor!" if lang == "uz" else "✅ Документ готов!"
        await msg.answer_document(FSInputFile(out_path), caption=caption)

        # Qo'shimcha xabar
        finish_msg = "✅ Hujjat tayyor!\n\n📝 Imzo qo'ysez bo'ldi!" if lang == "uz" else "✅ Документ готов!\n\n📝 Подпишите и готово!"
        await msg.answer(finish_msg)

        add_log(msg.from_user.id, msg.from_user.username, "late", template_key)
        logger.info(f"Generated: {filename}")
    except Exception as e:
        text = f"❌ Xato: {str(e)}" if lang == "uz" else f"❌ Ошибка: {str(e)}"
        await msg.answer(text)
        logger.error(f"Error in late: {e}")

    await state.clear()
    await show_menu(msg, state)

# ===== EXPLANATION FORM =====
@router.message(ExplanationForm.fish)
async def explanation_fish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(fish=msg.text)
    text = "Tushuntirish xati yozishni kiriting:" if lang == "uz" else "Введите пояснительную записку:"
    await msg.answer(text)
    await state.set_state(ExplanationForm.tx)

@router.message(ExplanationForm.tx)
async def explanation_tx(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(tx=msg.text)
    text = "Hujjat yozilgan sana? (sana: DD.MM.YYYY)" if lang == "uz" else "Дата документа? (дата: DD.MM.YYYY)"
    await msg.answer(text)
    await state.set_state(ExplanationForm.sana3)

@router.message(ExplanationForm.sana3)
async def explanation_finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    data["sana3"] = msg.text

    template_path = TEMPLATES["explanation"]
    if not os.path.exists(template_path):
        text = f"❌ Template fayli topilmadi!" if lang == "uz" else f"❌ Файл шаблона не найден!"
        await msg.answer(text)
        await state.clear()
        return

    try:
        doc = Document(template_path)
        replace_map = {
            "(FISH)": data.get("fish", ""),
            "(T.X)": data.get("tx", ""),
            "(sana3)": data.get("sana3", ""),
        }

        replace_placeholders_in_doc(doc, replace_map)

        filename = f"explanation_{msg.from_user.id}_{msg.from_user.username}.docx"
        out_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(out_path)

        caption = "✅ Hujjat tayyor!" if lang == "uz" else "✅ Документ готов!"
        await msg.answer_document(FSInputFile(out_path), caption=caption)

        # Qo'shimcha xabar
        finish_msg = "✅ Hujjat tayyor!\n\n📝 Imzo qo'ysez bo'ldi!" if lang == "uz" else "✅ Документ готов!\n\n📝 Подпишите и готово!"
        await msg.answer(finish_msg)

        add_log(msg.from_user.id, msg.from_user.username, "explanation", "Tushuntirish xati2026.docx")
        logger.info(f"Generated: {filename}")
    except Exception as e:
        text = f"❌ Xato: {str(e)}" if lang == "uz" else f"❌ Ошибка: {str(e)}"
        await msg.answer(text)
        logger.error(f"Error in explanation: {e}")

    await state.clear()
    await show_menu(msg, state)

# ===== ADMIN PANEL =====
@router.message(F.text.regexp(r"🛠 (Admin Panel|Админ панель)"))
async def admin_panel(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("❌ Bu funksiya faqat admin uchun.")
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")

    keyboard = [
        [KeyboardButton(text="➕ Foydalanuvchi qo'shish" if lang == "uz" else "➕ Добавить пользователя")],
        [KeyboardButton(text="❌ Foydalanuvchi o'chirish" if lang == "uz" else "❌ Удалить пользователя")],
        [KeyboardButton(text="📊 Loglar" if lang == "uz" else "📊 Логи")],
        [KeyboardButton(text="↩️ Orqaga" if lang == "uz" else "↩️ Назад")]
    ]

    title = "🛠 Admin Panel" if lang == "uz" else "🛠 Админ панель"
    await msg.answer(title, reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))

@router.message(F.text.regexp(r"➕ (Foydalanuvchi qo'shish|Добавить пользователя)"))
async def add_user_start(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "Yangi login kiriting:" if lang == "uz" else "Введите новый логин:"
    await msg.answer(text)
    await state.set_state(AdminAddUser.login)

@router.message(AdminAddUser.login)
async def add_user_login(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(login=msg.text)
    text = "Parol kiriting:" if lang == "uz" else "Введите пароль:"
    await msg.answer(text)
    await state.set_state(AdminAddUser.password)

@router.message(AdminAddUser.password)
async def add_user_password(msg: Message, state: FSMContext):
    data = await state.get_data()
    login = data["login"]
    password = msg.text
    lang = data.get("lang", "uz")

    if add_user(login, password):
        text = f"✅ Foydalanuvchi '{login}' muvaffaqiyatli qo'shildi." if lang == "uz" else f"✅ Пользователь '{login}' успешно добавлен."
        await msg.answer(text)
        add_log(msg.from_user.id, msg.from_user.username, "add_user", login)
    else:
        text = f"❌ Foydalanuvchi '{login}' allaqachon mavjud." if lang == "uz" else f"❌ Пользователь '{login}' уже существует."
        await msg.answer(text)

    await state.clear()

@router.message(F.text.regexp(r"❌ (Foydalanuvchi o'chirish|Удалить пользователя)"))
async def delete_user_start(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = "O'chiriladigan login:" if lang == "uz" else "Введите логин для удаления:"
    await msg.answer(text)
    await state.set_state(AdminDeleteUser.login)

@router.message(AdminDeleteUser.login)
async def delete_user_login(msg: Message, state: FSMContext):
    login = msg.text
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if delete_user(login):
        text = f"✅ Foydalanuvchi '{login}' o'chirildi." if lang == "uz" else f"✅ Пользователь '{login}' удалён."
        await msg.answer(text)
        add_log(msg.from_user.id, msg.from_user.username, "delete_user", login)
    else:
        text = f"❌ Foydalanuvchi '{login}' topilmadi." if lang == "uz" else f"❌ Пользователь '{login}' не найден."
        await msg.answer(text)

    await state.clear()

@router.message(F.text.regexp(r"📊 (Loglar|Логи)"))
async def show_logs(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")

    if not os.path.exists(LOGS_FILE):
        text = "📊 Loglar bo'sh." if lang == "uz" else "📊 Логи пусты."
        await msg.answer(text)
        return

    with open(LOGS_FILE, "r") as f:
        logs = json.load(f)

    logs_text = ("📊 Bot Loglar:\n\n" if lang == "uz" else "📊 Логи бота:\n\n")
    for log in logs[-20:]:
        logs_text += f"🕐 {log['timestamp']}\n👤 {log['username']} (ID: {log['user_id']})\n📝 {log['action']}\n📄 {log['template']}\n\n"

    await msg.answer(logs_text)

@router.message(F.text.regexp(r"↩️ (Orqaga|Назад)"))
async def back_to_menu(msg: Message, state: FSMContext):
    data = await state.get_data()
    # Lang va username saqlab qolamiz, qolgan state'ni o'chiramiz
    lang = data.get("lang", "uz")
    username = data.get("username", "User")
    await state.clear()
    await state.update_data(lang=lang, username=username)
    await show_menu(msg, state)

# ===== MAIN =====
async def main():
    init_users_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
