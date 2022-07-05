import asyncio
import csv
import os
import shutil
import zipfile
from asyncio import sleep

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from Testbot import bot
from bata import all_data
from data_base.DBuse import sql_safe_select, sql_safe_update, sql_safe_insert, mongo_select_info, mongo_add_admin, \
    mongo_pop_admin, mongo_select_admins, sql_delete, redis_just_one_write, redis_just_one_read, mongo_select
from day_func import day_count
from export_to_csv.pg_mg import backin
from filters.isAdmin import IsAdmin, IsSudo, isKamaga
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard, redct_text, \
    redct_media, redct_games, settings_bot, redct_editors
from keyboards.new_admin_kb import secretrebornkb
from log import logg
from states.admin_states import admin
from stats.stat import mongo_select_stat, mongo_select_stat_all_user
from utilts import Phoenix

router = Router()


@router.message(IsAdmin(), commands=["admin"])
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в режим администрации. Что вам угодно сегодня?",
                         reply_markup=main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


@router.message(state=admin.home)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в режим администрации. Что вам угодно сегодня?",
                         reply_markup=main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


@router.message(IsAdmin(), (F.text.contains('Возврат в главное меню')))
async def menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Чего изволите теперь?", reply_markup=main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.menu)


"""***************************************CANCEL************************************************"""


@router.message((F.text == 'Отменить изменения'), state=(
        admin.confirm_add_text, admin.confirm_add_media, admin.confirm_edit_text, admin.confirm_edit_media))
async def reset(message: Message, state: FSMContext):
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
        await message.answer('Хорошо, вернемся в меню', reply_markup=main_admin_keyboard(message.from_user.id))


@router.message((F.text == 'Назад'), state="*")
async def reset(message: Message, state: FSMContext):
    stt = await state.get_state()
    print(stt)
    await state.clear()
    print(stt)
    if 'media' in str(stt):
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
    elif 'admin:editors_menu' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    elif 'admin:import_menu' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    elif 'admin:import_csv' in str(stt):
        await state.set_state(admin.edit_context)
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    else:
        await state.set_state(admin.home)
        await message.answer('Хорошо, вернемся в меню', reply_markup=main_admin_keyboard(message.from_user.id))


@router.message(IsAdmin(), (F.text == "Выйти"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы покинули уютный режим администрирования.\nУдачи!",
                         reply_markup=types.ReplyKeyboardRemove())


"""***************************************MENU************************************************"""


@router.message(IsAdmin(), ((F.text.contains('текст')) | (F.text.contains('текстом'))), state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_text())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(), ((F.text.contains('медиа'))), state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_media())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(), ((F.text.contains('игры')) | (F.text.contains('играми'))), state=admin.menu)
async def select_text(message: types.Message, state: FSMContext):
    await message.answer("Это меню еще не готово", reply_markup=redct_games())
    await state.set_state(admin.edit_context)


@router.message(IsSudo(), ((F.text.contains('ботом'))), state=admin.menu)
async def suadmin_bot_edit(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=await settings_bot())
    await state.set_state(admin.edit_context)


"""***************************************EDITORS************************************************"""


@router.message(IsAdmin(), (F.text == 'Отменить'), state='*')
async def sadmins(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_editors())
    await state.set_state(admin.editors_menu)


