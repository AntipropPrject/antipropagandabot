from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def filler_kb():
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text='Договорились 👌'))
    return markup.as_markup(resize_keyboard=True)
