from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from pandas import DataFrame
from psycopg2 import sql
from bata import all_data
from data_base.DBuse import sql_safe_select, sql_safe_update, sql_safe_insert
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard
from stats.stat import mongo_select_stat
from utilts import phoenix_protocol


class admin_home(StatesGroup):
    admin = State()
    add_text = State()
    add_media = State()
    testing_text = State()
    testing_media = State()
    text_edit_tag = State()
    text_edit = State()
    text_edit_test = State()
    media_edit_tag = State()
    media_edit = State()
    media_edit_test = State()
    statistics = State()
    game_change_tag = State()
    game_changer_main = State()


router = Router()
router.message.filter(state=admin_home)


@router.message(commands=["reborn"])
async def cmd_start(message: Message, state: FSMContext):
    await phoenix_protocol(message)


@router.message((F.text == "Выйти"), state=admin_home)
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы покинули уютный режим администрирования.\nУдачи!",
                         reply_markup=types.ReplyKeyboardRemove())


@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='меню', state=admin_home)
async def menu(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin_home.admin)
    await message.answer("Чего изволите теперь?", reply_markup=main_admin_keyboard())


@router.message((F.text == 'Добавить блок текста'), state=admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_text)
    text = await sql_safe_select('text', 'texts', {'name': 'any_unique_readible_tag'})
    text = text
    await message.answer(f'Пришлите сообщение, отделив тег от текста вертикальной чертой'
                         f' и переносом строки. После черты приведен пример:\n'
                         f'-------------------------'
                         f'\n\n{text}', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.add_text)
async def get_text(message: Message, state: FSMContext):
    try:
        new_name = message.html_text.split("|\n")[0]
        new_text = message.html_text.split("|\n")[1]
        await state.update_data(text=new_text, name=new_name)
        await state.set_state(admin_home.testing_text)
        await message.answer(f'<b>Тэг текста:</b>{new_name}\n<b>Текст:\n</b>{new_text}', parse_mode="HTML",
                             reply_markup=app_admin_keyboard())
    except:
        await message.answer('Ошибка. Похоже, вы использовали неверный формат текста.\n'
                             'Пожалуйста, прочтите инструкцию.', reply_markup=middle_admin_keyboard())


@router.message((F.text == 'Добавить медиа'), state=admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_media)
    photo = await sql_safe_select('t_id', 'assets', {'name': 'test_photo_tag'})
    try:
        await message.answer(text='Пришлите фото или видео,'
                                  ' подписав его удобным тегом подобного формата: some_unique_tag',
                             reply_markup=middle_admin_keyboard())
    except TelegramBadRequest:
        await message.answer('Похоже, что картинка, которую показывает бот в качестве примера, для вашего бота не работает.\n'
                             'Вы можете заменить ее на свою, воспользовавшись опцией "Изменить медиа" в главном меню, '
                             'и указав таг <b>test_photo_tag</b>')

@router.message(content_types='photo', state=admin_home.add_media)
async def get_photo(message: Message, state: FSMContext):
    ph_id = message.photo[0].file_id
    try:
        capt = message.caption.replace(" ", "_")
        await state.update_data(t_id=ph_id, name=capt)
        await message.answer_photo(ph_id, caption=capt)
        await state.set_state(admin_home.testing_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')


@router.message(content_types='video', state=admin_home.add_media)
async def get_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    try:
        capt = message.caption.replace(" ", "_")
        await state.update_data(t_id=vid_id, name=capt)
        await message.answer_video(vid_id, caption=capt)
        await state.set_state(admin_home.testing_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')


@router.message((F.text == 'Отредактировать блок текста'), state=admin_home.admin)
async def text_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.text_edit_tag)
    await message.answer('Пришлите тэг текстового блока, который вы хотите изменить.',
                         reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit_tag)
async def text_edit_text_tag(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': message.text})
    if text is not False:
        await message.answer(f'Выбранный вами пост после линии:\n----------------\n{text}', parse_mode="HTML")
        await message.answer('Если это нужный блок, то отправьте мне его новый вариант.',
                             reply_markup=middle_admin_keyboard())
        await state.set_state(admin_home.text_edit)
        await state.update_data(name=message.text)
    else:
        await message.answer(f'Вы ввели некорректный тэг, попробуйте еще раз', parse_mode="HTML")


@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit)
async def text_edit_text_test(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f'Проверьте правильность внесенных данных.\n\n\nТэг текста:{data["name"]}\n\nНовый текст:\n{message.html_text}',
        parse_mode="HTML", reply_markup=app_admin_keyboard())
    await state.update_data({"text": message.html_text})
    await state.set_state(admin_home.text_edit_test)
    test = await state.get_data()



@router.message((F.text == 'Изменить медиа'), state=admin_home.admin)
async def media_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.media_edit_tag)
    await message.answer('Пришлите тэг медиа, которое вы хотите изменить.', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.media_edit_tag)
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
        await state.set_state(admin_home.media_edit)
        await state.update_data(name=message.text)
    else:
        await message.answer('К сожалению, медиа под этим тэгом нет в базе.\nПопробуйте еще раз.',
                             reply_markup=middle_admin_keyboard())