@router.message(IsSudo(), (F.text == 'Редакторы бота'), state=admin.edit_context)
async def sadmins(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Тут можно изменять список редакторов бота", reply_markup=redct_editors())
    await state.set_state(admin.editors_menu)


@router.message(IsSudo(), (F.text == 'Посмотреть редакторов'), state=admin.editors_menu)
async def sadmins_select(message: Message):
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


@router.message(IsSudo(), (F.text == 'Добавить редактора'), state=admin.editors_menu)
async def admins_add(message: Message, state: FSMContext):
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отменить'))
    await message.answer("Напишите id пользователя", reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(admin.add)


@router.message(IsSudo(), state=admin.add)
async def admins_add(message: Message, state: FSMContext):
    # проверка есть ли человек в общей базе
    id_admin = await mongo_select_info(message.text)
    if message.text in str(id_admin):
        await mongo_add_admin(message.text)
        await message.answer("Пользователь добавлен")
        await state.clear()
    else:
        await message.answer("Неправильный id")


@router.message(IsSudo(), (F.text == 'Удалить редактора'), state=admin.editors_menu)
async def admins_pop(message: Message, state: FSMContext):
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отменить'))
    await message.answer("Напишите id пользователя", reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(admin.pop)


@router.message(IsSudo(), state=admin.pop)
async def admins_pop(message: Message, state: FSMContext):
    # проверка есть ли человек в общей базе
    id_admin = await mongo_select_info(message.text)
    if message.text in str(id_admin):
        await mongo_pop_admin(message.text)
        await message.answer("Пользователь удалён", reply_markup=redct_editors())
        await state.clear()
    else:
        await message.answer("Неправильный id пользователя")


"""***************************************TEXTS************************************************"""


@router.message(IsAdmin(), (F.text == 'Добавить новый текст'), state=admin.edit_context)
async def text_hello(message: types.Message, state: FSMContext):
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


@router.message(IsAdmin(), (F.text == 'Редактировать текст'), state=admin.edit_context)
async def text_edit_tag(message: types.Message, state: FSMContext):
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
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=redct_text())
    await state.set_state(admin.edit_context)


@router.message(IsAdmin(), (F.text == "Удалить текст"))
async def delete_text_start(message: Message, state: FSMContext):
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
    await message.answer("Все выбранные теги были удалены!")


"""***************************************MEDIA************************************************"""


@router.message((F.text == 'Добавить новое медиа'), state=admin.edit_context)
async def text_hello(message: types.Message, state: FSMContext):
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
@router.message(IsAdmin(), (F.text == 'Редактировать медиа'), state=admin.edit_context)
async def media_edit_tag(message: types.Message, state: FSMContext):
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


@router.message(IsAdmin(), (F.text == "Удалить медиа"), state=admin.edit_context)
async def delete_text_start(message: Message, state: FSMContext):
    await state.set_state(admin.delete_media_test)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Отмена'))
    await message.answer("Введите теги, которые хотите удалить\n\n"
                         "Формат вводимых данных:\n\n"
                         "tag_1\ntag_2", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text == "Отмена"), state=(admin.delete_media, admin.delete_media_test))
async def cancel(message: Message, state: FSMContext):
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
    data = await state.get_data()
    for tag in data['tag_lists']:
        await sql_delete('assets', {'name': tag})

    # postgresql_csv_dump('assets')
    await message.answer("Все выбранные теги были удалены!")


"""***************************************CONFIRM************************************************"""


@router.message((F.text == 'Подтвердить'), state=admin.confirm_edit_media)
async def approve_media_edit(message: Message, state: FSMContext):
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
    data = await state.get_data()
    text = await sql_safe_update('texts', {"text": data["text"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=redct_text())
        await state.clear()
        await state.set_state(admin.edit_context)
    else:
        await message.answer('Что-то пошло не так. Вы не ошиблись в разметке?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_add_media)
async def approve_media(message: Message, state: FSMContext):
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
    await state.clear()
    await state.set_state(admin.edit_context)
    await redis_just_one_write(f'Usrs: admins: state: status:', '1')
    await message.answer("<b>🔴 Бот был отправлен на технические работы.</b>",
                         reply_markup=await settings_bot())


@router.message(IsSudo(), (F.text.contains('Выключить тех.')), state="*")
async def return_bot_from_work(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.edit_context)
    await redis_just_one_write(f'Usrs: admins: state: status:', '0')
    await message.answer("<b>🟢 Бот был выведен из технических работ.</b>",
                         reply_markup=await settings_bot())


@router.message(IsSudo(), (F.text.contains('Импорт')), state=admin.edit_context)
async def import_csv(message: types.Message, state: FSMContext):
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
    elif "0" in status:
        await message.answer("Вы должны включить технический режим 🔴'")


@router.message(IsSudo(), (F.text.contains('Выбрать существующий')), state=admin.import_menu)
async def import_csv(message: types.Message, state: FSMContext):
    status = await redis_just_one_read('Usrs: admins: state: status:')
    if '1' in status:
        await state.set_state(admin.import_csv_from_local)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Назад"))
        await message.answer("Напишите дату бэкапа в формате: day:month:year",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif "0" in status:
        await message.answer("Вы должны включить технический режим 🔴'")


@router.message(state=admin.import_csv_from_local)
async def import_csv(message: types.Message, state: FSMContext):
    path = "export_to_csv/backups"
    # we shall store all the file names in this list
    test_list = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':')
    switch = True
    for i in message.text:
        if i not in test_list:
            switch = False
    if switch == True:
        backlist = []
        date = message.text.replace(':', "-")
        print(date)
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
    file = await bot.get_file(csv_id.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"export_to_csv/backin/backin.zip")
    with zipfile.ZipFile("export_to_csv/backin/backin.zip", 'r') as zip_file:
        zip_file.extractall("export_to_csv/backin")

    if 'backup' in file_name.lower():
        await backin()
        await state.set_state(admin.edit_context)
        await message.answer("Импорт завершен успешно", reply_markup=await settings_bot())
    else:
        await message.answer("Неправильное название архива")


@router.callback_query()
async def import_csv(query: types.CallbackQuery, state: FSMContext):
    file = query.data
    with zipfile.ZipFile(f"export_to_csv/backups/{file}", 'r') as zip_file:
        zip_file.extractall("export_to_csv/backin")
    await backin()
    try:
        shutil.rmtree('export_to_csv/backin/export_to_csv')
    except:
        pass
    await state.set_state(admin.edit_context)
    await query.message.answer("Импорт завершен успешно", reply_markup=await settings_bot())


def count_visual(all_user, count):

    pr = round(count / all_user * 100)
    if pr <= 20:
        return f'<b>{pr}%</b> 🔴'
    elif pr <= 40:
        return f"<b>{pr}%</b> 🟤"
    elif pr <= 60:
        return f"<b>{pr}%</b> 🟠"
    elif pr <= 80:
        return f"<b>{pr}%</b> 🟡"
    elif pr <= 100:
        return f"<b>{pr}%</b> 🟢"



@router.message((F.text == 'Статистика бота'), state=admin.edit_context)
async def statistics(message: Message, state: FSMContext):
    await state.set_state(admin.edit_context)
    day_unt = await day_count(get_count=True)
    count_start = 1
    count_antiprop = 1
    count_donbass = 1
    count_war_aims = 1
    count_putin = 1
    count_end = 1
    victim = 1
    kinginfo = 1
    foma = 1
    warsupp = 1
    oppos = 1
    apolitical = 1
    stat = await mongo_select_stat()
    all_user = len(await mongo_select_stat_all_user())

    for i in stat:
        lst_count = []
        for j in i.values():
            if len(str(j))<2:
                print(j)
                lst_count.append(int(j))
            if str(j) == 'victim':
                victim +=1
            elif str(j) == 'kinginfo':
                kinginfo +=1
            elif str(j) == 'foma':
                foma +=1
            elif str(j) == 'warsupp':
                warsupp +=1
            elif str(j) == 'oppos':
                oppos +=1
            elif str(j) == 'apolitical':
                apolitical +=1
        print(lst_count)
        count_start += lst_count[1]
        count_antiprop += lst_count[2]
        count_donbass += lst_count[3]
        count_war_aims += lst_count[4]
        count_putin += lst_count[5]
        count_end += lst_count[6]
    await message.answer('<b>СТАТИСТИКА БОТА</b>\n'
                         '➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Пользователей за всё время: <b>{all_user}</b>\n'
                         f'Пользователей за 24 часа: <b>{day_unt}</b>\n'
                         f'➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Прошли начало: {count_start} ({count_visual(all_user, count_start)})\n'
                         f'Прошли Антипропаганду: {count_antiprop} ({count_visual(all_user, count_antiprop)})\n'
                         f'Прошли Донбасс: {count_donbass} ({count_visual(all_user, count_donbass)})\n'
                         f'Прошли Цели войны: {count_war_aims} ({count_visual(all_user, count_war_aims)})\n'
                         f'Прошли Путина: {count_putin} ({count_visual(all_user, count_putin)})\n'
                         f'Дошли до конца: {count_end} ({count_visual(all_user, count_end)})')





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


@router.message(IsAdmin(), (F.text == 'Подготовить бота к клонированию'))
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

@router.message(isKamaga(), content_types='video')
async def clone_bot_2(message: Message, state: FSMContext):
    video_id = message.video.file_id
    caption = message.caption
    await sql_safe_insert('new_assets', {'t_id': video_id, 'name': caption})
    await message.answer(f"Фото {caption} добавлено в базу данных. Ассет: {video_id}")


@router.message(isKamaga(), content_types='photo')
async def clone_bot_3(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    caption = message.caption
    await sql_safe_insert('new_assets', {'t_id': photo_id, 'name': caption})
    await message.answer(f"Фото {caption} добавлено в базу данных. Ассет: {photo_id}")


