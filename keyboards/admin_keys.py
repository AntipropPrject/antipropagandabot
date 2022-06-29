import random

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from data_base.DBuse import poll_get, redis_just_one_read


def main_admin_keyboard(t_id=None):
    usless_list = ['Пожалуйста, не редактируйте текст напрямую в базе данных',
                   'Никогда не угадаешь, где скрывалась опечатка']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Изменить медиа"))
    nmarkup.row(types.KeyboardButton(text="Изменить текст"))
    nmarkup.row(types.KeyboardButton(text="Изменить игры"))
    if t_id in all_data().super_admins:
        nmarkup.row(types.KeyboardButton(text="Управление ботом"))
    nmarkup.row(types.KeyboardButton(text="Выйти"))
    nmarkup.adjust(2)
    return nmarkup.as_markup(resize_keyboard=True, input_field_placeholder=random.choice(usless_list))


def redct_editors():
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Посмотреть редакторов'))
    markup.row(types.KeyboardButton(text='Добавить редактора'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Назад'))
    return markup.as_markup(resize_keyboard=True)


def redct_media():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новое медиа"))
    nmarkup.row(types.KeyboardButton(text="Редактировать медиа"))
    nmarkup.row(types.KeyboardButton(text="Удалить медиа"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))
    return nmarkup.as_markup(resize_keyboard=True)


def redct_text():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новый текст"))
    nmarkup.row(types.KeyboardButton(text="Редактировать текст"))
    nmarkup.row(types.KeyboardButton(text="Удалить текст"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))
    return nmarkup.as_markup(resize_keyboard=True)


def redct_games():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нужно придумать кнопки"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))
    return nmarkup.as_markup(resize_keyboard=True)



async def settings_bot():
    try:
        status = await redis_just_one_read('Usrs: admins: state: status:')
    except:
        pass
    print(status)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Редакторы бота"))
    nmarkup.row(types.KeyboardButton(text="Экспорт"))
    nmarkup.row(types.KeyboardButton(text="Импорт"))
    nmarkup.row(types.KeyboardButton(text="Статистика бота"))
    try:
        if '1' in status:
            nmarkup.row(types.KeyboardButton(text="Выключить тех. режим 🟢"))
        else:
            nmarkup.row(types.KeyboardButton(text="Включить тех. режим 🔴"))
    except:
        nmarkup.row(types.KeyboardButton(text="Включить тех. режим 🔴"))
    nmarkup.row(types.KeyboardButton(text="Возврат в главное меню"))
    nmarkup.adjust(1, 2, 1, 1, 1)
    return nmarkup.as_markup(resize_keyboard=True)


def middle_admin_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Назад"))
    return nmarkup.as_markup(resize_keyboard=True)

def app_admin_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Отменить изменения"))
    nmarkup.row(types.KeyboardButton(text="Подтвердить"))
    nmarkup.adjust(1, 1)
    return nmarkup.as_markup(resize_keyboard=True)




