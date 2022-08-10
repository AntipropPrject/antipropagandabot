from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import mongo_all_admins, mongo_select_info, mongo_add_admin, mongo_select_admin_levels, \
    mongo_edit_admin, \
    mongo_pop_admin_level
from filters.isAdmin import IsSudo
from keyboards.admin_keys import redct_editors
from log import logg
from states.admin_states import admin

router = Router()
router.message.filter(state=admin)

access_levels = bata.all_data().access_levels


@router.message((F.text == 'Отменить'), state=(admin.add, admin.pop, admin.editors_menu, admin.add_not))
async def canccel(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Отменить'")
    await state.clear()
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_editors())
    await state.set_state(admin.editors_menu)


@router.message(IsSudo(), (F.text == 'Администраторы'), state=admin.edit_context)
async def sadmins(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редакторы бота'")
    await state.clear()
    await message.answer("Тут можно изменять список редакторов бота", reply_markup=redct_editors())
    await state.set_state(admin.editors_menu)


@router.message(IsSudo(), (F.text == 'Посмотреть администраторов'), state=admin.editors_menu)
async def sadmins_select(message: Message):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Посмотреть редакторов'")
    admins_list = await mongo_all_admins()
    text = ''
    for cool_admin in admins_list:
        name = (await mongo_select_info(cool_admin['_id']))['username']
        levels = "\n - ".join([(str(lvl)) for lvl in cool_admin['access']])
        text = text + f"Пользователь — @{name}\n" \
                      f"ID — <code>{cool_admin['_id']}</code>\n" \
                      f"Уровни доступа:\n<i> - {levels}</i>"
        await message.answer(text)


@router.message(IsSudo(), (F.text == 'Добавить администратора'), state=admin.editors_menu)
async def admins_add(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Добавить редактора'")
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отменить'))
    await message.answer("Напишите id пользователя:", reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(admin.add_not)


@router.message(IsSudo(), state=admin.add_not)
async def admins_add_lvl_choose(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.set_state(admin.add)
        await state.update_data({'new_admin_id': message.text})
        markup = ReplyKeyboardBuilder()
        for i in access_levels:
            markup.row(types.KeyboardButton(text=i))
        markup.adjust(2)
        markup.row(types.KeyboardButton(text='Отменить'))
        await message.answer("Теперь выберите уровень доступа, который вы хотите предоставить этому пользователю:",
                             reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        await message.answer("id пользователя состоит только из цифр. Если вы не знаете, где достать id, обратитесь"
                             "к разработчикам")


@router.message(IsSudo(), F.text.in_(set(access_levels)), state=admin.add)
async def admins_add_lvl_done(message: Message, state: FSMContext):
    new_admin_id = (await state.get_data())['new_admin_id']
    # проверка есть ли человек в общей базе
    if await mongo_select_info(new_admin_id):
        if not await mongo_select_admin_levels(new_admin_id):
            await mongo_add_admin(new_admin_id, message.text)
        else:
            await mongo_edit_admin(new_admin_id, message.text)
        await message.answer(f"Уровень доступа {message.text} добавлен для пользователя {new_admin_id}")
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Новый уровень доступа для'{new_admin_id}': {message.text}")
        await state.clear()
        await sadmins(message, state)
    else:
        await message.answer("Этого пользователя нет в основной таблице; Пусть напишет /start")


@router.message(IsSudo(), (F.text == 'Удалить администратора'), state=admin.editors_menu)
async def admins_pop(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Удалить редактора'")
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отменить'))
    await message.answer("Напишите id пользователя", reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(admin.pop_not)


@router.message(state=admin.pop_not)
async def admins_pop_not(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.set_state(admin.pop)
        await state.update_data({'old_admin_id': message.text})
        levels = await mongo_select_admin_levels(int(message.text))
        if levels:
            markup = ReplyKeyboardBuilder()
            for i in levels:
                markup.row(types.KeyboardButton(text=i))
            markup.adjust(2)
            markup.row(types.KeyboardButton(text='Отменить'))
            await message.answer("Теперь выберите уровень доступа, который вы хотите забрать у этого пользователя:",
                                 reply_markup=markup.as_markup(resize_keyboard=True))
        else:
            await message.answer("Администратора с таким id не найдено, попробуйте снова.")
    else:
        await message.answer("id может содержать только цифры")


@router.message(F.text.in_(set(access_levels)), state=admin.pop)
async def admins_pop(message: Message, state: FSMContext):
    old_admin_id = (await state.get_data())['old_admin_id']
    if await mongo_select_info(old_admin_id):
        await mongo_pop_admin_level(old_admin_id, level=message.text)
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"У пользователя '{old_admin_id}' забран уровень доступа {message.text}")
        await message.answer(f"У пользователя '{old_admin_id}' забран уровень доступа {message.text}",
                             reply_markup=redct_editors())
        await state.clear()
        await sadmins(message, state)
    else:
        await message.answer("Этого пользователя нет в основной таблице; Пусть напишет /start")
