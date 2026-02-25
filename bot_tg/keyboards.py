from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(user_data=None):

    keyboard = [
        [KeyboardButton(text="start")],
        [KeyboardButton(text="Новый вопрос"), KeyboardButton(text="Сдаться")],
        [KeyboardButton(text="Мой счёт")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )
