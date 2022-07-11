import psycopg2
from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_update, data_getter, sql_safe_insert, sql_select_row_like, sql_games_row_selecter, \
    sql_delete
from filters.isAdmin import IsAdmin
from keyboards.admin_keys import main_admin_keyboard, games_keyboard
from log import logg
from states.admin_states import admin
from utilts import dynamic_media_answer, game_answer

router = Router()
router.message.filter(state=admin)


@router.message(IsAdmin(), (F.text == 'Игры 🎭'), state=admin.menu)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.menu)
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вошел в режим редактирования игр")
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))


@router.message(IsAdmin(), (F.text == "Пропагандисты 💢"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ошибка или ложь(пропагандисты) - выбор пропагандиста")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте фамилию пропагандиста без опечаток(ТОЛЬКО ФАМИЛИЮ)",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie)


@router.message(IsAdmin(), state=admin.addingMistakeOrLie)
async def menu(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ошибка или ложь(пропагандисты) - редактирование")
    await state.clear()
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer(
        "Отправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.update_data(surnameOfPerson=message.text)
    await state.set_state(admin.addingMistakeOrLie_media)


@router.message(IsAdmin(), state=admin.addingMistakeOrLie_media)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")
    text = message.html_text
    data = await state.get_data()
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    surname = data['surnameOfPerson']
    postgressdata = await data_getter(f"select name from assets where name like '%{surname}%'")
    count = len(postgressdata)
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Ошибка или ложь(пропагандисты) - Запись в базу данных \n {media_id} , statement_{surname}_{count}")
    # await sql_safe_update('assets', {"t_id": media_id}, {'name': f"statement_{surname}_{count}"})
    try:
        result = await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'statement_{surname}_{count + 1}'); commit;")
        print(result)
        await data_getter(
            f"insert into mistakeorlie(asset_name,belivers,nonbelivers,rebuttal) values ('statement_{surname}_{count + 1}', 1,1,'{text}'); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Ошибка или ложь(пропагандисты) - Запись в базу данных \n {media_id} , statement_{surname}_{count + 1}+{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом statement_{surname}_{count + 1}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Игра в правду 🥸"))
async def admin_truthgame(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.truthgame)
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Игра в правду - начало")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Добавить сюжет"))
    nmrkup.row(types.KeyboardButton(text="Редактировать сюжет"))
    nmrkup.add(types.KeyboardButton(text="Удалить сюжет"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Здравствуйте, это редактирование Игры в Правду.",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), (F.text == "Добавить сюжет"), state=admin.truthgame)
async def admin_truthgame_add(message: types.Message, state: FSMContext):
    await message.answer("Пришлите мне сюда сюжет.\n\n\nИм может быть медиа с подписью или просто текст")
    await state.set_state(admin.truthgame_media_statement)


@router.message(IsAdmin(), state=admin.truthgame_media_statement)
async def admin_truthgame_add_stat(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_media_rebuttal)
    media_id = ''
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    text = message.html_text
    await state.update_data({'truthgame_statement': text, 'truthgame_statement_asset': media_id})
    await message.answer('Пришлите мне сюда опровержение или подтверждение сюжате.'
                         '\n\n\nИми могут быть медиа с подписью или просто текст')


@router.message(IsAdmin(), state=admin.truthgame_media_rebuttal)
async def admin_truthgame_add_rebb(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_media_truth)
    media_id = ''
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    text = message.html_text
    await state.update_data({'truthgame_rebb': text, 'truthgame_rebb_asset': media_id})
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Правда"))
    nmrkup.row(types.KeyboardButton(text="Ложь"))
    await message.answer('Отлично! Теперь давайте определим: изначальный сюжет правда, или ложь?',
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), F.text.in_({'Правда', "Ложь"}), state=admin.truthgame_media_truth)
async def admin_truthgame_add_truth(message: types.Message, state: FSMContext):
    dick = dict()
    if message.text == 'Правда':
        dick = {'truthgamebool': 'true'}
    elif message.text == 'Ложь':
        dick = {'truthgamebool': 'false'}
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Игра в правду - ложь или правда")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Подтвердить 👌🏼"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await state.update_data(dick)
    await message.answer(f"В дальнейшем вы сможете проверить правильность внесенных данных, но пока что выбор таков",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), (F.text == "Подтвердить 👌🏼"), state=admin.truthgame_media_truth)
