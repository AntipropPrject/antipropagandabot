from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import random




def antip_why_kb():
    markup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Поговорим про войну в Украине"))
    nmarkup.row(types.KeyboardButton(text="Но ведь на войне первая жертва -- это правда. Откуда ты знаешь, кому можно верить?"))
    return markup.as_markup(resize_keyboard=True)