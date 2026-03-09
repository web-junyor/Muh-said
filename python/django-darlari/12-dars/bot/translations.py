# 3 til: uz, ru, en
LANGS = ("uz", "ru", "en")

T = {
    "welcome": {"uz": "Assalomu alaykum! Bizni botimizga kirganingizdan xursandmiz 😊", "ru": "Здравствуйте! Рады видеть вас в нашем боте 😊", "en": "Hello! Welcome to our bot 😊"},
    "choose_lang": {"uz": "Tilni tanlang:", "ru": "Выберите язык:", "en": "Choose language:"},
    "press_start_to_choose_lang": {"uz": "Tilni tanlash uchun /start bosing.", "ru": "Нажмите /start для выбора языка.", "en": "Press /start to choose language."},
    "enter_login": {"uz": "Login kiriting:", "ru": "Введите логин:", "en": "Enter login:"},
    "enter_password": {"uz": "Parol kiriting:", "ru": "Введите пароль:", "en": "Enter password:"},
    "login_fail": {"uz": "Login yoki parol noto'g'ri. Qayta urinib ko'ring.", "ru": "Неверный логин или пароль. Попробуйте снова.", "en": "Invalid login or password. Try again."},
    "choose_section": {"uz": "Quyidagi 2 ta bo'limdan birini tanlang:", "ru": "Выберите один из двух разделов:", "en": "Choose one of the two sections:"},
    "btn_new_post": {"uz": "📝 Yangi blog yozish", "ru": "📝 Написать новый блог", "en": "📝 Write new blog"},
    "section_new_post_choice": {"uz": "Tanlang:", "ru": "Выберите:", "en": "Choose:"},
    "btn_new_blog": {"uz": "📝 Yangi blog yozish", "ru": "📝 Написать блог", "en": "📝 Write blog"},
    "btn_reja": {"uz": "📋 Reja", "ru": "📋 План", "en": "📋 Plan"},
    "reja_enter_title": {"uz": "Reja sarlavhasini yozing:", "ru": "Напишите заголовок плана:", "en": "Type the plan title:"},
    "reja_enter_body": {"uz": "Reja matnini (body) to'liq yozing — istalgan uzunlikda:", "ru": "Напишите текст плана (body) полностью — любой длины:", "en": "Type the full plan text (body) — any length:"},
    "reja_btn_done": {"uz": "✅ Tugadi", "ru": "✅ Готово", "en": "✅ Done"},
    "reja_saved": {"uz": "✅ Reja saqlandi!", "ru": "✅ План сохранён!", "en": "✅ Plan saved!"},
    "reja_cb_sarlavha": {"uz": "Sarlavha", "ru": "Заголовок", "en": "Title"},
    "reja_cb_body": {"uz": "Body", "ru": "Текст", "en": "Body"},
    "btn_blog_history": {"uz": "📚 Bloglar tarixi", "ru": "📚 История блогов", "en": "📚 Blog history"},
    "btn_sayt_ochish": {"uz": "🔗 Sayt ochish", "ru": "🔗 Открыть на сайте", "en": "🔗 Open on site"},
    "btn_blog_ochirish": {"uz": "🗑 Blog o'chirish", "ru": "🗑 Удалить блог", "en": "🗑 Delete blog"},
    # Faqat matn — ovoz so'ralmaydi
    "enter_title": {"uz": "Sarlavhani matn yozing:", "ru": "Напишите заголовок текстом:", "en": "Type the title (text only):"},
    "enter_body": {"uz": "Blog matnini yozing:", "ru": "Напишите текст блога:", "en": "Type the blog text:"},
    "title_short": {"uz": "Title juda qisqa. Kamida 3 ta belgi.", "ru": "Заголовок слишком короткий. Минимум 3 символа.", "en": "Title too short. At least 3 characters."},
    "title_long": {"uz": "Title 120 ta belgidan oshmasin.", "ru": "Заголовок не более 120 символов.", "en": "Title must not exceed 120 characters."},
    "body_short": {"uz": "Body juda qisqa. Kamida 10 ta belgi.", "ru": "Текст слишком короткий. Минимум 10 символов.", "en": "Body too short. At least 10 characters."},
    "body_long": {"uz": "Body 4000 ta belgidan oshmasin.", "ru": "Текст не более 4000 символов.", "en": "Body must not exceed 4000 characters."},
    "add_photo": {"uz": "Rasim qo'shasizmi?", "ru": "Добавить фото?", "en": "Add photo?"},
    "img_yes": {"uz": "📷 Rasm qo'shaman", "ru": "📷 Добавить фото", "en": "📷 Add photo"},
    "img_no": {"uz": "❌ Kiritmaslik", "ru": "❌ Не добавлять", "en": "❌ No"},
    "send_photo": {"uz": "Rasm yuboring (photo).", "ru": "Отправьте фото.", "en": "Send a photo."},
    "post_saved": {"uz": "✅ Mana bu blogni qildingiz!", "ru": "✅ Ваш блог создан!", "en": "✅ Your blog has been created!"},
    "sarlavha": {"uz": "🧾 Sarlavha:", "ru": "🧾 Заголовок:", "en": "🧾 Title:"},
    "save_error": {"uz": "Blog saqlashda xato. Sayt ishlab turganini tekshiring.", "ru": "Ошибка сохранения. Проверьте, что сайт работает.", "en": "Save error. Check that the site is running."},
    "save_error_connection": {"uz": "❌ Saytga ulanish imkonsiz.\n\nDjango ishlayotganini tekshiring:\npython manage.py runserver 8001\n\n.env da DJANGO_BASE_URL = http://127.0.0.1:8001", "ru": "❌ Не удалось подключиться к сайту. Запустите Django (runserver 8001).", "en": "❌ Cannot connect to site. Run Django: python manage.py runserver 8001"},
    "save_error_auth": {"uz": "❌ Bot kaliti noto'g'ri.\n\n.env da DJANGO_BOT_KEY va Django settings.py da BOT_API_KEY bir xil bo'lishi kerak.", "ru": "❌ Неверный ключ бота. Проверьте DJANGO_BOT_KEY и BOT_API_KEY.", "en": "❌ Invalid bot key. Check DJANGO_BOT_KEY and BOT_API_KEY match."},
    "save_error_validation": {"uz": "❌ Ma'lumot xato (sarlavha/body qoidalariga mos emas). Qayta urinib ko'ring.", "ru": "❌ Ошибка данных. Проверьте заголовок и текст.", "en": "❌ Validation error. Check title and body."},
    "save_error_server": {"uz": "❌ Sayt ichki xato (500). Server terminalidagi xabarni tekshiring.", "ru": "❌ Ошибка сервера. Смотрите логи.", "en": "❌ Server error. Check server logs."},
    "blog_history_title": {"uz": "📚 Bloglar tarixi 👇\n\nQuyidagilardan birini tanlang:", "ru": "📚 История блогов 👇\n\nВыберите:", "en": "📚 Blog history 👇\n\nChoose one:"},
    "blog_today_btn": {"uz": "📅 Bugungi Blog", "ru": "📅 Блоги за сегодня", "en": "📅 Today's blogs"},
    "blog_all_btn": {"uz": "📚 Jami Bloglar", "ru": "📚 Все блоги", "en": "📚 All blogs"},
    "blog_today_list": {"uz": "📅 Bugungi Blog — so'nggi 24 soatda qilingan bloglar 👇", "ru": "📅 Блоги за последние 24 часа 👇", "en": "📅 Blogs from the last 24 hours 👇"},
    "blog_today_empty": {"uz": "📅 Bugungi bloglar topilmadi. So'nggi 24 soatda blog yozilmagan.", "ru": "📅 Нет блогов за последние 24 часа.", "en": "📅 No blogs in the last 24 hours."},
    "blog_all_list": {"uz": "📚 Jami Bloglar — sizning barcha bloglaringiz 👇", "ru": "📚 Все ваши блоги 👇", "en": "📚 All your blogs 👇"},
    "blog_all_empty": {"uz": "📚 Sizda hali bloglar yo'q.\n✏️ «Yangi blog yozish» tugmasini bosing.", "ru": "📚 У вас пока нет блогов.\n✏️ Нажмите «Написать блог».", "en": "📚 You have no blogs yet.\n✏️ Press «Write new blog»."},
    "load_error": {"uz": "❌ Bloglarni yuklashda xato. Sayt ishlab turganini tekshiring.", "ru": "❌ Ошибка загрузки. Проверьте сайт.", "en": "❌ Load error. Check the site."},
    "sayt_ochish_hint": {"uz": "Avval blog yarating yoki Bloglar tarixidan birini tanlang.", "ru": "Создайте блог или выберите из истории.", "en": "Create a blog or choose one from history."},
    "delete_no_post": {"uz": "O'chirish uchun blog topilmadi.", "ru": "Блог для удаления не найден.", "en": "No blog to delete."},
    "delete_ok": {"uz": "✅ Blog o'chirildi. Bugungi Blog va Jami Bloglar ro'yxatida ham ko'rinmaydi.", "ru": "✅ Блог удалён. Он больше не отображается в «Сегодня» и «Все блоги».", "en": "✅ Blog deleted. It won't appear in Today's or All blogs."},
    "main_menu": {"uz": "Bosh menyu:", "ru": "Главное меню:", "en": "Main menu:"},
    "blogni_ochirish_btn": {"uz": "🗑 Blogni o'chirish", "ru": "🗑 Удалить блог", "en": "🗑 Delete blog"},
    "btn_tahrirlash": {"uz": "✏️ Tahrirlash", "ru": "✏️ Редактировать", "en": "✏️ Edit"},
    "btn_continue": {"uz": "➕ Yana qo'shish", "ru": "➕ Добавить ещё", "en": "➕ Add more"},
    "btn_done": {"uz": "✅ Tayyorman", "ru": "✅ Готово", "en": "✅ Done"},
    "body_part_added": {"uz": "✅ Qabul qilindi. Yana qo'shasizmi yoki tugatishni xohlaysizmi?", "ru": "✅ Принято. Добавить ещё?", "en": "✅ Received. Add more or finish?"},
    "lang_name_uz": {"uz": "🇺🇿 O'zbekcha", "ru": "🇺🇿 O'zbekcha", "en": "🇺🇿 O'zbekcha"},
    "lang_name_ru": {"uz": "🇷🇺 Ruscha", "ru": "🇷🇺 Русский", "en": "🇷🇺 Russian"},
    "lang_name_en": {"uz": "🇬🇧 Inglizcha", "ru": "🇬🇧 Английский", "en": "🇬🇧 English"},
    "error_generic": {"uz": "❌ Xato.", "ru": "❌ Ошибка.", "en": "❌ Error."},
    "error_delete_post": {"uz": "❌ Blogni o'chirishda xato.", "ru": "❌ Ошибка удаления блога.", "en": "❌ Error deleting blog."},
    "admin_welcome": {
        "uz": "🛡 Assalomu alaykum, administrator!\n\nSiz ushbu botning admin paneli orqali saytni boshqarishingiz mumkin. Quyidagi tugmani bosing — sayt ochiladi.\n\nHurmat bilan, MuhammadSaid.",
        "ru": "🛡 Здравствуйте, администратор!\n\nВы можете управлять сайтом через панель администратора этого бота. Нажмите кнопку ниже — откроется сайт.\n\nС уважением, MuhammadSaid.",
        "en": "🛡 Hello, administrator!\n\nYou can manage the site through this bot's admin panel. Press the button below to open the site.\n\nBest regards, MuhammadSaid.",
    },
    "admin_link_text": {"uz": "Admin saytni ochish", "ru": "Открыть админ-сайт", "en": "Open admin site"},
    "admin_no_access": {"uz": "❌ Bu buyruq faqat administrator uchun.", "ru": "❌ Эта команда только для администратора.", "en": "❌ This command is for administrator only."},
    "said_blog_welcome": {
        "uz": "📌 Salom! Blog saytiga xush kelibsiz. Quyidagi tugma orqali saytga o‘ting.\n\n— MuhammadSaid",
        "ru": "📌 Привет! Добро пожаловать на блог. Перейдите на сайт по кнопке ниже.\n\n— MuhammadSaid",
        "en": "📌 Hi! Welcome to the blog site. Go to the site using the button below.\n\n— MuhammadSaid",
    },
    "said_link_text": {"uz": "🔗 Saytga o'tish", "ru": "🔗 Перейти на сайт", "en": "🔗 Go to site"},
}

def t(key: str, lang: str) -> str:
    # Eski ovoz kalitlari chaqirilsa ham faqat matn so'rov qaytariladi
    if key == "voice_or_text_title":
        key = "enter_title"
    elif key == "voice_or_text_body":
        key = "enter_body"
    if lang not in T.get(key, {}):
        lang = "uz"
    return T.get(key, {}).get(lang, key)