async def mesdfsdfnu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    st_text = data['truthgame_statement']
    st_asset = data['truthgame_statement_asset']
    reb_text = data['truthgame_rebb']
    reb_asset = data['truthgame_rebb_asset']
    tag_count = (await data_getter("SELECT id FROM truthgame ORDER BY id DESC LIMIT 1"))[0][0]
    st_tag = 'truthgame_' + str(tag_count).zfill(2)
    reb_tag = 't_game_reb_' + str(tag_count).zfill(2)
    isTrue = data['truthgamebool']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Игра в правду - Запись в базу данных \n {st_tag} , {reb_tag}")
    dick = {'id': tag_count + 1, 'truth': isTrue, 'belivers': 1, 'nonbelivers': 1}
    if st_asset:
        await sql_safe_insert('assets', {'t_id': st_asset, 'name': st_tag})
        dick.update({'asset_name': st_tag})
    if reb_asset:
        await sql_safe_insert('assets', {'t_id': reb_asset, 'name': reb_tag})
        dick.update({'reb_asset_name': reb_tag})
    if st_text:
        await sql_safe_insert('texts', {'text': st_text, 'name': st_tag})
        dick.update({'text_name': st_tag})
    if reb_text:
        await sql_safe_insert('texts', {'text': reb_text, 'name': reb_tag})
        dick.update({'rebuttal': reb_tag})
    await sql_safe_insert('truthgame', dick)
    await message.answer(f"Добавлено новая пара для игры в правду под тегами {st_tag}/{reb_tag}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Удалить сюжет"), state=admin.truthgame)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    leng = (await data_getter("SELECT COUNT (*) FROM truthgame"))[0][0]
    nmrkup = ReplyKeyboardBuilder()
    for i in range(leng):
        nmrkup.row(types.KeyboardButton(text=i + 1))
    await message.answer("Выберите сюжет, который вы хотели бы удалить",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame_deletion)


