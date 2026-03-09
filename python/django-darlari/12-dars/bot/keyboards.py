from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from translations import t

def kb_lang(lang: str = "uz"):
    """Tilni tanlang — 3 til (tarjima)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("lang_name_uz", lang), callback_data="lang_uz")],
        [InlineKeyboardButton(text=t("lang_name_ru", lang), callback_data="lang_ru")],
        [InlineKeyboardButton(text=t("lang_name_en", lang), callback_data="lang_en")],
    ])

def kb_start(lang: str):
    """Start: 2 ta bo'lim — oddiy tugmalar."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_new_post", lang))],
            [KeyboardButton(text=t("btn_blog_history", lang))],
        ],
        resize_keyboard=True,
    )

def kb_new_post_choice(lang: str):
    """Yangi blog yozish bo'limida: 1) Yangi blog 2) Reja."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_new_blog", lang), callback_data="new_blog")],
        [InlineKeyboardButton(text=t("btn_reja", lang), callback_data="reja")],
    ])

def kb_image_choice(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("img_yes", lang), callback_data="img_yes")],
        [InlineKeyboardButton(text=t("img_no", lang), callback_data="img_no")],
    ])


def kb_blog_history_choice(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("blog_today_btn", lang), callback_data="blog_today"),
            InlineKeyboardButton(text=t("blog_all_btn", lang), callback_data="blog_all"),
        ],
    ])

def kb_post_actions_inline(private_url: str, post_id: int, access_token: str, lang: str, edit_url: str = "", delete_callback_data: str | None = None):
    """delete_callback_data berilsa shu ishlatiladi (blog tarixida 64 bayt cheklovi uchun)."""
    cb = delete_callback_data or f"delete_post:{post_id}:{access_token}"
    rows = [
        [
            InlineKeyboardButton(text=t("btn_sayt_ochish", lang), url=private_url),
            InlineKeyboardButton(text=t("blogni_ochirish_btn", lang), callback_data=cb[:64]),
        ],
    ]
    if edit_url and (edit_url.startswith("http://") or edit_url.startswith("https://")):
        rows.append([InlineKeyboardButton(text=t("btn_tahrirlash", lang), url=edit_url[:256])])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_reja_body_done(lang: str):
    """Reja body: bir necha xabar yozib tugagach shu tugmani bosing."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("reja_btn_done", lang), callback_data="reja_body_done")],
    ])


def kb_reja_checkboxes(
    post_id: int,
    access_token: str,
    private_url: str,
    lang: str,
    checked_sarlavha: bool = False,
    checked_body: bool = False,
):
    """Reja: ○ tugma — bosganda ● (yonib) turadi. URL faqat to'g'ri bo'lsa qo'shiladi."""
    s = "● " if checked_sarlavha else "○ "
    b = "● " if checked_body else "○ "
    # URL faqat http(s) bo'lsa "Sayt ochish" ishlaydi (Telegram talabi)
    access_token_str = str(access_token)
    cb_delete = f"delete_post:{post_id}:{access_token_str}"
    rows = [
        [
            InlineKeyboardButton(
                text=s + t("reja_cb_sarlavha", lang),
                callback_data=f"reja_check:{post_id}:sarlavha",
            ),
            InlineKeyboardButton(
                text=b + t("reja_cb_body", lang),
                callback_data=f"reja_check:{post_id}:body",
            ),
        ],
    ]
    if private_url and isinstance(private_url, str) and (private_url.startswith("http://") or private_url.startswith("https://")):
        row2 = [
            InlineKeyboardButton(text=t("btn_sayt_ochish", lang), url=private_url[:256]),
            InlineKeyboardButton(text=t("blogni_ochirish_btn", lang), callback_data=cb_delete),
        ]
        rows.append(row2)
        edit_url = (private_url.split("?")[0].rstrip("/") + "/edit/" + ("?" + private_url.split("?", 1)[1] if "?" in private_url else ""))
        if edit_url.startswith("http"):
            rows.append([InlineKeyboardButton(text=t("btn_tahrirlash", lang), url=edit_url[:256])])
    else:
        rows.append([InlineKeyboardButton(text=t("blogni_ochirish_btn", lang), callback_data=cb_delete)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_post_actions(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("btn_sayt_ochish", lang)),
                KeyboardButton(text=t("btn_blog_ochirish", lang)),
            ],
        ],
        resize_keyboard=True,
    )

def kb_body_continue(lang: str):
    """Body xabarini davom ettirish yoki tugatish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_continue", lang), callback_data="body_continue")],
        [InlineKeyboardButton(text=t("btn_done", lang), callback_data="body_done")],
    ])
