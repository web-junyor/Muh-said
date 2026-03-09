from aiogram.fsm.state import State, StatesGroup

class Auth(StatesGroup):
    lang = State()

class NewPost(StatesGroup):
    type_choice = State()  # Yangi blog yoki Reja tanlash
    title = State()
    body = State()
    body_accumulate = State()
    image_choice = State()
    image_upload = State()

class Reja(StatesGroup):
    title = State()
    body = State()
    image_choice = State()
    image_upload = State()
