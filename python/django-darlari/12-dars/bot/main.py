import os
import json
import secrets
import tempfile
import io
import asyncio
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile, ReplyKeyboardRemove, BotCommand
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNetworkError
from PIL import Image

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from states import Auth, NewPost, Reja
from keyboards import (
    kb_lang,
    kb_start,
    kb_new_post_choice,
    kb_image_choice,
    kb_post_actions_inline,
    kb_reja_checkboxes,
    kb_blog_history_choice,
    kb_body_continue,
)
from translations import t, LANGS
from api_client import DjangoApi, ApiError

load_dotenv()

def _check_env():
    """Bot ishga tushishdan oldin kerakli o'zgaruvchilarni tekshiradi."""
    token = os.getenv("BOT_TOKEN")
    base_url = os.getenv("DJANGO_BASE_URL")
    if not token or not token.strip():
        print("❌ XATO: .env faylida BOT_TOKEN yo'q yoki bo'sh. Bot tokenini qo'ying.")
        raise SystemExit(1)
    if not base_url or not base_url.strip():
        print("❌ XATO: .env faylida DJANGO_BASE_URL yo'q. Masalan: http://127.0.0.1:8001")
        raise SystemExit(1)

_check_env()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router_lang = Router()  # Til tanlash — birinchi tekshiriladi

USER_LANG_FILE = Path(__file__).resolve().parent / "user_lang.json"

# Reja checkbox: (chat_id, message_id) -> {sarlavha, body} va post ma'lumotlari
reja_check_state: dict[tuple[int, int], dict[str, bool]] = {}
reja_message_data: dict[tuple[int, int], dict] = {}

# O'chirish tugmasi uchun qisqa kalit (callback_data 64 bayt cheklovi)
delete_cache: dict[str, tuple[int, str]] = {}

def _delete_register(post_id: int, access_token: str) -> str:
    """post_id va token ni cache ga yozadi, qisqa kalit qaytaradi (callback_data 64 bayt dan oshmasin)."""
    key = secrets.token_hex(4)
    delete_cache[key] = (post_id, access_token)
    return key

def _load_user_lang() -> dict[int, str]:
    """Bot ishga tushganda fayldan tilni yuklaydi."""
    if not USER_LANG_FILE.exists():
        return {}
    try:
        with open(USER_LANG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {int(k): v for k, v in data.items() if v in ("uz", "ru", "en")}
    except Exception:
        return {}

def _save_user_lang():
    """user_lang ni faylga yozadi."""
    try:
        with open(USER_LANG_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in user_lang.items()}, f, ensure_ascii=False)
    except Exception:
        pass

user_lang: dict[int, str] = _load_user_lang()
last_post_by_user: dict[int, dict] = {}

api = DjangoApi(
    base_url=os.getenv("DJANGO_BASE_URL"),
    bot_key=os.getenv("DJANGO_BOT_KEY"),
)


def get_lang_and_uid(uid: int) -> tuple[str, int] | None:
    """(til, owner_telegram_id). Til tanlanmagan bo'lsa None."""
    if uid not in user_lang:
        return None
    return (user_lang[uid], uid)

def btn_texts(key: str) -> set:
    return {t(key, lang) for lang in LANGS}


def _save_error_message(exc: Exception, lang: str) -> str:
    """create_post xatosi uchun foydalanuvchiga ko'rsatiladigan matn."""
    if isinstance(exc, ApiError):
        if exc.status_code == 0 or exc.message == "connection":
            return t("save_error_connection", lang)
        if exc.status_code in (401, 403):
            return t("save_error_auth", lang)
        if 400 <= exc.status_code < 500:
            return t("save_error_validation", lang) + (f"\n({exc.message})" if exc.message and exc.message != "connection" else "")
        return t("save_error_server", lang)
    return t("save_error", lang)

def _edit_url(private_url: str) -> str:
    """Saytda postni tahrirlash sahifasi linki (token saqlanadi)."""
    if not private_url:
        return ""
    if "?" in private_url:
        base, q = private_url.split("?", 1)
        return base.rstrip("/") + "/edit/?" + q
    return private_url.rstrip("/") + "/edit/"

