import asyncio
import os
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from Testbot import bot
from bata import all_data
from bot_statistics.stat import mongo_select_stat, mongo_select_stat_all_user
from data_base.DBuse import sql_safe_select, sql_safe_update, sql_safe_insert, sql_delete, redis_just_one_write, \
    redis_just_one_read, mongo_select_news, \
    mongo_add_news, mongo_pop_news, mongo_update_news
from day_func import day_count
from export_to_csv.pg_mg import Backup
from filters.isAdmin import IsAdmin, IsSudo, IsKamaga
from handlers.admin_handlers.admin_for_games import admin_home_games, admin_truthgame, admin_gam_tv, admin_mistake_lie, \
    admin_normal_game_start
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard, redct_text, \
    redct_media, redct_games, settings_bot, spam_admin_keyboard
from keyboards.admin_keys import secretrebornkb
from log import logg
from states.admin_states import admin
from utilts import Phoenix

router = Router()


@router.message(IsAdmin(level=['Редактирование', 'Маркетинг']), commands=["admin"])
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вошел в режим администратора")
    await message.answer("Добро пожаловать в режим администрации. Что вам угодно сегодня?",
                         reply_markup=await main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


@router.message(state=admin.home)
async def admin_home_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в меню",
                         reply_markup=await main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


@router.message(IsAdmin(level=['Редактирование', 'Маркетинг']), (F.text.contains('Вернуться в меню администрирования')))
async def menu(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вернулся в главное меню")
    await state.clear()
    await message.answer("Чего изволите теперь?", reply_markup=await main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


"""***************************************CANCEL************************************************"""


@router.message((F.text == 'Отменить изменения'), state=(
        admin.confirm_add_text, admin.confirm_add_media, admin.confirm_edit_text, admin.confirm_edit_media,))
async def reset(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Отменить изменения'")
    stt = await state.get_state()
    print(stt)
    if stt == 'admin:confirm_add_text':
        await state.set_state(admin.add_text)
        await message.answer('Хорошо, отправьте мне текст с правками', reply_markup=middle_admin_keyboard())
    elif stt == 'admin:confirm_add_media':
        await state.set_state(admin.add_media)
        await message.answer('Хорошо, отправьте мне другое медиа', reply_markup=middle_admin_keyboard())
    elif stt == 'admin:confirm_edit_text':
        await state.set_state(admin.edit_media_test)
        await message.answer('Хорошо, отправьте мне медиа, на которое вы хотите заменить старое',
                             reply_markup=middle_admin_keyboard())
    elif stt == 'admin:confirm_edit_media':
        await state.set_state(admin_home.text_edit)
        await message.answer('Хорошо, отправьте мне текст, который заменит старый',
                             reply_markup=middle_admin_keyboard())
    else:
        await state.set_state(admin.home)
        await admin_home_main_menu(message, state)


@router.message((F.text == 'Назад'), state=admin)
async def reset(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Назад'")
    stt = await state.get_state()
    print(stt)
    await state.clear()
    print(stt)
    if stt == 'admin:update_news':
        await state.set_state(admin.spam_menu)
        await message.answer('Выберите интересующий вас пункт меню', reply_markup=await spam_admin_keyboard())
    elif stt == 'admin:add_news':
        await state.set_state(admin.spam_menu)
        await message.answer('Выберите интересующий вас пункт меню', reply_markup=await spam_admin_keyboard())
    elif stt == 'admin:spam_menu':
        await state.set_state(admin.spam_menu)
        await message.answer('Выберите интересующий вас пункт меню', reply_markup=await spam_admin_keyboard())
    elif stt == 'admin:mediais_back':
        await state.set_state(admin.secretreborn)
        await message.answer('Вы все еще в опасном меню', reply_markup=secretrebornkb())
    elif stt in ('admin:mass_media_menu', 'admin:truthgame', 'admin:tv_lie', 'admin:addingMistakeOrLie',
                 'admin:putin_game_lobby', 'admin:putin_game_old_lies', 'admin:normal_game_lobby',
                 'admin:nazi_game_lobby'):
        await admin_home_games(message, state)
    elif 'admin:truthgame_' in stt:
        await admin_truthgame(message, state)
    elif 'admin:tv_lie_' in stt:
        await admin_gam_tv(message, state)
    elif 'MistakeOrLie' in stt:
        await admin_mistake_lie(message, state)
    elif 'normal_game' in stt:
        await admin_normal_game_start(message, state)
    elif 'admin:editors_menu' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    elif 'admin:import_menu' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    elif 'admin:import_csv' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    elif 'media' in str(stt):
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_media())
        await state.set_state(admin.edit_context)
    elif 'text' in str(stt):
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_text())
        await state.set_state(admin.edit_context)
    elif 'games' in str(stt):
        await message.answer("Это меню еще не готово", reply_markup=redct_games())
        await state.set_state(admin.edit_context)
    elif 'bot' in str(stt):
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
        await state.set_state(admin.edit_context)
    else:
        await state.set_state(admin.home)
        await admin_home_main_menu(message, state)


@router.message(IsAdmin(), (F.text == "Выйти"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Выйти'")
    await state.clear()
    await message.answer("Вы покинули уютный режим администрирования.\nУдачи!",
                         reply_markup=types.ReplyKeyboardRemove())


"""***************************************MENU************************************************"""


@router.message(IsAdmin(level=['Редактирование']), ((F.text.contains('текст')) | (F.text.contains('текстом'))),
                state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редактировать текст'")
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_text())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(level=['Редактирование']), ((F.text.contains('медиа'))), state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редактировать медиа'")
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_media())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(level=['Редактирование']), ((F.text.contains('игры')) | (F.text.contains('играми'))),
                state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редактировать игры'")
    await message.answer("Это меню еще не готово", reply_markup=redct_games())
    await state.set_state(admin.edit_context)


@router.message(IsSudo(), ((F.text.contains('ботом'))), state=admin.menu)
async def suadmin_bot_edit(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Управление ботом'")
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    await state.set_state(admin.edit_context)


"""***************************************ADD_SPAM************************************************"""


@router.message(IsSudo(), (F.text == 'Рассылка'), state=admin.edit_context)
async def sadmins(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Рассылка'")
    await state.clear()
    await message.answer("Тут можно редактировать список новостей для рассылки, создать свою и отключить рассылку",
                         reply_markup=await spam_admin_keyboard())
    await state.set_state(admin.spam_menu)


@router.message(IsSudo(), (F.text == 'Главные новости'), state=admin.spam_menu)
async def sadmins(message: Message, state: FSMContext):
    main_news = await mongo_select_news(coll='main')
    print(main_news)
    if len(main_news) != 0:
        await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Главные новости'")
        await message.answer(f"Все ваши главные новости: ")
        count = 0
        count_for_button = len(main_news)
        for spam in main_news:
            count += 1
            nmarkup = InlineKeyboardBuilder()
            media = spam["media"]
            nmarkup.button(text='Удалить', callback_data=f'del_{media[:47]}_main')
            nmarkup.button(text='Редактировать', callback_data=f'red_{media[:47]}_main')
            if count == count_for_button:
                nmarkup.button(text='Добавить новость', callback_data=f'add_main_news')
            nmarkup.adjust(2)
            try:
                await message.answer_photo(photo=media, caption=spam['caption'], reply_markup=nmarkup.as_markup())
            except:
                await message.answer_video(video=media, caption=spam['caption'], reply_markup=nmarkup.as_markup())
            await asyncio.sleep(0.1)
    else:
        nmarkup = InlineKeyboardBuilder()
        nmarkup.button(text='Добавить новость', callback_data='add_main_news')
        await message.answer(
            "Упс.. Мне не удалось найти главные новости. Я добавил кнопочку под сообщением, чтобы вы смогли их добавить!",
            reply_markup=nmarkup.as_markup())


@router.message(IsSudo(), (F.text == 'Актуальные новости'), state=admin.spam_menu)
async def sadmins(message: Message, state: FSMContext):
    actual_news = await mongo_select_news(coll='actu')
    print(actual_news)
    if len(actual_news) != 0:
        await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Главные новости'")
        await message.answer(f"Все ваши актуальные новости: ")
        count = 0
        count_for_button = len(actual_news)
        print(actual_news)
        for spam in actual_news:
            count += 1
            nmarkup = InlineKeyboardBuilder()
            # vote_cb.new(action='up', amount=amount))
            media = spam["media"]
            nmarkup.button(text='Удалить', callback_data=f'del_{media[:47]}_actu')
            nmarkup.button(text='Редактировать', callback_data=f'red_{media[:47]}_actu')
            if count == count_for_button:
                nmarkup.button(text='Добавить новость', callback_data=f'add_actual_news')
            nmarkup.adjust(2)
            print(1)
            try:
                await message.answer_photo(photo=media, caption=spam['caption'],
                                           reply_markup=nmarkup.as_markup())
            except:
                await message.answer_video(video=media, caption=spam['caption'],
                                           reply_markup=nmarkup.as_markup())
            print(2)
            await asyncio.sleep(0.1)
    else:
        nmarkup = InlineKeyboardBuilder()
        nmarkup.button(text='Добавить новость', callback_data='add_actual_news')
        await message.answer(
            "Упс.. Мне не удалось найти aктуальные новости. Я добавил кнопочку под сообщением, чтобы вы смогли их добавить!",
            reply_markup=nmarkup.as_markup())


@router.message(IsSudo(), (F.text == 'Создать рассылку'), state=admin.spam_menu)
async def sadmins(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Создать рассылку'")
    await message.answer("Это меню на данный момент не готово")


@router.message(IsSudo(), (F.text == 'Включить рассылку 🔴'), state=admin.spam_menu)
async def sadmins(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Выключить рассылку'")
    await redis_just_one_write(f'Usrs: admins: spam: status:', '1')
    await message.answer("Запланированная рассылка была включена", reply_markup=await spam_admin_keyboard())


# 1
@router.message(IsSudo(), (F.text == 'Выключить рассылку 🟢'), state=admin.spam_menu)
async def sadmins(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Выключить рассылку'")
    print(213)
    await redis_just_one_write(f'Usrs: admins: spam: status:', '0')
    await message.answer("Запланированная рассылка была отключена", reply_markup=await spam_admin_keyboard())


@router.callback_query(lambda call: call.data == "add_main_news" or call.data == "add_actual_news")
async def add_news(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(coll=str(query.data))
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Назад'))
    if str(query.data) == 'add_main_news':
        await state.set_state(admin.add_news_spam)
        await query.message.answer(
            'Чтобы добавить главную новость'
            ' -- отправьте мне медиафайл'
            ' в одном сообщении и напишите описание', reply_markup=markup.as_markup(resize_keyboard=True)
        )
    elif str(query.data) == 'add_actual_news':
        await state.set_state(admin.add_media_actula_spam)
        await query.message.answer(
            'Чтобы добавить актуальную новость'
            ' -- отправьте мне медиафайл'
            ' в одном сообщении и напишите описание', reply_markup=markup.as_markup(resize_keyboard=True)
        )


@router.callback_query(lambda call: 'del' in call.data)
async def delete_news(query: types.CallbackQuery, state: FSMContext):
    # spam["media"][0]}_aclual
    media_id = str(query.data[4:-5])
    coll = query.data[-10:]
    await mongo_pop_news(media_id, coll=coll)
    await query.message.delete()
    await state.set_state(admin.spam_menu)
    await query.message.answer("Вы удалили новость", reply_markup=await spam_admin_keyboard())


@router.callback_query(lambda call: 'red' in call.data)
async def update(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(media_id=str(query.data[4:-5]))
    await state.update_data(coll=str(query.data[-10:]))
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Назад'))
    await state.set_state(admin.update_news)
    await query.message.answer("Отправьте мне новое медиа с описанием взамен старому",
                               reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(state=admin.update_news)
async def update_news(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data['media_id'])
    print(data['coll'])
    caption = message.html_text
    if message.content_type == 'photo':
        id = message.photo[0].file_id
        await mongo_update_news(m_id=data['media_id'], new_m_id=id, new_caption=caption, coll=data['coll'])
        await state.set_state(admin.spam_menu)
        await message.answer("Вы успешно изменили новость", reply_markup=await spam_admin_keyboard())
    elif message.content_type == 'video':
        id = message.video.file_id
        await mongo_update_news(m_id=data['media_id'], new_m_id=id, new_caption=caption, coll=data['coll'])
        await state.set_state(admin.spam_menu)
        await message.answer("Вы успешно изменили новость", reply_markup=await spam_admin_keyboard())
    else:
        await message.answer("Упс.. Кажется вы отправили не медиа, пожалуйста повторите попытку")


@router.message(state=admin.add_media_actula_spam)
async def add_news(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.content_type == 'photo':
        id = message.photo[0].file_id
        await state.update_data(media_id=id)
        await state.update_data(media_caption=message.html_text)
        await state.set_state(admin.add_date_for_spam)
        await message.answer("Напишите дату, на которую хотите запланировать рассылку в формате: YYYY.MM.DD")
    elif message.content_type == 'video':
        id = message.video.file_id
        await state.update_data(media_id=id)
        await state.update_data(media_caption=message.html_text)
        await state.set_state(admin.add_date_for_spam)
        await message.answer("Напишите дату, на которую хотите запланировать рассылку в формате: YYYY.MM.DD")
    else:
        await message.answer("Упс.. Кажется вы отправили не медиа, пожалуйста повторите попытку")


@router.message(state=admin.add_date_for_spam)
async def add_news(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%Y.%m.%d')
        await state.update_data(plan_data=message.text)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="1️⃣1️⃣:0️⃣0️⃣"))
        nmarkup.row(types.KeyboardButton(text="1️⃣9️⃣:0️⃣0️⃣"))
        nmarkup.adjust(2)
        await state.set_state(admin.add_time_for_spam)
        await message.answer("Выберите время для рассылки", reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except ValueError:
        await message.answer("Упс.. Кажется вы указали неверный формат даты, пожалуйста повторите попытку")


@router.message(state=admin.add_time_for_spam)
async def add_news(message: Message, state: FSMContext):
    data = await state.get_data()
    coll = data['coll']
    date = data['plan_data']
    media_id = data['media_id']
    caption = data['media_caption']
    if message.text == '1️⃣1️⃣:0️⃣0️⃣':
        time = '11:00'
        dt_for_spam = date + ' ' + time
        date = datetime.strptime(dt_for_spam, '%Y.%m.%d %H:%M')
        await mongo_add_news(media_id, str(caption), date, coll=str(coll))
        coll = data['coll']
        nmarkup = InlineKeyboardBuilder()
        nmarkup.button(text='Добавить новость', callback_data=str(coll))
        await message.answer("Новость запланирована", reply_markup=await spam_admin_keyboard())
        await message.answer("Хотите добавить еще?", reply_markup=nmarkup.as_markup())
    elif message.text == '1️⃣9️⃣:0️⃣0️⃣':
        time = '19:00'
        dt_for_spam = date + ' ' + time
        date = datetime.strptime(dt_for_spam, '%Y.%m.%d %H:%M')
        await mongo_add_news(media_id, str(caption), date, coll=str(coll))
        coll = data['coll']
        nmarkup = InlineKeyboardBuilder()
        nmarkup.button(text='Добавить новость', callback_data=str(coll))
        await message.answer("Новость запланирована", reply_markup=await spam_admin_keyboard())
        await message.answer("Хотите добавить еще?", reply_markup=nmarkup.as_markup())
    else:
        await message.answer("Ошибка, вы указали неверный формат даты, пожулуйста повторите попытку")


@router.message(state=admin.add_news_spam)
async def add_news(message: Message, state: FSMContext):
    data = await state.get_data()
    coll = data['coll']
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='Добавить новость', callback_data=str(coll))
    if message.content_type == 'photo':
        id = message.photo[0].file_id
        await mongo_add_news(id, str(message.html_text), coll=str(coll))
        await state.set_state(admin.spam_menu)
        await message.answer("Новость добавлена", reply_markup=await spam_admin_keyboard())
        await message.answer('Хотите добавить еще одну?', reply_markup=nmarkup.as_markup())
    elif message.content_type == 'video':
        id = message.video.file_id
        await mongo_add_news(id, str(message.html_text), coll=str(coll))
        await state.set_state(admin.spam_menu)

        await message.answer("Новость добавлена", reply_markup=await spam_admin_keyboard())
        await message.answer('Хотите добавить еще одну?', reply_markup=nmarkup.as_markup())
    else:
        await message.answer("Упс.. Кажется вы отправили не медиа, пожалуйста повторите попытку")


"""***************************************EDITORS************************************************"""

"""***************************************TEXTS************************************************"""


@router.message(IsAdmin(level=['Редактирование']), (F.text == 'Добавить новый текст'), state=admin.edit_context)
async def text_hello(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Добавить новый текст'")
    await state.set_state(admin.add_text)
    text = await sql_safe_select('text', 'texts', {'name': 'any_unique_readible_tag'})
    text = text
    await message.answer(f'Пришлите сообщение, отделив тег от текста вертикальной чертой'
                         f' и переносом строки. После черты приведен пример:\n'
                         f'-------------------------'
                         f'\n\n{text}', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin.add_text)
async def get_text(message: Message, state: FSMContext):
    try:
        new_name = message.html_text.split("|\n")[0]
        new_text = message.html_text.split("|\n")[1]
        await state.update_data(text=new_text, name=new_name)
        await state.set_state(admin.confirm_add_text)
        await message.answer(f'<b>Тэг текста: </b>{new_name}\n<b>Текст:\n</b>{new_text}', parse_mode="HTML",
                             reply_markup=app_admin_keyboard())
    except:
        await message.answer('Ошибка. Похоже, вы использовали неверный формат текста.\n'
                             'Пожалуйста, прочтите инструкцию.', reply_markup=middle_admin_keyboard())


@router.message(IsAdmin(level=['Редактирование']), (F.text == 'Редактировать текст'), state=admin.edit_context)
async def text_edit_tag(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редактировать текст'")
    await state.set_state(admin.edit_text)
    await message.answer('Пришлите тэг текстового блока, который вы хотите изменить.',
                         reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin.edit_text)
async def text_edit_text_tag(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': message.text})
    if text is not False:
        await message.answer(f'Выбранный вами пост после линии:\n----------------\n{text}', parse_mode="HTML")
        await message.answer('Если это нужный блок, то отправьте мне его новый вариант.',
                             reply_markup=middle_admin_keyboard())
        await state.set_state(admin.edit_text_test)
        await state.update_data(name=message.text)
    else:
        await message.answer(f'Вы ввели некорректный тэг, попробуйте еще раз', parse_mode="HTML")


@router.message(content_types=types.ContentType.TEXT, state=admin.edit_text_test)
async def text_edit_text_test(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f'Проверьте правильность внесенных данных.\n\n\nТэг текста:{data["name"]}\n\nНовый текст:\n{message.html_text}',
        parse_mode="HTML", reply_markup=app_admin_keyboard())
    await state.update_data({"text": message.html_text})
    await state.set_state(admin.confirm_edit_text)


@router.message((F.text == "Отмена"), state=(admin.delete_text, admin.delete_text_test))
async def cancel(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Отмена'")
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_text())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(level=['Редактирование']), (F.text == "Удалить текст"))
async def delete_text_start(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Удалить текст'")
    await state.set_state(admin.delete_text_test)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отмена'))
    await message.answer("Введите теги, которые хотите удалить\n\n"
                         "Формат вводимых данных:\n\n"
                         "tag_1\ntag_2", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(state=admin.delete_text_test)
async def delete_text_test(message: Message, state: FSMContext):
    texts = message.text.split()
    tag_lists = []
    count = 0
    try:
        for text in texts:
            tex = await sql_safe_select('text', 'texts', {'name': text})
            if tex != False:
                tag_lists.append(texts[count])
                await message.answer(f"Тег: {texts[count]}\n\n"
                                     f"Текст:\n\n{tex[:100]}...")
            else:
                await message.answer(f"Не удалось найти тег: {texts[count]}")
            count += 1
        if len(tag_lists) >= 1:
            markup = ReplyKeyboardBuilder()
            markup.row(types.KeyboardButton(text='Удалить'))
            markup.row(types.KeyboardButton(text='Отмена'))
            await state.update_data(tag_lists=tag_lists)
            await state.set_state(admin.delete_text)
            await message.answer("Удалить выбранные теги?", reply_markup=markup.as_markup(resize_keyboard=True))
        else:
            await message.answer("Теги не обнаружены, повторите попытку")
    except:
        await message.answer("Неправильно введены теги")


@router.message((F.text == 'Удалить'), state=admin.delete_text)
async def delete_text(message: Message, state: FSMContext):
    data = await state.get_data()
    for tag in data['tag_lists']:
        await sql_delete('texts', {'name': tag})

    # postgresql_csv_dump('texts')
    await logg.admin_logs(message.from_user.id, message.from_user.username, 'Удалил теги')
    await message.answer("Все выбранные теги были удалены!")


"""***************************************MEDIA************************************************"""


@router.message((F.text == 'Добавить новое медиа'), state=admin.edit_context)
async def text_hello(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Добавить новое медиа'")
    await state.set_state(admin.add_media)
    photo = await sql_safe_select('t_id', 'assets', {'name': 'test_photo_tag'})
    try:
        await message.answer(text='Пришлите фото или видео,'
                                  ' подписав его удобным тегом подобного формата: some_unique_tag',
                             reply_markup=middle_admin_keyboard())
    except TelegramBadRequest:
        await message.answer(
            'Похоже, что картинка, которую показывает бот в качестве примера, для вашего бота не работает.\n'
            'Вы можете заменить ее на свою, воспользовавшись опцией "Изменить медиа" в главном меню, '
            'и указав таг <b>test_photo_tag</b>')


@router.message(content_types='photo', state=admin.add_media)
async def get_photo(message: Message, state: FSMContext):
    ph_id = message.photo[0].file_id
    try:
        capt = message.caption.replace(" ", "_")
        await state.update_data(t_id=ph_id, name=capt)
        await message.answer_photo(ph_id, caption=capt)
        await state.set_state(admin.confirm_add_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')


@router.message(content_types='video', state=admin.add_media)
async def get_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    try:
        capt = message.caption.replace(" ", "_")
        await state.update_data(t_id=vid_id, name=capt)
        await message.answer_video(vid_id, caption=capt)
        await state.set_state(admin.confirm_add_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')


# red video
@router.message(IsAdmin(level=['Редактирование']), (F.text == 'Редактировать медиа'), state=admin.edit_context)
async def media_edit_tag(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Редактировать медиа'")
    await state.set_state(admin.edit_media_test)
    await message.answer('Пришлите тэг медиа, которое вы хотите изменить.', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin.edit_media_test)
async def edit_media(message: Message, state: FSMContext):
    media_id = await sql_safe_select('t_id', 'assets', {'name': message.text})
    if media_id is not False:
        try:
            await message.answer_photo(media_id, caption='Это выбранная вами картинка. Если все верно, отправьте ту, '
                                                         'на которую вы хотите ее заменить',
                                       reply_markup=middle_admin_keyboard())
        except TelegramBadRequest:
            try:
                await message.answer_video(media_id,
                                           caption='Это выбранное вами видео. Если все верно, отправьте то, на которое его надо заменить',
                                           reply_markup=middle_admin_keyboard())
            except TelegramBadRequest:
                await message.answer('Похоже, что медиа, которое вы хотите заменить, предназначалось другому боту, '
                                     'и поэтому я не смогу вам его показать.\n\n'
                                     'Но все в порядке, вы можете отправить мне новое медиа, и мы починим медиа '
                                     'по этому тегу.')
        await state.set_state(admin.edit_media)
        await state.update_data(name=message.text)
    else:
        await message.answer('К сожалению, медиа под этим тэгом нет в базе.\nПопробуйте еще раз.',
                             reply_markup=middle_admin_keyboard())


@router.message(content_types='video', state=admin.edit_media)
async def appr_updated_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    await state.update_data(t_id=vid_id)
    await message.answer_video(vid_id, caption="Вы отправили это видео. Оно заменит старое. Все верно?",
                               reply_markup=app_admin_keyboard())
    await state.set_state(admin.confirm_edit_media)


@router.message(content_types='photo', state=admin.edit_media)
async def updated_video_test(message: Message, state: FSMContext):
    photo_id = message.photo[0].file_id
    await state.update_data(t_id=photo_id)
    await message.answer_photo(photo_id, caption="Вы отправили это фото. Оно заменит старое. Все верно?",
                               reply_markup=app_admin_keyboard())
    await state.set_state(admin.confirm_edit_media)


@router.message(IsAdmin(level=['Редактирование']), (F.text == "Удалить медиа"), state=admin.edit_context)
async def delete_text_start(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Удалить медиа'")
    await state.set_state(admin.delete_media_test)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отмена'))
    await message.answer("Введите теги, которые хотите удалить\n\n"
                         "Формат вводимых данных:\n\n"
                         "tag_1\ntag_2", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text == "Отмена"), state=(admin.delete_media, admin.delete_media_test))
async def cancel(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Отмена'")
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_media())
    await state.set_state(admin.edit_context)


@router.message(state=admin.delete_media_test)
async def delete_text_test(message: Message, state: FSMContext):
    texts = message.text.split()
    tag_lists = []
    count = 0
    try:
        for tag in texts:
            media = await sql_safe_select("t_id", "assets", {"name": tag})
            if media != False:
                tag_lists.append(texts[count])
                try:
                    await message.answer_photo(media)
                except:
                    await message.answer_video(media)
            else:
                await message.answer(f"Не удалось найти тег: {texts[count]}")
            count += 1
        if len(tag_lists) >= 1:
            markup = ReplyKeyboardBuilder()
            markup.row(types.KeyboardButton(text='Удалить'))
            markup.row(types.KeyboardButton(text='Отмена'))
            print(tag_lists)
            await state.update_data(tag_lists=tag_lists)
            await state.set_state(admin.delete_media)
            await message.answer("Удалить выбранные теги?", reply_markup=markup.as_markup(resize_keyboard=True))
        else:
            await message.answer("Теги не обнаружены, повторите попытку")
    except:
        await message.answer("тег не из бота")


@router.message((F.text == 'Удалить'), state=admin.delete_media)
async def delete_text(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Удалить'")
    data = await state.get_data()
    for tag in data['tag_lists']:
        await sql_delete('assets', {'name': tag})

    # postgresql_csv_dump('assets')
    await message.answer("Все выбранные теги были удалены!")


"""***************************************CONFIRM************************************************"""


@router.message((F.text == 'Подтвердить'), state=admin.confirm_edit_media)
async def approve_media_edit(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Подтвердить'")
    data = await state.get_data()
    text = await sql_safe_update('assets', {"t_id": data["t_id"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=redct_media())
        await state.clear()
        await state.set_state(admin.edit_context)
    else:
        await message.answer('Что-то пошло не так. Вы указали тэг?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_edit_text)
async def approve_edit_text(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Подтвердить'")
    data = await state.get_data()
    text = await sql_safe_update('texts', {"text": data["text"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=redct_text())
        await state.clear()
        await state.set_state(admin.edit_context)
    else:
        await message.answer('Что-то пошло не так. Вы не ошиблись в Аке?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_add_media)
async def approve_media(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нажал(a) -- 'Подтвердить' -- Медиа добавлено")
    data = await state.get_data()
    text = await sql_safe_insert('assets', data)
    if text is not False:
        await state.clear()

        await state.set_state(admin.edit_context)
        await message.answer('Медиа добавлено. Еще разок?', reply_markup=redct_media())
    else:
        await message.answer('Не получилось. Может быть, вы указали существующий таг?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_add_text)
async def approve_text(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нажал(a) -- 'Подтвердить' -- Текст добавлен")
    data = await state.get_data()
    r = await sql_safe_insert('texts', data)
    if r != False:
        await state.set_state(admin.edit_context)
        await message.answer('Текст добавлен. Еще разок?', reply_markup=redct_text())
    else:
        await message.answer('Увы, ошибка. Скорее всего, этот таг сущесвует.')


"""***************************************IMPORT************************************************"""


@router.message(IsSudo(), (F.text.contains('Включить тех.')), state="*")
async def send_bot_to_work(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Включить технический режим'")
    await state.clear()
    await state.set_state(admin.edit_context)
    await redis_just_one_write(f'Usrs: admins: state: status:', '1')
    await message.answer("<b>🔴 Бот был отправлен на технические работы.</b>",
                         reply_markup=await settings_bot())


@router.message(IsSudo(), (F.text.contains('Выключить тех.')), state="*")
async def return_bot_from_work(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Выключить технический режим'")
    await state.clear()
    await state.set_state(admin.edit_context)
    await redis_just_one_write(f'Usrs: admins: state: status:', '0')
    await message.answer("<b>🟢 Бот был выведен из технических работ.</b>",
                         reply_markup=await settings_bot())


@router.message(IsSudo(), (F.text.contains('Импорт')), state=admin.edit_context)
async def import_csv(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Импорт'")
    status = await redis_just_one_read('Usrs: admins: state: status:')
    if '1' in status:
        await state.set_state(admin.import_menu)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Выбрать существующий"))
        nmarkup.row(types.KeyboardButton(text="Загрузить файл"))
        nmarkup.row(types.KeyboardButton(text="Назад"))
        await message.answer("Вы можете сделать backup прямо с сервера"
                             " или загрузить файл восстановления самостоятельно",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await message.answer("Вы должны включить технический режим 🔴'")


@router.message(IsSudo(), (F.text.contains('Выбрать существующий')), state=admin.import_menu)
async def import_csv(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Выбрать существующий'")
    status = await redis_just_one_read('Usrs: admins: state: status:')
    if '1' in status:
        await state.set_state(admin.import_csv_from_local)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Назад"))
        await message.answer("Напишите дату бэкапа в формате: year.month.day",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif "0" in status:
        await message.answer("Вы должны включить технический режим 🔴'")


@router.message(state=admin.import_csv_from_local)
async def import_csv(message: types.Message, state: FSMContext):
    path = "export_to_csv/backups"
    # we shall store all the file names in this list
    test_list = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.')
    switch = True
    for i in message.text:
        if i not in test_list:
            switch = False
    if switch == True:
        backlist = []
        date = message.text.replace('.', "-")
        for root, dirs, files in os.walk(path):
            for file in files:
                if date in str(file) and '.zip' in str(file):
                    print(file)
                    # append the file name to the list
                    backlist.append(os.path.join(file))
        if len(backlist) != 0:
            await message.answer(f"Все ваши бэкапы за {message.text}")
        else:
            await message.answer(f"За выбранную дату бэкапы отсутствуют")
        for backup in backlist:
            nmarkup = InlineKeyboardBuilder()
            nmarkup.button(text='Восстановить', callback_data=backup)
            await message.answer(str(backup), reply_markup=nmarkup.as_markup())
    else:
        await message.answer("Вы неправильно ввели дату, повторите попытку")


@router.message(IsSudo(), (F.text.contains('Загрузить файл')), state=admin.import_menu)
async def import_csv(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Загрузить файл'")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Создать копию"))
    nmarkup.row(types.KeyboardButton(text="Назад"))

    await message.answer("Отправьте мне backup архив для восстановления базы\n\n"
                         "Внимание, база будет полностью обновлена, хотите сделать копию текущей базы??",
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.import_csv)


@router.message(state=admin.import_csv)
async def import_csv(message: types.Message, state: FSMContext):
    csv_id = message.document
    file_name = csv_id.file_name
    if 'dump' in file_name.lower():
        backup = Backup()
        await backup.restore_all(name=file_name)
        await state.set_state(admin.edit_context)
        await message.answer("Импорт завершен успешно", reply_markup=await settings_bot())
        await logg.admin_logs(message.from_user.id, message.from_user.username, "Завершил(a) импорт")
    else:
        await message.answer("Неправильное название архива")


@router.callback_query(lambda call: 'DUMP' in call.data)
async def import_csv(query: types.CallbackQuery, state: FSMContext):
    file = query.data
    print(file)
    backup = Backup()
    await backup.restore_all(name=file)
    await state.set_state(admin.edit_context)
    await logg.admin_logs(query.from_user.id, query.from_user.username, "Завершил(a) импорт")
    await query.message.answer("Импорт завершен успешно", reply_markup=await settings_bot())


def count_visual(all_user, count):
    pr = round(int(count) / int(all_user) * 100)
    if pr <= 20:
        return f'<b>{pr}%</b> 🔴'
    elif pr <= 40:
        return f"<b>{pr}%</b> 🟤"
    elif pr <= 60:
        return f"<b>{pr}%</b> 🟠"
    elif pr <= 80:
        return f"<b>{pr}%</b> 🟡"
    elif pr >= 80:
        return f"<b>{pr}%</b> 🟢"


@router.message((F.text == 'Статистика бота'), state=admin.edit_context)
async def statistics(message: Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Нажал(a) -- 'Статистика бота'")
    await state.set_state(admin.edit_context)
    day_unt = await day_count(get_count=True)
    stat = await mongo_select_stat()
    all_user = len(await mongo_select_stat_all_user())
    await message.answer('<b>СТАТИСТИКА БОТА</b>\n'
                         '➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Пользователей за всё время: <b>{all_user}</b>\n'
                         f'Пользователей за 24 часа: <b>{day_unt}</b>\n'
                         f'➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Прошли вступление: {stat["start"]} ({count_visual(all_user, stat["start"])})\n'
                         f'Прошли пропаганду: {stat["antiprop"]} ({count_visual(all_user, stat["antiprop"])})\n'
                         f'Прошли кт.Донбасс: {stat["donbass"]} ({count_visual(all_user, stat["donbass"])})\n'
                         f'Прошли Цели войны: {stat["war_aims"]} ({count_visual(all_user, stat["war_aims"])})\n'
                         f'Прошли Президента: {stat["putin"]} ({count_visual(all_user, stat["putin"])})\n'
                         f'Прошли до   конца: {stat["end"]} ({count_visual(all_user, stat["end"])})')


@router.message(IsSudo(), commands=["reborn"], state=admin.edit_context)
async def reborn_menu(message: Message, state: FSMContext):
    await state.set_state(admin.secretreborn)
    await message.answer(
        '<b>ВНИМАНИЕ! Последствия использования этого режима несут потенциальную угрозу персистентности бота.\n'
        'Убедитесь в том, что вы понимаете, что делаете</b>')
    await asyncio.sleep(2)
    await message.answer('Добро пожаловать в резервную систему восстановления. Здесь вы можете:\n\n'
                         '- Скачать на диск все медиафайлы, у которых в базе есть несломанный telegram_id\n'
                         '- Починить все медиафайлы в базе, взяв их с их директории /resources/media',
                         reply_markup=secretrebornkb())


@router.message((F.text == 'Скачать медиа'), state=admin.secretreborn)
async def secretreborn(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer('Процесс записи медиа запущен. Пожалуйста, ничего не трогайте до его завершения.',
                         reply_markup=ReplyKeyboardRemove())
    await Phoenix.fire(message, bot)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скачать медиа"))
    await message.answer('Процесс записи медиа на диск завершен. \nОни сохранены в директории /resources/media',
                         reply_markup=secretrebornkb())


@router.message((F.text == 'Починить медиа'), state=admin.secretreborn)
async def secretreborn(message: types.Message):
    await message.answer(
        'Процесс починки медиа сейчас будет запущен. Пожалуйста, ничего не пишите боту, пока он не будет завершен\n\n'
        'Также вам нужно будет нажать на значок загрузки каждого видео, чтобы все записалось корректно.',
        reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(5)
    await Phoenix.rebirth(message)
    await message.answer(
        'Процесс восстановления медиа завершен.\nДля ненайденных тегов выведены ошибки. Либо добавьте медиа под этими именами на диск...\n\n'
        '      ...либо просто игнорируйте это, если уверены, что этот тег нигде не используется.',
        reply_markup=secretrebornkb())


@router.message((F.text == 'Получить все медиа'), state=admin.secretreborn)
async def secretreborn(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer('Отправка медиа начата. Ничего не трогайте, пока вам не вернут клавиатуру.',
                         reply_markup=ReplyKeyboardRemove())
    await Phoenix.roost(message, bot)
    await message.answer('Это все медиа из базы, которые удалось отправить. Перешлите их нужному боту.',
                         reply_markup=secretrebornkb())


@router.message((F.text == 'Принять медиа'), state=admin.secretreborn)
async def secretreborn(message: types.Message, bot: Bot, state: FSMContext):
    await state.set_state(admin.mediais_back)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Назад"))
    await message.answer('Отправьте мне все медиа между чертами, полученные в другом боте',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(state=admin.mediais_back)
async def secretreborn2(message: types.Message, bot: Bot, state: FSMContext):
    media_id = str()
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    if media_id:
        if await sql_safe_select('t_id', 'assets', {'name': message.caption}):
            await sql_safe_update('assets', {'t_id': media_id}, {'name': message.caption})
            print(f'Обновлено медиа под тегом {message.caption}')
        else:
            await sql_safe_insert('assets', {'t_id': media_id, 'name': message.caption})
            print(f'Создано новое медиа под тегом {message.caption}')
    else:
        await message.answer('Перешлите мне медиа из другого бота, или нажмите кнопку "Назад".')


@router.message((F.text == 'Вернуться в менее опасное место'), state=admin.secretreborn)
async def secretreborn(message: types.Message, state: FSMContext):
    await suadmin_bot_edit(message, state)


@router.message((F.text == 'Клонировать бота'))
async def clone_bot(message: Message, state: FSMContext):
    await bot.send_message(784006905, "/writesender")

    from data_base.DBuse import data_getter
    counter = 0

    assets = await data_getter('select * from assets')
    print(assets[0][0])
    print(assets[0][1])
    print(assets[1][0])
    print(assets[1][1])
    for media in assets:

        try:
            await bot.send_video(784006905, media[0], caption=media[1])
        except:
            try:
                await bot.send_photo(784006905, media[0], caption=media[1])
            except:
                await bot.send_message(784006905, "ЧТО-ТО НЕ ТАК")

        await asyncio.sleep(1)


@router.message(IsSudo(), (F.text == 'Подготовить бота к клонированию'))
async def clone_bot_1(message: Message, state: FSMContext):
    await bot.send_message(784006905, "/writreciver")
    con = all_data().get_postg()
    # Курсор для выполнения операций с базой данных
    cur = con.cursor()
    con.autocommit = True
    table_name = "new_assets"

    cur.execute(f'''CREATE TABLE IF NOT EXISTS new_assets(
                            "t_id" TEXT NOT NULL,
                            "name" TEXT NOT NULL PRIMARY KEY
                            )''')
    logg.get_info("table assets is created".upper())


@router.message(IsKamaga(), content_types='video')
async def clone_bot_2(message: Message, state: FSMContext):
    video_id = message.video.file_id
    caption = message.caption
    await sql_safe_insert('new_assets', {'t_id': video_id, 'name': caption})
    await message.answer(f"Фото {caption} добавлено в базу данных. Ассет: {video_id}")


@router.message(IsKamaga(), content_types='photo')
async def clone_bot_3(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    caption = message.caption
    await sql_safe_insert('new_assets', {'t_id': photo_id, 'name': caption})
    await message.answer(f"Фото {caption} добавлено в базу данных. Ассет: {photo_id}")
