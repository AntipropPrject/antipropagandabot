from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import random




def antip_why_kb():
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Поговорим про военные действия в Украине"))
    markup.row(types.KeyboardButton(text="Но ведь на войне первая жертва -- это правда. Откуда ты знаешь, кому можно верить? 🤔"))
    return markup.as_markup(resize_keyboard=True)


def antip_killme_kb():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Честно говоря, я в шоке 🤯"))
    nmarkup.row(types.KeyboardButton(text="Сильно удивлен 😧"))
    nmarkup.row(types.KeyboardButton(text="Немного удивлен 😯"))
    nmarkup.row(types.KeyboardButton(text="Не удивлен 😐"))
    nmarkup.row(types.KeyboardButton(text="Я и так знал, что по ТВ врут 🤨"))
    nmarkup.row(types.KeyboardButton(text="Хочу посмотреть еще!"))
    nmarkup.adjust(2,2,1,1)
    return nmarkup.as_markup(resize_keyboard=True)