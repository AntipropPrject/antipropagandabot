from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import bata
from data_base.DBuse import mongo_select_admins, mongo_add_admin, \
    mongo_pop_admin, mongo_select_info


router = Router()


class su_admin(StatesGroup):
    add_admin = State()
    pop_admin = State()


@router.message(F.from_user.id.in_(bata.all_data().super_admins), (F.text == 'Добавить/Удалить редактора'))
async def sadmins(message: Message, state: FSMContext):
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Добавить редактора'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Список редакторов'))
    markup.row(types.KeyboardButton(text='Вернуться в меню'))
    await message.answer("Добро пожаловать! Тут можно изменять список редакторов бота", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(F.from_user.id.in_(bata.all_data().super_admins), (F.text == 'Список редакторов'))
async def sadmins_select(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Добавить редактора'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Вернуться в меню'))
    admins_list = await mongo_select_admins()

    lst_id = []
    lst_username = []
    for id in admins_list:

        lst_id.append(id['_id'])
    for username in lst_id:
        x = await mongo_select_info(username)
        lst_username.append(x['username'])
    for i in range(len(lst_id)):
        await message.answer(f"Пользователь - @{lst_username[i]}\n"
                             f"ID - <code>{lst_id[i]}</code>")

@router.message(F.from_user.id.in_(bata.all_data().super_admins), (F.text == 'Добавить редактора'))
async def admins_add(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Напишите id пользователя")
    await state.set_state(su_admin.add_admin)


@router.message(F.from_user.id.in_(bata.all_data().super_admins), state=su_admin.add_admin)
async def admins_add(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Добавить редактора'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Список редакторов'))
    markup.row(types.KeyboardButton(text='Вернуться в меню'))
    # проверка есть ли человек в общей базе
    id_admin = await mongo_select_info(message.text)
    if message.text in str(id_admin):
        await mongo_add_admin(message.text)
        await message.answer("Пользователь добавлен", reply_markup=markup.as_markup(resize_keyboard=True))
        await state.clear()
    else:
        await message.answer("Неправильный id")

@router.message(F.from_user.id.in_(bata.all_data().super_admins), (F.text == 'Удалить редактора'))
async def admins_pop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Напишите id пользователя")
    await state.set_state(su_admin.pop_admin)

@router.message(F.from_user.id.in_(bata.all_data().super_admins), state=su_admin.pop_admin)
async def admins_pop(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Добавить редактора'))
    markup.row(types.KeyboardButton(text='Удалить редактора'))
    markup.row(types.KeyboardButton(text='Список редакторов'))
    markup.row(types.KeyboardButton(text='Вернуться в меню'))
    # проверка есть ли человек в общей базе
    id_admin = await mongo_select_info(message.text)
    if message.text in str(id_admin):
        await mongo_pop_admin(message.text)
        await message.answer("Пользователь удалён", reply_markup=markup.as_markup(resize_keyboard=True))
        await state.clear()
    else:
        await message.answer("Неправильный id пользователя")

