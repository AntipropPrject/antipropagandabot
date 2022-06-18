from psycopg2 import sql
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message
from pandas import DataFrame
from stats.stat import mongo_select
from bata import all_data
from data_base.DBuse import safe_data_getter, data_getter, sql_safe_select, sql_safe_update, sql_safe_insert
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard

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
router.message.filter(state = admin_home)


@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='Выйти', state=admin_home)
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы покинули уютный режим администрирования.\nУдачи!", reply_markup=types.ReplyKeyboardRemove())


@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='меню', state=admin_home)
async def menu(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin_home.admin)
    await message.answer("Чего изволите теперь?", reply_markup=main_admin_keyboard())


@router.message((F.text == 'Добавить блок текста'), state = admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_text)
    text = await sql_safe_select('text', 'texts', {'name':'any_unique_readible_tag'})
    text = text
    await message.answer(f'Пришлите сообщение, отделив тег от текста вертикальной чертой и переносом строки. После черты приведен пример:\n-------------------------'
                         f'\n\n{text}', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.add_text)
async def get_text(message: Message, state: FSMContext):
    try:
        new_name = message.text.split("|\n")[0]
        new_text = message.text.split("|\n")[1]
        await state.update_data(text = new_text, name = new_name)
        await state.set_state(admin_home.testing_text)
        await message.answer(f'<b>Тэг текста:</b>{new_name}\n<b>Текст:\n</b>{new_text}', parse_mode="HTML", reply_markup=app_admin_keyboard())
    except:
        await message.answer('Ошибка. Похоже, вы использовали неверный формат текста.\nПожалуйста, прочтите инструкцию.', reply_markup=middle_admin_keyboard())


@router.message((F.text == 'Добавить медиа'), state = admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_media)
    photo = await sql_safe_select('t_id', 'assets', {'name':'test_photo_tag'})
    await message.answer(text = 'Пришлите фото или видео, подписав его удобным тегом подобного формата: some_unique_tag', reply_markup=middle_admin_keyboard())

@router.message(content_types='photo', state=admin_home.add_media)
async def get_photo(message: Message, state: FSMContext):
    ph_id = message.photo[0].file_id
    try:
        capt = message.caption.replace(" ","_")
        await state.update_data(t_id = ph_id, name = capt)
        await message.answer_photo(ph_id, caption=capt)
        await state.set_state(admin_home.testing_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')


@router.message(content_types='video', state=admin_home.add_media)
async def get_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    try:
        capt = message.caption.replace(" ","_")
        await state.update_data(t_id = vid_id, name = capt)
        await message.answer_video(vid_id, caption=capt)
        await state.set_state(admin_home.testing_media)
        await message.answer('Все верно?', reply_markup=app_admin_keyboard())
    except:
        await message.answer('Пожалуйста, укажите тэг')

@router.message((F.text == 'Отредактировать блок текста'), state = admin_home.admin)
async def text_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.text_edit_tag)
    await message.answer('Пришлите тэг текстового блока, который вы хотите изменить.', reply_markup=middle_admin_keyboard())

@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit_tag)
async def text_edit_text_tag(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name':message.text})
    if text != False:
        await message.answer(f'Выбранный вами пост после линии:\n----------------\n{text}', parse_mode="HTML")
        await message.answer('Если это нужный блок, то отправьте мне его новый вариант.', reply_markup=middle_admin_keyboard())
        await state.set_state(admin_home.text_edit)
        await state.update_data(name = message.text)
    else:
        await message.answer(f'Вы ввели некорректный тэг, попробуйте еще раз', parse_mode="HTML")

@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit)
async def text_edit_text_test(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f'Проверьте правильность внесенных данных.\n\n\nТэг текста:{data["name"]}\n\nНовый текст:\n{message.text}',
                         parse_mode="HTML", reply_markup=app_admin_keyboard())
    await state.update_data({"text":message.text})
    await state.set_state(admin_home.text_edit_test)

    test = await state.get_data()
    dtframe = DataFrame([test.values()], columns=test.keys())
    print(dtframe)


@router.message((F.text == 'Изменить медиа'), state = admin_home.admin)
async def media_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.media_edit_tag)
    await message.answer('Пришлите тэг медиа, которое вы хотите изменить.', reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.media_edit_tag)
async def edit_media(message: Message, state: FSMContext):
    media_id = await sql_safe_select('t_id', 'assets', {'name': message.text})
    if media_id != False:
        try:
            await message.answer_photo(media_id, caption='Это выбранная вами картинка. Если все верно, отправьте ту, '
                                                         'на которую вы хотите ее заменить', reply_markup=middle_admin_keyboard())
        except:
            pass
        try:
            await message.answer_video(media_id, caption='Это выбранное вами видео. Если все верно, отправьте то, на которое его надо заменить'
                                       , reply_markup=middle_admin_keyboard())
        except:
            pass
        await state.set_state(admin_home.media_edit)
        await state.update_data(name = message.text)
    else:
        await message.answer('К сожалению, медиа под этим тжгом нет в базе.\nПопробуйте еще раз.', reply_markup=middle_admin_keyboard())


