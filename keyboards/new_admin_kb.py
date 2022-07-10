import random

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data


def main_admin_keyboard(t_id=None):
    usless_list = ['Пожалуйста, не редактируйте текст напрямую в базе данных',
                   'Никогда не угадаешь, где скрывалась опечатка']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Изменить медиа"))
    nmarkup.row(types.KeyboardButton(text="Изменить текст"))
    nmarkup.row(types.KeyboardButton(text="Добавить позицию к играм"))
    if t_id in all_data().super_admins:
        nmarkup.row(types.KeyboardButton(text="Аналитика"))
        nmarkup.row(types.KeyboardButton(text="Добавить/Удалить редактора"))
    nmarkup.row(types.KeyboardButton(text="Отредактировать блок текста"))
    nmarkup.row(types.KeyboardButton(text="Выйти"))
    nmarkup.adjust(2, 2, 1)
    return nmarkup.as_markup(resize_keyboard=True, input_field_placeholder=random.choice(usless_list))

def redc_editors():
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Посмотреть редакторов'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Список редакторов'))
    markup.row(types.KeyboardButton(text='Назад'))






def redct_media():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новое медиа"))
    nmarkup.row(types.KeyboardButton(text="Редактировать медиа"))
    nmarkup.row(types.KeyboardButton(text="Удалить медиа"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))


def redct_text():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новый текст"))
    nmarkup.row(types.KeyboardButton(text="Редактировать текст"))
    nmarkup.row(types.KeyboardButton(text="Удалить текст"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))

def redct_games():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нужно придумать кнопки"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))



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


def secretrebornkb():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скачать медиа"))
    nmarkup.row(types.KeyboardButton(text="Починить медиа"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в менее опасное место"))
    nmarkup.adjust(2,1)
    return nmarkup.as_markup(resize_keyboard=True)