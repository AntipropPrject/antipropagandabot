import random

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from data_base.DBuse import redis_just_one_read, mongo_select_admin_levels


async def main_admin_keyboard(t_id=None):
    usless_list = ('Пожалуйста, не редактируйте текст напрямую в базе данных',
                   'Никогда не угадаешь, где скрывалась опечатка',
                   'Ходят слухи, что где-то в админке спрятаны сокровища...')
    levels = await mongo_select_admin_levels(t_id)
    nmarkup = ReplyKeyboardBuilder()
    if t_id in all_data().super_admins:
        levels = all_data().access_levels
    if levels:
        if 'Редактирование' in levels:
            nmarkup.row(types.KeyboardButton(text="Изменить медиа"))
            nmarkup.row(types.KeyboardButton(text="Изменить текст"))
            nmarkup.row(types.KeyboardButton(text="Игры 🎭"))
        if t_id in all_data().super_admins:
            nmarkup.row(types.KeyboardButton(text="Управление ботом"))
            nmarkup.row(types.KeyboardButton(text="Клонировать бота"))
            nmarkup.row(types.KeyboardButton(text="Подготовить бота к клонированию"))
        if 'Маркетинг' in levels:
            nmarkup.row(types.KeyboardButton(text="Маркетинг 📈"))
        nmarkup.adjust(2)
        nmarkup.row(types.KeyboardButton(text="Выйти"))
    return nmarkup.as_markup(resize_keyboard=True, input_field_placeholder=random.choice(usless_list))


def games_keyboard(t_id=None):
    usless_list = ['Пожалуйста, не редактируйте текст напрямую в базе данных',
                   'Никогда не угадаешь, где скрывалась опечатка']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ложь по тв 📺"))
    nmarkup.row(types.KeyboardButton(text="Ложь других СМИ 🧮"))
    nmarkup.row(types.KeyboardButton(text="Пропагандисты 💢"))
    nmarkup.row(types.KeyboardButton(text="Игра в правду 🥸"))
    nmarkup.row(types.KeyboardButton(text="Путин (Ложь) 🚮"))
    nmarkup.row(types.KeyboardButton(text="Путин (Обещания) 🍜"))
    nmarkup.row(types.KeyboardButton(text="Игра Абсурда 🗯"))
    nmarkup.row(types.KeyboardButton(text="Игра Нацизма 💤"))
    nmarkup.row(types.KeyboardButton(text="Превентивный удар 🐓"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    nmarkup.adjust(2)
    return nmarkup.as_markup(resize_keyboard=True, input_field_placeholder=random.choice(usless_list))


def redct_editors():
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Посмотреть администраторов'))
    markup.row(types.KeyboardButton(text='Добавить администратора'))
    markup.row(types.KeyboardButton(text='Удалить администратора'))
    markup.row(types.KeyboardButton(text='Назад'))
    return markup.as_markup(resize_keyboard=True)


def redct_media():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новое медиа"))
    nmarkup.row(types.KeyboardButton(text="Редактировать медиа"))
    nmarkup.row(types.KeyboardButton(text="Удалить медиа"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    return nmarkup.as_markup(resize_keyboard=True)


def redct_text():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новый текст"))
    nmarkup.row(types.KeyboardButton(text="Редактировать текст"))
    nmarkup.row(types.KeyboardButton(text="Удалить текст"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    return nmarkup.as_markup(resize_keyboard=True)


def game_keys():
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Добавить сюжет"))
    nmrkup.row(types.KeyboardButton(text="Редактировать сюжет"))
    nmrkup.add(types.KeyboardButton(text="Удалить сюжет"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    return nmrkup.as_markup(resize_keyboard=True)


def redct_games():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нужно придумать кнопки"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    return nmarkup.as_markup(resize_keyboard=True)


async def settings_bot():
    try:
        status = await redis_just_one_read('Usrs: admins: state: status:')
    except:
        pass
    print(status)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Администраторы"))
    nmarkup.row(types.KeyboardButton(text="Экспорт"))
    nmarkup.row(types.KeyboardButton(text="Импорт"))
    nmarkup.row(types.KeyboardButton(text="Статистика бота"))
    nmarkup.row(types.KeyboardButton(text="Рассылка"))
    try:
        if '1' in status:
            nmarkup.row(types.KeyboardButton(text="Выключить тех. режим 🟢"))
        else:
            nmarkup.row(types.KeyboardButton(text="Включить тех. режим 🔴"))
    except:
        nmarkup.row(types.KeyboardButton(text="Включить тех. режим 🔴"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
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


async def spam_admin_keyboard():
    try:
        status = await redis_just_one_read('Usrs: admins: spam: status:')
    except:
        pass
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Главные новости"))
    nmarkup.row(types.KeyboardButton(text="Актуальные новости"))
    nmarkup.row(types.KeyboardButton(text="🛑 Массовая рассылка 🛑"))
    try:
        if '1' in status:
            nmarkup.row(types.KeyboardButton(text="Выключить рассылку 🟢"))
        else:
            nmarkup.row(types.KeyboardButton(text="Включить рассылку 🔴"))
    except:
        nmarkup.row(types.KeyboardButton(text="Включить рассылку 🔴"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    return nmarkup.as_markup(resize_keyboard=True)


def red_spam_admin_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить новость"))
    nmarkup.row(types.KeyboardButton(text="Удалить новость"))
    nmarkup.row(types.KeyboardButton(text="Создать рассылку"))
    nmarkup.row(types.KeyboardButton(text="Назад"))
    return nmarkup.as_markup(resize_keyboard=True)


def admin_games_keyboard():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить сюжет"))
    nmarkup.row(types.KeyboardButton(text="Удалить сюжет"))
    nmarkup.row(types.KeyboardButton(text="Редактировать сюжет"))
    nmarkup.row(types.KeyboardButton(text="Назад"))
    return nmarkup.as_markup(resize_keyboard=True)


def secretrebornkb():
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скачать медиа"))
    nmarkup.row(types.KeyboardButton(text="Починить медиа"))
    nmarkup.row(types.KeyboardButton(text="Получить все медиа"))
    nmarkup.row(types.KeyboardButton(text="Принять медиа"))
    nmarkup.adjust(2)
    nmarkup.row(types.KeyboardButton(text="Вернуться в менее опасное место"))
    return nmarkup.as_markup(resize_keyboard=True)
