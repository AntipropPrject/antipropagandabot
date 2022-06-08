from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import random




def filler_kb():
    markup = ReplyKeyboardBuilder()
    filler_answers = ['Договорились', 'Хорошо', 'Понятно']
    btn1 = types.KeyboardButton(text=random.choice(filler_answers))
    markup.add(btn1)
    return markup.as_markup(resize_keyboard=True)