@router.message(content_types='video', state=admin_home.media_edit)
async def appr_updated_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    await state.update_data(t_id=vid_id)
    await message.answer_video(vid_id, caption="Вы отправили это видео. Оно заменит старое. Все верно?",
                               reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)


@router.message(content_types='photo', state=admin_home.media_edit)
async def updated_video_test(message: Message, state: FSMContext):
    photo_id = message.photo[0].file_id
    await state.update_data(t_id=photo_id)
    await message.answer_photo(photo_id, caption="Вы отправили это фото. Оно заменит старое. Все верно?",
                               reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)


@router.message((F.text == 'Подтвердить'), state=admin_home.media_edit_test)
async def approve_media_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_update('assets', {"t_id": data["t_id"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin_home.admin)
    else:
        await message.answer('Что-то пошло не так. Вы указали тэг?')


@router.message((F.text == 'Подтвердить'), state=admin_home.text_edit_test)
async def approve_edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_update('texts', {"text": data["text"]}, {'name': data['name']})
    if text is not False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin_home.admin)
    else:
        await message.answer('Что-то пошло не так. Вы не ошиблись в разметке?')


@router.message((F.text == 'Подтвердить'), state=admin_home.testing_media)
async def approve_media(message: Message, state: FSMContext):
    data = await state.get_data()
    text = await sql_safe_insert('assets', data)
    if text is not False:
        await state.clear()
        await state.set_state(admin_home.admin)
        await message.answer('Медиа добавлено. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Не получилось. Может быть, вы указали существующий таг?')


@router.message((F.text == 'Подтвердить'), state=admin_home.testing_text)
async def approve_text(message: Message, state: FSMContext):
    data = await state.get_data()
    r = await sql_safe_insert('texts', data)
    if r != False:
        await state.set_state(admin_home.admin)
        await message.answer('Текст добавлен. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Увы, ошибка. Скорее всего, этот таг сущесвует.')


@router.message((F.text == 'Отменить'), state=(
admin_home.testing_text, admin_home.testing_media, admin_home.text_edit_test, admin_home.media_edit_test))
async def reset(message: Message, state: FSMContext):
    stt = await state.get_state()
    if stt == 'admin_home:testing_text':
        await state.set_state(admin_home.add_text)
        await message.answer('Хорошо, отправьте мне текст с правками', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:testing_media':
        await state.set_state(admin_home.add_media)
        await message.answer('Хорошо, отправьте мне другое медиа', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:media_edit_test':
        await state.set_state(admin_home.media_edit)
        await message.answer('Хорошо, отправьте мне медиа, на которое вы хотите заменить старое',
                             reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:text_edit_test':
        await state.set_state(admin_home.text_edit)
        await message.answer('Хорошо, отправьте мне текст, который заменит старый',
                             reply_markup=middle_admin_keyboard())
    else:
        await state.set_state(admin_home.admin)
        await message.answer('Хорошо, вернемся в меню', reply_markup=main_admin_keyboard())


@router.message((F.text == 'Изменить игру'), state=admin_home)
async def game_change_tag(message: Message, state: FSMContext):
    await state.set_state(admin_home.game_change_tag)
    await message.answer('Уф. Хорошо, в целях безопасности я попрошу вас прислать внутреннее название необходимой игры')


@router.message(state=admin_home.game_change_tag)
async def game_changer_main(message: Message, state: FSMContext):
    query = sql.SQL("SELECT * FROM {};").format(sql.Identifier(message.text))
    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
    conn.close()
    for thing in data:
        print(thing)
    await state.set_state(admin_home.game_changer_main)


@router.message((F.text == 'Аналитика'), state=admin_home.admin)
async def statistics(message: Message):
    count_come = 0
    count_start = 0
    count_antiprop = 0
    count_donbass = 0
    count_war_aims = 0
    count_putin = 0
    stat = await mongo_select_stat()
    for i in stat:
        lst = []
        for j in i.values():
            if len(str(j)) < 2:
                lst.append(j)
        count_come += lst[0]
        count_start += lst[1]
        count_antiprop += lst[2]
        count_donbass += lst[3]
        count_war_aims += lst[4]
    await message.answer('<b>ИНФОРМАЦИЯ О БОТЕ</b>\n'
                         '➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Пользователей: {count_come}\n'
                         f'➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Прошли начало: {count_start} ({round(count_start / count_come * 100, 1)}%)\n'
                         f'Прошли Антипропаганду: {count_antiprop} ({round(count_antiprop / count_come * 100, 1)}%)\n'
                         f'Прошли Донбасс: {count_donbass} ({round(count_donbass / count_come * 100, 1)}%)\n'
                         f'Прошли Цели войны: {count_war_aims} ({round(count_war_aims / count_come * 100, 1)}%)\n'
                        )