@router.message(content_types='video', state=admin_home.media_edit)
async def appr_updated_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    await state.update_data(t_id = vid_id)
    await message.answer_video(vid_id, caption="Вы отправили это видео. Оно заменит старое. Все верно?", reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)

@router.message(content_types='photo', state=admin_home.media_edit)
async def updated_video_test(message: Message, state: FSMContext):
    photo_id = message.photo[0].file_id
    await state.update_data(t_id = photo_id)
    await message.answer_photo(photo_id, caption="Вы отправили это фото. Оно заменит старое. Все верно?", reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)

@router.message((F.text == 'Подтвердить'), state=admin_home.media_edit_test)
async def approve_media_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    r = await sql_safe_update('assets', {"t_id": data["t_id"]}, {'name': data['name']})
    if r != False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin_home.admin)
    else:
        await message.answer('Что-то пошло не так. Вы указали тэг?')


@router.message((F.text == 'Подтвердить'), state=admin_home.text_edit_test)
async def approve_edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    r = await sql_safe_update('texts', {"text": data["text"]}, {'name': data['name']})
    if r != False:
        await message.answer('Все готово', reply_markup=main_admin_keyboard())
        await state.clear()
        await state.set_state(admin_home.admin)
    else:
        await message.answer('Что-то пошло не так. Вы не ошиблись в разметке?')

@router.message((F.text == 'Подтвердить'), state = admin_home.testing_media)
async def approve_media(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    r = await sql_safe_insert('assets', data)
    if r != False:
        await state.clear()
        await state.set_state(admin_home.admin)
        await message.answer('Медиа добавлено. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Не получилось. Может быть, вы указали существующий таг?')


@router.message((F.text == 'Подтвердить'), state = admin_home.testing_text)
async def approve_text(message: Message, state: FSMContext):
    data = await state.get_data()
    r = await sql_safe_insert('texts', data)
    if r != False:
        await state.set_state(admin_home.admin)
        await message.answer('Текст добавлен. Еще разок?', reply_markup=main_admin_keyboard())
    else:
        await message.answer('Увы, ошибка. Скорее всего, этот таг сущесвует.')


@router.message((F.text == 'Отменить'), state = (admin_home.testing_text, admin_home.testing_media, admin_home.text_edit_test, admin_home.media_edit_test))
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
        await message.answer('Хорошо, отправьте мне медиа, на которое вы хотите заменить старое', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:text_edit_test':
        await state.set_state(admin_home.text_edit)
        await message.answer('Хорошо, отправьте мне текст, который заменит старый', reply_markup=middle_admin_keyboard())
    else:
        await state.set_state(admin_home.admin)
        await message.answer('Хорошо, вернемся в меню',
                             reply_markup=main_admin_keyboard())



@router.message((F.text == 'Изменить игру'), state = admin_home)
async def game_change_tag(message: Message, state: FSMContext):
    await state.set_state(admin_home.game_change_tag)
    await message.answer('Уф. Хорошо, в целях безопасности я попрошу вас прислать внутреннее название необходимой игры')

@router.message(state = admin_home.game_change_tag)
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


@router.message((F.text == 'Аналитика'), state = admin_home.admin)
async def statistics(message: Message, state: FSMContext):
    count_come = 0
    count_start = 0
    count_antiprop = 0
    count_donbass = 0
    count_war_aims = 0
    count_putin = 0
    stat = await mongo_select()
    for i in stat:
        lst = []
        for j in i.values():
            if len(str(j))<2:
                lst.append(j)
        count_come += lst[0]
        count_start += lst[1]
        count_antiprop += lst[2]
        count_donbass += lst[3]
        count_war_aims += lst[4]
        count_putin += lst[5]
    await message.answer('АНАЛИТИКА О БОТЕ\n'
                         '➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Пользователей: {count_come}\n'
                         f'➖➖➖➖➖➖➖➖➖➖\n\n'
                         f'Прошли начало: {count_start} ({count_start/count_come*100}%)\n'
                         f'Прошли Антипропаганду: {count_antiprop} ({count_antiprop/count_come*100}%)\n'
                         f'Прошли Донбасс: {count_donbass} ({count_donbass/count_come*100}%)\n'
                         f'Прошли Цели войны: {count_war_aims} ({count_war_aims/count_come*100}%)\n'
                         f'Прошли Путина: {count_putin} ({count_putin/count_come*100}%)')

