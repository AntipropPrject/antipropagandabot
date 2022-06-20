import random

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data


def main_admin_keyboard(t_id=None):
    usless_list = ['Пожалуйста, не редактируйте текст напрямую в базе данных',
                   'Никогда не угадаешь, где скрывалась опечатка']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить медиа"))
    nmarkup.row(types.KeyboardButton(text="Изменить медиа"))
    nmarkup.row(types.KeyboardButton(text="Добавить блок текста"))
    nmarkup.row(types.KeyboardButton(text="Отредактировать блок текста"))
    if t_id in all_data().super_admins:
        nmarkup.row(types.KeyboardButton(text="Аналитика"))
        nmarkup.row(types.KeyboardButton(text="Добавить/Удалить редактора"))
    nmarkup.row(types.KeyboardButton(text="Выйти"))
    nmarkup.adjust(2, 2, 1)
    return nmarkup.as_markup(resize_keyboard=True, input_field_placeholder=random.choice(usless_list))

def middle_admin_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню"))
    return nmarkup.as_markup(resize_keyboard=True)

def app_admin_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Отменить"))
    nmarkup.row(types.KeyboardButton(text="Подтвердить"))
    nmarkup.adjust(1, 1)
    return nmarkup.as_markup(resize_keyboard=True)