# ——— /start: HAR DOIM tilni tanlash (majburiy), keyin bosh menyu ———
def _detect_start_lang(telegram_lang_code: str | None) -> str:
    """Telegram foydalanuvchi tiliga qarab til tanlash matnini qaytarish uchun (uz/ru/en)."""
    if not telegram_lang_code:
        return "uz"
    if telegram_lang_code.startswith("ru"):
        return "ru"
    if telegram_lang_code.startswith("en"):
        return "en"
    return "uz"

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    start_lang = _detect_start_lang(message.from_user.language_code)
    await message.answer(t("choose_lang", start_lang), reply_markup=kb_lang(start_lang))
    await state.set_state(Auth.lang)


# ——— Til tanlash routeri (birinchi tekshiriladi — "tashlanib" ketmaydi) ———
@router_lang.callback_query(F.data.startswith("lang_"))
async def cb_lang(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = cb.data.replace("lang_", "")
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    user_lang[cb.from_user.id] = lang
    _save_user_lang()
    await state.clear()
    await cb.message.answer(t("welcome", lang))
    await cb.message.answer(t("choose_section", lang), reply_markup=kb_start(lang))

@router_lang.message(StateFilter(Auth.lang))
async def on_message_while_choosing_lang(message: Message, state: FSMContext):
    """Til tanlash ekranida har qanday xabar — qayta tilni tanlash (inline tugmalardan biri kerak)."""
    start_lang = _detect_start_lang(message.from_user.language_code)
    await message.answer(t("choose_lang", start_lang), reply_markup=kb_lang(start_lang))

dp.include_router(router_lang)

# ——— Bosh menyu ———
@dp.message(F.text.in_(btn_texts("btn_new_post")))
async def btn_new_post(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    await state.clear()
    await message.answer(t("section_new_post_choice", lang), reply_markup=kb_new_post_choice(lang))
    await state.set_state(NewPost.type_choice)

@dp.callback_query(StateFilter(NewPost.type_choice), F.data == "new_blog")
async def cb_new_blog(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.message.answer(t("enter_title", lang))
    await state.set_state(NewPost.title)

@dp.callback_query(StateFilter(NewPost.type_choice), F.data == "reja")
async def cb_reja(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.message.answer(t("reja_enter_title", lang))
    await state.set_state(Reja.title)

@dp.message(F.text.in_(btn_texts("btn_blog_history")))
async def btn_blog_history(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    await message.answer(t("blog_history_title", lang), reply_markup=kb_blog_history_choice(lang))

@dp.callback_query(F.data == "blog_today")
async def cb_blog_today(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await cb.message.answer(t("press_start_to_choose_lang", _detect_start_lang(cb.from_user.language_code)))
        return
    lang, owner_id = info
    try:
        posts = api.list_posts(owner_telegram_id=owner_id, last_hours=24)
    except Exception:
        await cb.message.answer(t("load_error", lang))
        return
    if not posts:
        await cb.message.answer(t("blog_today_empty", lang))
        return
    await cb.message.answer(t("blog_today_list", lang))
    for post in posts:
        title = post.get("title", "")
        body_short = body_slice_100(post.get("body", ""))
        caption = f"🧾 {title}\n\n📄 {body_short}"
        private_url = post.get("private_url")
        post_id = post.get("id")
        access_token = post.get("access_token")
        if not private_url or post_id is None or not access_token:
            await cb.message.answer(caption)
            continue
        del_cb = "delete_post:" + _delete_register(int(post_id), str(access_token))
        markup = kb_post_actions_inline(private_url, post_id, str(access_token), lang, _edit_url(private_url), delete_callback_data=del_cb)
        image_url = post.get("image_url")
        if image_url and image_url.strip():
            try:
                r = requests.get(image_url, timeout=10)
                r.raise_for_status()
                resized = resize_image_to_210x109(r.content)
                photo = BufferedInputFile(resized, filename="post.jpg")
                await cb.message.answer_photo(photo=photo, caption=caption, reply_markup=markup)
            except Exception:
                await cb.message.answer(caption, reply_markup=markup)
        else:
            await cb.message.answer(caption, reply_markup=markup)

@dp.callback_query(F.data == "blog_all")
async def cb_blog_all(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await cb.message.answer(t("press_start_to_choose_lang", _detect_start_lang(cb.from_user.language_code)))
        return
    lang, owner_id = info
    try:
        posts = api.list_posts(owner_telegram_id=owner_id)
    except Exception:
        await cb.message.answer(t("load_error", lang))
        return
    if not posts:
        await cb.message.answer(t("blog_all_empty", lang), reply_markup=kb_start(lang))
        return
    await cb.message.answer(t("blog_all_list", lang))
    for post in posts:
        title = post.get("title", "")
        body_short = body_slice_100(post.get("body", ""))
        caption = f"🧾 {title}\n\n📄 {body_short}"
        private_url = post.get("private_url")
        post_id = post.get("id")
        access_token = post.get("access_token")
        if not private_url or post_id is None or not access_token:
            await cb.message.answer(caption)
            continue
        del_cb = "delete_post:" + _delete_register(int(post_id), str(access_token))
        markup = kb_post_actions_inline(private_url, post_id, str(access_token), lang, _edit_url(private_url), delete_callback_data=del_cb)
        image_url = post.get("image_url")
        if image_url and image_url.strip():
            try:
                r = requests.get(image_url, timeout=10)
                r.raise_for_status()
                resized = resize_image_to_210x109(r.content)
                photo = BufferedInputFile(resized, filename="post.jpg")
                await cb.message.answer_photo(photo=photo, caption=caption, reply_markup=markup)
            except Exception:
                await cb.message.answer(caption, reply_markup=markup)
        else:
            await cb.message.answer(caption, reply_markup=markup)

@dp.message(F.text.in_(btn_texts("btn_sayt_ochish")))
async def btn_sayt_ochish(message: Message):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        return
    lang, _ = info
    data = last_post_by_user.get(uid)
    if not data:
        await message.answer(t("sayt_ochish_hint", lang))
        return
    await message.answer(f"🔗 {data['private_url']}")

@dp.message(F.text.in_(btn_texts("btn_blog_ochirish")))
async def btn_blog_ochirish(message: Message):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        return
    lang, _ = info
    data = last_post_by_user.get(uid)
    if not data:
        await message.answer(t("delete_no_post", lang))
        return
    try:
        api.delete_post(post_id=data["post_id"], access_token=data["access_token"])
    except Exception:
        await message.answer(t("save_error", lang))
        return
    del last_post_by_user[uid]
    await message.answer(t("delete_ok", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(t("main_menu", lang), reply_markup=kb_start(lang))

def body_first_7_words(text: str) -> str:
    words = text.strip().split()
    return " ".join(words[:7]) if words else ""

def body_slice_100(text: str) -> str:
    """Sayt home.html kabi: body ning birinchi 100 belgisi + ..."""
    s = (text or "").strip()
    if len(s) <= 100:
        return s
    return s[:100] + "..."

def resize_image_to_210x109(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    img = img.resize((210, 109), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf.read()



@dp.message(NewPost.title, F.text)
async def get_title(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    title = message.text.strip()
    if len(title) < 3:
        await message.answer(t("title_short", lang))
        return
    if len(title) > 120:
        await message.answer(t("title_long", lang))
        return
    await state.update_data(title=title)
    await message.answer(t("enter_body", lang))
    await state.set_state(NewPost.body)

@dp.callback_query(NewPost.body_accumulate, F.data == "body_done")
async def cb_body_done(cb: CallbackQuery, state: FSMContext):
    """Tugashini tanlash — barcha qismlarni birlash."""
    uid = cb.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await cb.message.answer(t("press_start_to_choose_lang", _detect_start_lang(cb.from_user.language_code)))
        await cb.answer()
        return
    lang, _ = info

    data = await state.get_data()
    body_parts = data.get("body_parts", [])

    # Barcha qismlarni birlash (newline orqali)
    full_body = "\n\n".join(body_parts)

    if len(full_body) < 10:
        await cb.message.answer(t("body_short", lang))
        return
    if len(full_body) > 4000:
        await cb.message.answer(t("body_long", lang))
        return

    await state.update_data(body=full_body)
    await cb.message.answer(t("add_photo", lang), reply_markup=kb_image_choice(lang))
    await state.set_state(NewPost.image_choice)
    await cb.answer()


@dp.message(NewPost.body, F.text)
async def get_body(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    body = message.text.strip()
    if len(body) < 10:
        await message.answer(t("body_short", lang))
        return
    if len(body) > 4000:
        await message.answer(t("body_long", lang))
        return

    # Tekst kirilgan bo'lsa, bevosita saqlash (single body mode)
    await state.update_data(body=body)
    await message.answer(t("add_photo", lang), reply_markup=kb_image_choice(lang))
    await state.set_state(NewPost.image_choice)


# ——— Reja: sarlavha → body → saqlash, checkbox ———
@dp.message(Reja.title, F.text)
async def reja_get_title(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    title = (message.text or "").strip()
    if len(title) < 3:
        await message.answer(t("title_short", lang))
        return
    if len(title) > 120:
        await message.answer(t("title_long", lang))
        return
    await state.update_data(title=title)
    await message.answer(t("reja_enter_body", lang))
    await state.set_state(Reja.body)

@dp.message(Reja.body, F.text)
async def reja_get_body(message: Message, state: FSMContext):
    """Reja body: bitta xabar to'liq matn, keyin rasm ixtiyoriy."""
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    data = await state.get_data()
    title = data.get("title")
    if not title:
        await message.answer(t("reja_enter_title", lang))
        await state.set_state(Reja.title)
        return
    body = (message.text or "").strip()
    if len(body) < 10:
        await message.answer(t("body_short", lang))
        return
    if len(body) > 4000:
        await message.answer(t("body_long", lang))
        return
    await state.update_data(body=body)
    await message.answer(t("add_photo", lang), reply_markup=kb_image_choice(lang))
    await state.set_state(Reja.image_choice)


@dp.message(Reja.body)
async def reja_body_not_text(message: Message, state: FSMContext):
    """Reja body kutilayotganda matn emas yuborilsa — faqat matn so'ra."""
    uid = message.from_user.id
    lang = user_lang.get(uid, "uz")
    await message.answer(t("reja_enter_body", lang))


@dp.callback_query(StateFilter(Reja.image_choice), F.data == "img_yes")
async def reja_img_yes(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.message.answer(t("send_photo", lang))
    await state.set_state(Reja.image_upload)

@dp.callback_query(StateFilter(Reja.image_choice), F.data == "img_no")
async def reja_img_no(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    uid = cb.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        return
    lang, owner_id = info
    data = await state.get_data()
    title = data.get("title")
    body = data.get("body", "")
    if not title or len(body) < 10:
        await cb.message.answer(t("body_short", lang))
        return
    try:
        post = api.create_post(
            title=title,
            body=body,
            owner_telegram_id=owner_id,
            image_path=None,
            post_type="reja",
        )
    except ApiError as e:
        logger.warning("Reja create_post ApiError: %s", e)
        await cb.message.answer(_save_error_message(e, lang))
        return
    except Exception as e:
        logger.exception("Reja create_post xato: %s", e)
        await cb.message.answer(t("save_error", lang))
        return
    private_url = post.get("private_url", "")
    last_post_by_user[uid] = {"post_id": post["id"], "access_token": str(post["access_token"]), "private_url": private_url}
    sent = await cb.message.answer(
        f"{t('reja_saved', lang)}\n\n○ {t('sarlavha', lang)} {title}\n\n○ Body: {(body[:len(body)//2] + '...') if len(body) > 1 else body}",
        reply_markup=kb_reja_checkboxes(post["id"], str(post["access_token"]), private_url, lang, False, False),
    )
    if sent:
        key = (cb.message.chat.id, sent.message_id)
        reja_message_data[key] = {"post_id": post["id"], "access_token": str(post["access_token"]), "private_url": private_url, "lang": lang}
        reja_check_state[key] = {"sarlavha": False, "body": False}
    await state.clear()

@dp.message(Reja.image_upload, F.photo)
async def reja_get_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, owner_id = info
    data = await state.get_data()
    title = data.get("title")
    body = data.get("body", "")
    if not title or len(body) < 10:
        await message.answer(t("body_short", lang))
        return
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), f"tg_reja_{photo.file_unique_id}.jpg")
    await bot.download_file(file.file_path, destination=tmp_path)
    try:
        post = api.create_post(
            title=title,
            body=body,
            owner_telegram_id=owner_id,
            image_path=tmp_path,
            post_type="reja",
        )
    except ApiError as e:
        logger.warning("Reja create_post ApiError: %s", e)
        await message.answer(_save_error_message(e, lang))
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return
    except Exception as e:
        logger.exception("Reja create_post xato: %s", e)
        await message.answer(t("save_error", lang))
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return
    try:
        os.remove(tmp_path)
    except OSError:
        pass
    last_post_by_user[uid] = {"post_id": post["id"], "access_token": str(post["access_token"]), "private_url": post.get("private_url", "")}
    half = max(1, len(body) // 2)
    body_50 = (body[:half] + "...") if len(body) > half else body
    caption = f"{t('reja_saved', lang)}\n\n○ {t('sarlavha', lang)} {title}\n\n○ Body: {body_50}"
    markup = kb_reja_checkboxes(post["id"], str(post["access_token"]), post.get("private_url", ""), lang, False, False)
    sent = await message.answer_photo(photo=photo.file_id, caption=caption, reply_markup=markup)
    if sent:
        key = (message.chat.id, sent.message_id)
        reja_message_data[key] = {"post_id": post["id"], "access_token": str(post["access_token"]), "private_url": post.get("private_url", ""), "lang": lang}
        reja_check_state[key] = {"sarlavha": False, "body": False}
    await state.clear()


# Body accumulate holatida tekst qo'shish
@dp.message(NewPost.body_accumulate, F.text)
async def get_body_text_accumulate(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, _ = info
    text = message.text.strip()
    if len(text) < 3:
        await message.answer(t("title_short", lang))
        return

    # `body_parts` ga yangi tekst qo'shish
    data = await state.get_data()
    body_parts = data.get("body_parts", [])
    body_parts.append(text)

    # Barcha qismlarni birlash
    full_body = "\n\n".join(body_parts)
    if len(full_body) > 4000:
        await message.answer(t("body_long", lang))
        body_parts.pop()  # Oxirgi qo'shilganini olib tashish
        await state.update_data(body_parts=body_parts)
        return

    preview_text = f"📄 {full_body[:150]}..." if len(full_body) > 150 else f"📄 {full_body}"
    await state.update_data(body_parts=body_parts, body_text_preview=preview_text)
    logger.info(f"User {uid}: Text body part added (total: {len(body_parts)} parts)")
    await message.answer(t("body_part_added", lang), reply_markup=kb_body_continue(lang))


@dp.callback_query(StateFilter(NewPost.image_choice), F.data == "img_yes")
async def img_yes(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.message.answer(t("send_photo", lang))
    await state.set_state(NewPost.image_upload)


@dp.callback_query(StateFilter(NewPost.image_choice), F.data == "img_no")
async def img_no(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    uid = cb.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await cb.message.answer(t("press_start_to_choose_lang", _detect_start_lang(cb.from_user.language_code)))
        return
    lang, owner_id = info
    data = await state.get_data()
    title = data.get("title") or ""
    body = data.get("body") or ""
    if len(title) < 3 or len(body) < 10:
        await cb.message.answer(t("body_short", lang))
        return
    try:
    post = api.create_post(
            title=title,
            body=body,
        owner_telegram_id=owner_id,
        image_path=None,
    )
    except ApiError as e:
        logger.warning("create_post (img_no) ApiError: %s", e)
        await cb.message.answer(_save_error_message(e, lang))
        return
    except Exception as e:
        logger.exception("create_post (img_no): %s", e)
        await cb.message.answer(t("save_error", lang))
        return
    last_post_by_user[uid] = {
        "post_id": post["id"],
        "access_token": str(post["access_token"]),
        "private_url": post.get("private_url", ""),
    }
    preview = f"{t('post_saved', lang)}\n\n{t('sarlavha', lang)} {title}\n\n📄 {body}"
    await cb.message.answer(
        preview,
        reply_markup=kb_post_actions_inline(
            post.get("private_url", ""), post["id"], str(post["access_token"]), lang,
            _edit_url(post.get("private_url", "")),
        ),
    )
    await state.clear()


@dp.message(NewPost.title)
async def get_title_not_text(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = user_lang.get(uid, _detect_start_lang(message.from_user.language_code))
    await message.answer(t("enter_title", lang))

@dp.message(NewPost.body)
async def get_body_not_text(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = user_lang.get(uid, _detect_start_lang(message.from_user.language_code))
    await message.answer(t("enter_body", lang))

@dp.message(NewPost.image_upload, F.photo)
async def get_image(message: Message, state: FSMContext):
    uid = message.from_user.id
    info = get_lang_and_uid(uid)
    if not info:
        await message.answer(t("press_start_to_choose_lang", _detect_start_lang(message.from_user.language_code)))
        return
    lang, owner_id = info
    data = await state.get_data()
    title = data.get("title") or ""
    body = data.get("body") or ""
    if len(title) < 3 or len(body) < 10:
        await message.answer(t("body_short", lang))
        return
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), f"tg_post_{photo.file_unique_id}.jpg")
    await bot.download_file(file.file_path, destination=tmp_path)
    try:
    post = api.create_post(
            title=title,
            body=body,
        owner_telegram_id=owner_id,
        image_path=tmp_path,
    )
    except ApiError as e:
        logger.warning("create_post (image) ApiError: %s", e)
        await message.answer(_save_error_message(e, lang))
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return
    except Exception as e:
        logger.exception("create_post (image): %s", e)
        await message.answer(t("save_error", lang))
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return
    last_post_by_user[uid] = {
        "post_id": post["id"],
        "access_token": str(post["access_token"]),
        "private_url": post.get("private_url", ""),
    }
    caption = f"{t('post_saved', lang)}\n\n{t('sarlavha', lang)} {title}\n\n📄 {body}"
    await message.answer_photo(
        photo=photo.file_id,
        caption=caption,
        reply_markup=kb_post_actions_inline(
            post.get("private_url", ""), post["id"], str(post["access_token"]), lang,
            _edit_url(post.get("private_url", "")),
        ),
    )
    try:
        os.remove(tmp_path)
    except OSError:
        pass
    await state.clear()


@dp.message(NewPost.image_upload)
async def get_image_not_photo(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, _detect_start_lang(message.from_user.language_code))
    await message.answer(t("send_photo", lang))


@dp.callback_query(F.data.startswith("reja_check:"))
async def reja_checkbox_toggle(cb: CallbackQuery):
    """Reja checkbox: bosganda ✅ (yonib) turadi."""
    await cb.answer()
    parts = cb.data.split(":", 2)
    if len(parts) != 3:
        return
    _, post_id_str, field = parts
    if field not in ("sarlavha", "body"):
        return
    key = (cb.message.chat.id, cb.message.message_id)
    data = reja_message_data.get(key)
    if not data:
        return
    state = reja_check_state.get(key, {"sarlavha": False, "body": False})
    state[field] = not state[field]
    reja_check_state[key] = state
    lang = data.get("lang", "uz")
    markup = kb_reja_checkboxes(
        data["post_id"], data["access_token"], data["private_url"], lang,
        checked_sarlavha=state["sarlavha"], checked_body=state["body"],
    )
    try:
        await cb.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@dp.callback_query(F.data.startswith("delete_post:"))
async def delete_post_callback(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    parts = cb.data.split(":", 2)
    post_id = None
    access_token = None
    if len(parts) == 2:
        short_key = parts[1]
        if short_key in delete_cache:
            post_id, access_token = delete_cache.pop(short_key)
    if len(parts) == 3:
        try:
            post_id = int(parts[1])
            access_token = parts[2]
        except ValueError:
            pass
    if post_id is None or not access_token:
        await cb.answer(t("error_delete_post", lang), show_alert=True)
        return
    try:
        api.delete_post(post_id=post_id, access_token=access_token)
    except ApiError as e:
        msg = _save_error_message(e, lang) if e.status_code != 404 else t("error_delete_post", lang)
        await cb.answer(msg, show_alert=True)
        if e.status_code == 404:
            try:
                await cb.message.delete()
            except Exception:
                try:
                    await cb.message.edit_reply_markup(reply_markup=None)
                except Exception:
                    pass
        return
    except Exception as e:
        logger.exception("delete_post: %s", e)
        await cb.answer(t("error_delete_post", lang), show_alert=True)
        return
    chat_id = cb.message.chat.id
    try:
        await cb.message.delete()
    except Exception:
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await bot.send_message(chat_id, t("delete_ok", lang))
    await cb.answer()


async def set_bot_commands():
    """Telegram'da bot komanda'larini register qilish."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Bitta event loopda komandalarni ro'yxatga olish va polling."""
    try:
        await set_bot_commands()
    except (TelegramNetworkError, OSError, Exception) as e:
        logger.warning("Komandalar ro'yxatga olinmadi: %s", e)
        print("⚠️ Telegram serveriga ulanishda xato. Komandalar ro'yxatga olinmadi. Polling boshlanmoqda...")

    try:
        await dp.start_polling(bot)
    except TelegramNetworkError:
        print("\n❌ Telegram ga ulanish imkonsiz (api.telegram.org).")
        print("   • Internet aloqangizni tekshiring")
        print("   • VPN yoqib qayta urinib ko'ring (Telegram bloklangan bo'lishi mumkin)")
        raise
    finally:
        try:
            await bot.session.close()
        except Exception:
            pass


if __name__ == "__main__":
    import asyncio
    logger.info("🤖 BOT STARTING...")
    print("\n🤖 Bot ishga tushmoqda.")
    print("📝 Start: /start | Yangi blog yozish | Bloglar tarixi")
    print()
    asyncio.run(main())