@router.message(IsAdmin(), (F.text.in_({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'})), state=admin.truthgame_deletion)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    number = int(message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да, удалить этот сюжет"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = (await sql_games_row_selecter('truthgame', number))
    await state.update_data(data)
    await game_answer(message, data['plot_media'], data['plot_text'])
    await game_answer(message, data['rebb_media'], data['rebb_text'], nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), (F.text == "Да, удалить этот сюжет"), state=admin.truthgame_deletion)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deletion_data = (await data_getter(f'DELETE FROM truthgame WHERE id = {data["id"]} RETURNING '
                                       f'asset_name, text_name, rebuttal, reb_asset_name'))[0]
    print(deletion_data)
    if deletion_data[0] is not None:
        await sql_delete('assets', {'name': deletion_data[0]})
    if deletion_data[3] is not None:
        await sql_delete('assets', {'name': deletion_data[3]})
    if deletion_data[1] is not None:
        await sql_delete('texts', {'name': deletion_data[1]})
    if deletion_data[2] is not None:
        await sql_delete('texts', {'name': deletion_data[2]})
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Возврат в главное меню"))
    await message.answer('Сюжет был успешно удален', reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), (F.text == "Редактировать сюжет"), state=admin.truthgame)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    leng = (await data_getter("SELECT COUNT (*) FROM truthgame"))[0][0]
    nmrkup = ReplyKeyboardBuilder()
    for i in range(leng):
        nmrkup.row(types.KeyboardButton(text=i + 1))
    await message.answer("Выберите сюжет, который вы хотели бы изменить",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame_update)


@router.message(IsAdmin(), (F.text.in_({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'})),
                state=admin.truthgame_update)
async def admin_truthgame_update_select(message: types.Message, state: FSMContext):
    number = int(message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да, отредактировать этот сюжет"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = (await data_getter(f'SELECT * FROM (SELECT *, row_number() over (ORDER BY id) FROM truthgame) '
                              f'AS GG WHERE row_number = {number}'))[0]
    dick = dict()
    if data[2] is not None:
        dick.update({'st_tag': data[2]})
    elif data[3] is not None:
        dick.update({'st_tag': data[3]})
    if data[6] is not None:
        dick.update({'rb_tag': data[6]})
    elif data[7] is not None:
        dick.update({'rb_tag': data[7]})
    dick.update({'id': data[0]})
    await state.update_data(dick)
    data = (await sql_games_row_selecter('truthgame', number))
    await game_answer(message, data['plot_media'], data['plot_text'])
    await game_answer(message, data['rebb_media'], data['rebb_text'], nmrkup.as_markup(resize_keyboard=True))
    await message.answer('Если это корректные сообщения, отправьте мне сообщение сюжета:')
    await state.set_state(admin.truthgame_update_stt)


@router.message(IsAdmin(), state=admin.truthgame_update_stt)
async def admin_truthgame_add_stat(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_update_rbb)
    media_id = ''
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    text = message.html_text
    await state.update_data({'truthgame_statement': text, 'truthgame_statement_asset': media_id})
    await message.answer('Пришлите мне сюда опровержение или подтверждение сюжате.'
                         '\n\n\nИми могут быть медиа с подписью или просто текст')


@router.message(IsAdmin(), state=admin.truthgame_update_rbb)
async def admin_truthgame_add_rebb(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_update_truth)
    media_id = ''
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    text = message.html_text
    await state.update_data({'truthgame_rebb': text, 'truthgame_rebb_asset': media_id})
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Правда"))
    nmrkup.row(types.KeyboardButton(text="Ложь"))
    await message.answer('Отлично! Теперь давайте определим: изначальный сюжет правда, или ложь?',
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), F.text.in_({'Правда', "Ложь"}), state=admin.truthgame_update_truth)
async def admin_truthgame_add_truth(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_update_approve)
    dick = dict()
    if message.text == 'Правда':
        dick = {'truthgamebool': 'true'}
    elif message.text == 'Ложь':
        dick = {'truthgamebool': 'false'}
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Игра в правду - ложь или правда")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Подтвердить 🤙"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await state.update_data(dick)
    await message.answer(f"В дальнейшем вы сможете проверить правильность внесенных данных, но пока что выбор таков",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))


@router.message(IsAdmin(), (F.text == "Подтвердить 🤙"), state=admin.truthgame_update_approve)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    st_text = data['truthgame_statement']
    st_asset = data['truthgame_statement_asset']
    reb_text = data['truthgame_rebb']
    reb_asset = data['truthgame_rebb_asset']
    tag_count = (await data_getter("SELECT id FROM truthgame ORDER BY id DESC LIMIT 1"))[0][0]
    st_tag = data['st_tag']
    reb_tag = data['rb_tag']
    isTrue = data['truthgamebool']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    dick = {'truth': isTrue, 'belivers': 1, 'nonbelivers': 1}
    deletion_data = (await data_getter(f'DELETE FROM truthgame WHERE id = {data["id"]} RETURNING '
                                       f'asset_name, text_name, rebuttal, reb_asset_name'))[0]
    print(deletion_data)
    if deletion_data[0] is not None:
        await sql_delete('assets', {'name': deletion_data[0]})
    if deletion_data[3] is not None:
        await sql_delete('assets', {'name': deletion_data[3]})
    if deletion_data[1] is not None:
        await sql_delete('texts', {'name': deletion_data[1]})
    if deletion_data[2] is not None:
        await sql_delete('texts', {'name': deletion_data[2]})

    dick = {'id': data['id'], 'truth': isTrue, 'belivers': 1, 'nonbelivers': 1}
    if st_asset:
        await sql_safe_insert('assets', {'t_id': st_asset, 'name': st_tag})
        dick.update({'asset_name': st_tag})
    if reb_asset:
        await sql_safe_insert('assets', {'t_id': reb_asset, 'name': reb_tag})
        dick.update({'reb_asset_name': reb_tag})
    if st_text:
        await sql_safe_insert('texts', {'text': st_text, 'name': st_tag})
        dick.update({'text_name': st_tag})
    if reb_text:
        await sql_safe_insert('texts', {'text': reb_text, 'name': reb_tag})
        dick.update({'rebuttal': reb_tag})
    await sql_safe_insert('truthgame', dick)
    await message.answer(f"Обновлена пара по тегам: {st_tag}/{reb_tag}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


"""    if st_asset:
        if await sql_safe_insert('assets', {'t_id': st_asset, 'name': st_tag}) is False:
            await sql_safe_update('assets', {'t_id': st_asset}, {'name': st_tag})
        dick.update({'asset_name': st_tag})
    else:
        dick.update({'asset_name': None})
        await sql_delete('assets', {'name': st_tag})
    if reb_asset:
        if await sql_safe_insert('assets', {'t_id': st_asset, 'name': reb_tag}) is False:
            await sql_safe_update('assets', {'t_id': reb_asset}, {'name': reb_tag})
        dick.update({'reb_asset_name': reb_tag})
    else:
        dick.update({'reb_asset_name': None})
        await sql_delete('assets', {'name': reb_tag})
    if st_text:
        if await sql_safe_insert('texts', {'text': st_text, 'name': st_tag}) is False:
            await sql_safe_update('assets', {'t_id': reb_asset}, {'name': reb_tag})
        dick.update({'text_name': st_tag})
    else:
        dick.update({'text_name': None})
        await sql_delete('texts', {'name': st_tag})
    if reb_text:
        if await sql_safe_insert('texts', {'text': st_text, 'name': st_tag}) is False:
            await sql_safe_update('texts', {'text': reb_text}, {'name': reb_tag})
        dick.update({'rebuttal': reb_tag})
    else:
        dick.update({'rebuttal': None})
        await sql_delete('texts', {'name': reb_tag})
    print(dick)
    for di in dick:
        await sql_safe_update('truthgame', {di: dick[di]}, {'id': data['id']})"""



#######################ПУТИН
@router.message(IsAdmin(), (F.text == "Путин (Ложь) 🚮"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - Загрузка медиа")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game)


@router.message(IsAdmin(), state=admin.putin_game)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")

    text = message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%putin_lie_game_%'")
    count = len(postgressdata) + 1
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Ошибка или ложь(пропагандисты) - Запись в базу данных \n {media_id} , lying_dictator_00{count}")
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'lying_dictator_00{count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{text}', 'putin_lie_game_{count}'); commit;")

        await data_getter(
            f"insert into putin_lies(asset_name,text_name,belivers,nonbelivers) values ('lying_dictator_00{count}','putin_lie_game_{count}', 1,1); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Ошибка или ложь(пропагандисты) - Запись в базу данных +{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом lying_dictator_00{count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Путин (Обещания) 🍜"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - обещания")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_old_lies)


@router.message(IsAdmin(), state=admin.putin_game)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")

    text = message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%putin_oldlie_game%'")
    count = len(postgressdata) + 1
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Путин-старый - Запись в базу данных \n {media_id} , putin_oldlie_game_{count}")
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'putin_oldlie_game_{count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{text}', 'putin_oldlie_game_{count}'); commit;")

        await data_getter(
            f"insert into putin_old_lies(asset_name,text_name,belivers,nonbelivers) values ('putin_oldlie_game_{count}','putin_lie_game_{count}', 1,1); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Старый Путин - Запись в базу данных +{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом putin_oldlie_game_{count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Игра Абсурда 🗯"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Игра в нормальность")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.normal_game)


@router.message(IsAdmin(), state=admin.normal_game)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")

    text = message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%normal_game%'")
    count = len(postgressdata) + 1
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Игра в нормальность - Запись в базу данных \n {media_id} , normal_game_{count}")
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'normal_game_{count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{text}', 'normal_game_{count}'); commit;")

        await data_getter(
            f"insert into normal_game(asset_name,text_name,belivers,nonbelivers) values ('normal_game_{count}','normal_game_{count}', 1,1); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Игра в нормальность - Запись в базу данных +{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом normal_game_{count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Игра Нацизма 💤"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Украина или нет?")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте True или False",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.ucraine_or_not)


@router.message(IsAdmin(), state=admin.ucraine_or_not)
async def menu(message: types.Message, state: FSMContext):
    if message.text.lower() == 'true' or message.text.lower() == 'false':
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              "Украина или нет - редактирование")
        await state.clear()
        nmrkup = ReplyKeyboardBuilder()
        nmrkup.row(types.KeyboardButton(text="Назад"))
        await message.answer(
            "Утверждение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
            reply_markup=nmrkup.as_markup(resize_keyboard=True))
        await state.update_data(ucranebool=message.text)
        await state.set_state(admin.ucraine_or_not_media)
    else:
        await message.answer("Что-то пошло не так, отправьте либо True либо False")


@router.message(IsAdmin(), state=admin.ucraine_or_not_media)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")
    data = state.get_data()
    truth = data['ucranebool']
    text = message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%country_game%'")
    count = len(postgressdata) + 1
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Украина - Запись в базу данных \n {media_id} , country_game_{count}")
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'country_game_{count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{text}', 'country_game_{count}'); commit;")

        await data_getter(
            f"insert into ucraine_or_not_game(asset_name,text_name,belivers,nonbelivers,truth) values ('normal_game_{count}','normal_game_{count}', 1,1,{truth}); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Украина или нет? - Запись в базу данных +{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом country_game_{count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text == "Ложь по тв 📺"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ложь по тв")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="tv_first"))
    nmrkup.row(types.KeyboardButton(text="tv_HTB"))
    nmrkup.row(types.KeyboardButton(text="tv_star"))
    nmrkup.row(types.KeyboardButton(text="tv_24"))

    await message.answer("Выберете телеканал",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie)


