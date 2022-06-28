import csv

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from psycopg2 import sql

import bata
from bata import all_data
from data_base.DBuse import sql_safe_select, sql_safe_update, sql_safe_insert, mongo_select_info, mongo_add_admin, \
    mongo_pop_admin, mongo_select_admins, sql_delete, postgresql_csv_dump
from filters.isAdmin import IsAdmin, IsSudo
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard, redct_text, \
    redct_media, redct_games, settings_bot, redct_editors
from stats.stat import mongo_select_stat
from utilts import phoenix_protocol, simple_media

router = Router()

class admin(StatesGroup):
    home = State()
    menu = State()
    add = State()
    pop = State()
    editors_menu = State()
    edit_context = State()
    add_text = State()
    edit_text = State()
    edit_text_test = State()
    add_media = State()
    edit_media_test = State()
    edit_media = State()
    confirm_add_text = State()
    confirm_edit_text = State()
    confirm_add_media = State()
    confirm_edit_media = State()
    repeat_add_text = State()
    repeat_edit_text = State()
    repeat_add_media = State()
    repeat_edit_media = State()
    delete_text_test = State()
    delete_text = State()
    delete_media_test = State()
    delete_media = State()


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

@router.message((F.text == 'Отменить изменения'), state=(admin.confirm_add_text, admin.confirm_add_media, admin.confirm_edit_text, admin.confirm_edit_media))
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
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=settings_bot())
        await state.set_state(admin.edit_context)
    elif 'admin:editors_menu' in str(stt):
        await message.answer("Выберите интересующий вас пункт меню", reply_markup=settings_bot())
        await state.set_state(admin.edit_context)
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
async def select_text(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующий вас пункт меню", reply_markup=settings_bot())
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
            print(tag_lists)
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

    postgresql_csv_dump('texts')
    await message.answer("Все выбранные теги были удалены!")


"""***************************************MEDIA************************************************"""

@router.message((F.text == 'Добавить новое медиа'), state = admin.edit_context)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin.add_media)
    photo = await sql_safe_select('t_id', 'assets', {'name': 'test_photo_tag'})
    try:
        await message.answer(text='Пришлите фото или видео,'
                                  ' подписав его удобным тегом подобного формата: some_unique_tag',
                             reply_markup=middle_admin_keyboard())
    except TelegramBadRequest:
        await message.answer('Похоже, что картинка, которую показывает бот в качестве примера, для вашего бота не работает.\n'
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

#red video
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

    postgresql_csv_dump('assets')
    await message.answer("Все выбранные теги были удалены!")
"""***************************************CONFIRM************************************************"""


@router.message((F.text == 'Подтвердить'), state=admin.confirm_edit_media)
async def approve_media_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_update('assets', {"t_id": data["t_id"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin.repeat_edit_media)
    else:
        await message.answer('Что-то пошло не так. Вы указали тэг?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_edit_text)
async def approve_edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_update('texts', {"text": data["text"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin.repeat_edit_text)
    else:
        await message.answer('Что-то пошло не так. Вы не ошиблись в разметке?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_add_media)
async def approve_media(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_insert('assets', data)
    if text is not False:
        await state.clear()
        await state.set_state(admin.repeat_add_media)
        await message.answer('Медиа добавлено. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Не получилось. Может быть, вы указали существующий таг?')


@router.message((F.text == 'Подтвердить'), state=admin.confirm_add_text)
async def approve_text(message: Message, state: FSMContext):
    data = await state.get_data()
    r = await sql_safe_insert('texts', data)
    if r != False:
        await state.set_state(admin.repeat_add_text)
        await message.answer('Текст добавлен. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Увы, ошибка. Скорее всего, этот таг сущесвует.')

"""***************************************IMPORT************************************************"""

@router.message((F.text == 'Импорт'), state=admin.edit_context)
async def import_csv_start(message: Message, state: FSMContext):
    await message.answer("Пришлите")