@router.message(IsAdmin(), state=admin.tv_lie)
async def menu(message: types.Message, state: FSMContext):
    await state.update_data(tv_channel=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer(
        "Утверждение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_st)


@router.message(IsAdmin(), state=admin.tv_lie_st)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Не вижу медиа")
    text = message.html_text
    data = await state.get_data()
    tv_channel = data['tv_channel']
    await state.update_data(tv_lie_statement=text)
    await state.update_data(tv_lie_statement_asset=media_id)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%{data['tv_channel']}%'")
    count = len(postgressdata) + 1
    print(postgressdata)
    tagdata = list()
    for everytag in postgressdata:
        tagdata.append(everytag[0])
    print(tagdata)
    tag = f'{tv_channel}_{count}'
    while tag in tagdata:
        count += 1
        tag = f'{tv_channel}'
        print(tag)
    print(tag)
    await state.update_data(tv_tag=tag)
    await state.update_data(tv_tag_count=count)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))

    await message.answer("Опровержение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_reb)


@router.message(IsAdmin(), state=admin.tv_lie_reb)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Не вижу медиа")
    st_text = data['tv_lie_statement']
    st_asset = data['tv_lie_statement_asset']
    reb_text = message.html_text
    reb_asset = media_id
    tag_count = data['tv_tag_count']
    tv_channel = data['tv_channel']

    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))

    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Ложь на тв - Запись в базу данных \n {reb_asset} , {tv_channel}")
    # await sql_safe_update('assets', {"t_id": media_id}, {'name': f"statement_{surname}_{count}"})
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{st_asset}', '{tv_channel}_lie_{tag_count}'); commit;")
        await data_getter(
            f"insert into assets(t_id,name) values('{reb_asset}', '{tv_channel}_reb_{tag_count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{st_text}', '{tv_channel}_lie_{tag_count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{reb_text}', '{tv_channel}_reb_{tag_count}'); commit;")

    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Ошибка или ложь(пропагандисты) - Запись в базу данных")
        await message.answer(str(ex))
    await message.answer(
        f"Добавлено новая пара для игры Ложь На ТВ под тегами {tv_channel}_lie_{tag_count}/{tv_channel}_reb_{tag_count}",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message(IsAdmin(), (F.text.contains('Удаление медиа из игры')))
async def menu(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))
    await state.set_state(admin.game_deleting)

# @router.message(IsAdmin(), state=admin.game_deleting)
# async def menu(message: types.Message, state: FSMContext):
#     await message
