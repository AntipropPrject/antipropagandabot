from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from data_base.DBuse import sql_safe_update, data_getter, sql_safe_insert, sql_delete, sql_games_row_selecter
from filters.isAdmin import IsAdmin
from keyboards.admin_keys import games_keyboard, admin_games_keyboard, app_admin_keyboard, \
    game_keys
from log import logg
from states.admin_states import admin
from utilts import game_answer
from utilts import simple_media

router = Router()
router.message.filter(state=admin)


@router.message(IsAdmin(level=['Редактирование']), (F.text == 'Игры 🎭'), state=admin.menu)
async def admin_home_games(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.game_menu)
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вошел в режим редактирования игр")
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))


@router.message((F.text == "Редактировать сюжет"), state=admin.addingMistakeOrLie_adding)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['surnameOfPerson']
    leng = await data_getter(
        f"select asset_name from mistakeorlie where asset_name like '%{tag}%' order by asset_name asc")
    nmrkup = ReplyKeyboardBuilder()
    for i in leng:
        nmrkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите сюжет, который вы хотели бы изменить",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie_upd)


@router.message(state=admin.addingMistakeOrLie_upd)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    await state.update_data(tag=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да, я хочу отредактировать этот сюжет полностью(и текст и медиа)"))
    nmrkup.row(types.KeyboardButton(text="Я хочу отредактировать только текст"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    media_id = await data_getter(f"select t_id from assets where name='{message.text}'")
    caption = await data_getter((f"select rebuttal from mistakeorlie where asset_name='{message.text}'"))
    try:
        await message.answer_photo(media_id[0][0], caption=caption[0][0],
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(media_id[0][0], caption=caption[0][0],
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie_upd_text_or_media)


@router.message(state=admin.addingMistakeOrLie_upd_text_or_media)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да, я хочу отредактировать этот сюжет полностью(и текст и медиа)":
        await message.answer("Пришлите новый видеофаил с подписью(тесктом)",
                             reply_markup=nmrkup.as_markup(resize_keyboard=True))
        await state.set_state(admin.addingMistakeOrLie_upd_text_and_media)
    elif message.text == "Я хочу отредактировать только текст":
        await message.answer("Пришлите текст", reply_markup=nmrkup.as_markup(resize_keyboard=True))
        await state.set_state(admin.addingMistakeOrLie_upd_text_only)
    else:
        print('do nothing')


@router.message(state=admin.addingMistakeOrLie_upd_text_only)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['tag']
    text = message.html_text
    await data_getter(f"update mistakeorlie set rebuttal='{text}' where asset_name='{tag}'; commit;")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer(f"Удалось обновить текст {tag}")
    await state.clear()


@router.message(state=admin.addingMistakeOrLie_upd_text_and_media)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['tag']
    text = message.html_text
    try:
        media_id = message.video.file_id
    except:
        media_id = message.photo[-1].file_id

    await data_getter(f"update assets set t_id='{media_id}' where name='{tag}'; commit;")
    await data_getter(f"update mistakeorlie set rebuttal='{text}' where asset_name='{tag}'; commit;")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Удалось обновить медиа и текст ")
    await state.clear()


@router.message((F.text == "Игра в правду 🥸"))
async def admin_truthgame(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.truthgame)
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Игра в правду - начало")

    await message.answer("Здравствуйте, это редактирование Игры в Правду.",
                         reply_markup=game_keys())


@router.message((F.text == "Добавить сюжет"), state=admin.truthgame)
async def admin_truthgame_add(message: types.Message, state: FSMContext):
    await message.answer("Пришлите мне сюда сюжет.\n\n\nИм может быть медиа с подписью или просто текст")
    await state.set_state(admin.truthgame_media_statement)


@router.message(state=admin.truthgame_media_statement)
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


@router.message(state=admin.truthgame_media_rebuttal)
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


@router.message(F.text.in_({'Правда', "Ложь"}), state=admin.truthgame_media_truth)
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


@router.message((F.text == "Подтвердить 👌🏼"), state=admin.truthgame_media_truth)
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


@router.message((F.text == "Удалить сюжет"), state=admin.truthgame)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    leng = (await data_getter("SELECT COUNT (*) FROM truthgame"))[0][0]
    nmrkup = ReplyKeyboardBuilder()
    for i in range(leng):
        nmrkup.row(types.KeyboardButton(text=i + 1))
    nmrkup.adjust(3)
    nmrkup.row(types.KeyboardButton(text='Назад'))
    await message.answer("Выберите сюжет, который вы хотели бы удалить",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame_deletion)


@router.message((F.text.in_({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'})),
                state=admin.truthgame_deletion)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    number = int(message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да, удалить этот сюжет"))
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = (await sql_games_row_selecter('truthgame', number))
    await state.update_data(data)
    await game_answer(message, data['plot_media'], data['plot_text'])
    await game_answer(message, data['rebb_media'], data['rebb_text'], nmrkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Да, удалить этот сюжет"), state=admin.truthgame_deletion)
async def admin_truthgame_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deletion_data = (await data_getter(f'DELETE FROM truthgame WHERE id = {data["id"]} RETURNING '
                                       f'asset_name, text_name, rebuttal, reb_asset_name; commit;'))[0]
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


@router.message((F.text == "Редактировать сюжет"), state=admin.truthgame)
async def admin_truthgame_update(message: types.Message, state: FSMContext):
    leng = (await data_getter("SELECT COUNT (*) FROM truthgame"))[0][0]
    nmrkup = ReplyKeyboardBuilder()
    for i in range(leng):
        nmrkup.row(types.KeyboardButton(text=i + 1))
    nmrkup.adjust(3)
    nmrkup.row(types.KeyboardButton(text='Назад'))
    await message.answer("Выберите сюжет, который вы хотели бы изменить",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame_update)


@router.message((F.text.in_({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'})),
                state=admin.truthgame_update)
async def admin_truthgame_update_select(message: types.Message, state: FSMContext):
    number = int(message.text)
    nmrkup = ReplyKeyboardBuilder()
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
    await message.answer(f'Если вам хочется отредактировать отдельно текст/медиа по тегам, то теги таковы:\n'
                         f'Правда: {dick["st_tag"]}\nЛожь: {dick["rb_tag"]}\n\n'
                         f'Если же вы хотите отредактировать все полностью, то пришлите мне новый сюжет ("Правда"):')
    await state.set_state(admin.truthgame_update_stt)


@router.message(state=admin.truthgame_update_stt)
async def admin_truthgame_add_stat(message: types.Message, state: FSMContext):
    await state.set_state(admin.truthgame_update_rbb)
    media_id = ''
    if message.photo is not None:
        media_id = message.photo[-1].file_id
    elif message.video is not None:
        media_id = message.video.file_id
    text = message.html_text
    await state.update_data({'truthgame_statement': text, 'truthgame_statement_asset': media_id})
    await message.answer('Пришлите мне сюда опровержение или подтверждение сюжета.'
                         '\n\n\nИми могут быть медиа с подписью или просто текст')


@router.message(state=admin.truthgame_update_rbb)
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


@router.message(F.text.in_({'Правда', "Ложь"}), state=admin.truthgame_update_truth)
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


@router.message((F.text == "Подтвердить 🤙"), state=admin.truthgame_update_approve)
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
                                       f'asset_name, text_name, rebuttal, reb_asset_name; commit;'))[0]
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
@router.message((F.text == "Путин (Ложь) 🚮"))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - Загрузка медиа")
    await message.answer("Привет! Это простая игра. Тут только один сюжет без опровержения! Что будем делать?",
                         reply_markup=game_keys())
    await state.set_state(admin.putin_game_lobby)


@router.message((F.text == "Добавить сюжет"), state=admin.putin_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - Загрузка медиа")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game)


@router.message(state=admin.putin_game)
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
                          f"Путин - Запись в базу данных \n {media_id} , putin_lie_game_{count}")
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{media_id}', 'putin_lie_game_{count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{text}', 'putin_lie_game_{count}'); commit;")

        await data_getter(
            f"insert into putin_lies(asset_name,text_name,belivers,nonbelivers) values ('putin_lie_game_{count}','putin_lie_game_{count}', 1,1); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Путин - Запись в базу данных +{ex}")
        await message.answer(str(ex))
    await message.answer(f"Добавлено новое утверждение под тегом putin_lie_game_{count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()


@router.message((F.text.contains('Удалить сюжет')), state=admin.putin_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите удалить",
                         reply_markup=admin_games_keyboard())
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from putin_lies order by asset_name asc")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите источник, в котором хотите удалить сюжет", reply_markup=nmarkup.as_markup())
    await state.set_state(admin.putin_game_del)


@router.message(state=admin.putin_game_del)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_del_apply)


@router.message(state=admin.putin_game_del_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да":
        await data_getter(f"delete from putin_lies where asset_name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text.contains('Редактировать сюжет')), state=admin.putin_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from putin_lies")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите редактировать",
                         reply_markup=nmarkup.as_markup())
    await state.set_state(admin.putin_game_upd)


@router.message(state=admin.putin_game_upd)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_update=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет ",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_upd_apply)


@router.message(state=admin.putin_game_upd_apply)
async def admin_home(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = await state.get_data()
    tag = data['media_to_update']
    try:
        asset = message.photo[-1].file_id
    except:
        asset = message.video.file_id
    if message.text == "Нет":
        await message.answer("Ну тогда смело жмите назад", reply_markup=nmrkup.as_markup())

    text = message.html_text

    if tag:
        await data_getter(f"update assets set t_id = '{asset}' where name = '{tag}; commit;'")
        await data_getter(f"update texts set text = '{text}' where name = '{tag}'; commit;")
        await message.answer(f"Медиа и текст под тегом <b>{tag}</b> изменено ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


#### TODO Удаление


@router.message(F.text == "Путин (Обещания) 🍜")
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - обещания")
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=game_keys())
    await state.set_state(admin.putin_game_old_lies)


@router.message((F.text == "Добавить сюжет"), state=admin.putin_game_old_lies)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Путин - Загрузка медиа")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_old_lies_add)


@router.message(state=admin.putin_game_old_lies_add)
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


@router.message((F.text.contains('Удалить сюжет')), state=admin.putin_game_old_lies)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите удалить",
                         reply_markup=admin_games_keyboard())
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from putin_old_lies order by asset_name asc")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите источник, в котором хотите удалить сюжет", reply_markup=nmarkup.as_markup())
    await state.set_state(admin.putin_game_old_lies_del)


@router.message(state=admin.putin_game_old_lies_del)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_old_lies_del_apply)


@router.message(state=admin.putin_game_del_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да":
        await data_getter(f"delete from putin_old_lies where asset_name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text.contains('Редактировать сюжет')), state=admin.putin_game_old_lies)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from putin_old_lies")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))

    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите редактировать",
                         reply_markup=nmarkup.as_markup())
    await state.set_state(admin.putin_game_old_lies_upd)


@router.message(state=admin.putin_game_old_lies_upd)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_update=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет ",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.putin_game_old_lies_upd_aplly)


@router.message(state=admin.putin_game_old_lies_upd_aplly)
async def admin_home(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = await state.get_data()
    tag = data['media_to_update']
    try:
        asset = message.photo[-1].file_id
    except:
        asset = message.video.file_id
    if message.text == "Нет":
        await message.answer("Ну тогда смело жмите назад", reply_markup=nmrkup.as_markup())

    text = message.html_text

    if tag:
        await data_getter(f"update assets set t_id = '{asset}' where name = '{tag}; commit;'")
        await data_getter(f"update texts set text = '{text}' where name = '{tag}'; commit;")
        await message.answer(f"Медиа и текст под тегом <b>{tag}</b> изменено ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message(F.text == "Игра Абсурда 🗯")
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нормал - Загрузка медиа")
    await message.answer("Привет! Это простая игра. Тут только один сюжет без опровержения! Что будем делать?",
                         reply_markup=game_keys())
    await state.set_state(admin.normal_game_lobby)


@router.message((F.text == "Добавить сюжет"), state=admin.normal_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нормал - Загрузка медиа")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.normal_game_add)


@router.message(state=admin.normal_game_add)
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


@router.message((F.text.contains('Удалить сюжет')), state=admin.normal_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите удалить",
                         reply_markup=admin_games_keyboard())
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from normal_game order by asset_name asc")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите источник, в котором хотите удалить сюжет", reply_markup=nmarkup.as_markup())
    await state.set_state(admin.normal_game_del)


@router.message(state=admin.normal_game_del)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.normal_game_del_apply)


@router.message(state=admin.normal_game_del_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да":
        await data_getter(f"delete from normal_game where asset_name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text.contains('Редактировать сюжет')), state=admin.normal_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from normal_game")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите редактировать",
                         reply_markup=nmarkup.as_markup())
    await state.set_state(admin.normal_game_upd)


@router.message(state=admin.normal_game_upd)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_update=message.text)
    nmrkup = ReplyKeyboardBuilder()

    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет ",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.normal_game_upd_apply)


@router.message(state=admin.normal_game_upd_apply)
async def admin_home(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = await state.get_data()
    tag = data['media_to_update']
    try:
        asset = message.photo[-1].file_id
    except:
        asset = message.video.file_id
    if message.text == "Нет":
        await message.answer("Ну тогда смело жмите назад", reply_markup=nmrkup.as_markup())

    text = message.html_text

    if tag:
        await data_getter(f"update assets set t_id = '{asset}' where name = '{tag}; commit;'")
        await data_getter(f"update texts set text = '{text}' where name = '{tag}'; commit;")
        await message.answer(f"Медиа и текст под тегом <b>{tag}</b> изменено ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message(F.text == "Игра Нацизма 💤")
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нацизм - Загрузка медиа")
    await message.answer("Привет! Это простая игра. Тут только один сюжет без опровержения! Что будем делать?",
                         reply_markup=game_keys())
    await state.set_state(admin.nazi_game_lobby)


@router.message((F.text == "Добавить сюжет"), state=admin.nazi_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Нацизм - Загрузка медиа")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте новый медиафайл и текст к посту с необходимой разметкой",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.nazi_game_lobby_add)


@router.message(state=admin.nazi_game_lobby_add)
async def menu(message: types.Message, state: FSMContext):
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


@router.message(state=admin.ucraine_or_not_media)
async def menu(message: types.Message, state: FSMContext):
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Невижу медиа")
    data = await state.get_data()
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


@router.message((F.text.contains('Удалить сюжет')), state=admin.nazi_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите удалить",
                         reply_markup=admin_games_keyboard())
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from ucraine_or_not_game order by asset_name asc")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите источник, в котором хотите удалить сюжет", reply_markup=nmarkup.as_markup())
    await state.set_state(admin.nazi_game_del)


@router.message(state=admin.nazi_game_del)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.nazi_game_del_apply)


@router.message(state=admin.nazi_game_del_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да":
        await data_getter(f"delete from ucraine_or_not_game where asset_name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text.contains('Редактировать сюжет')), state=admin.nazi_game_lobby)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    postgresdata = await data_getter(f"select asset_name from ucraine_or_not_game")
    for i in postgresdata:
        nmarkup.row(types.KeyboardButton(text=i[0]))
    await message.answer("Выберите номер сюжета(они представлены по порядку), который вы хотите редактировать",
                         reply_markup=nmarkup.as_markup())
    await state.set_state(admin.nazi_game_upd)


@router.message(state=admin.nazi_game_upd)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_update=message.text)
    nmrkup = ReplyKeyboardBuilder()

    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет ",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0],
                                   caption="Посмотрите внимательно. Это сюжет вы хотите редактировать? \nЕсли да, тогда отправьте новый сюжет с необходимой разметкой. Если нет, нажмите нет",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.nazi_game_upd_apply)


@router.message(state=admin.nazi_game_upd_apply)
async def admin_home(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    data = await state.get_data()
    tag = data['media_to_update']
    try:
        asset = message.photo[-1].file_id
    except:
        asset = message.video.file_id
    if message.text == "Нет":
        await message.answer("Ну тогда смело жмите назад", reply_markup=nmrkup.as_markup())

    text = message.html_text

    if tag:
        await data_getter(f"update assets set t_id = '{asset}' where name = '{tag}; commit;'")
        await data_getter(f"update texts set text = '{text}' where name = '{tag}'; commit;")
        await message.answer(f"Медиа и текст под тегом <b>{tag}</b> изменено ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text == "Ложь по тв 📺"), state=admin.game_menu)
async def admin_gam_tv(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ложь по тв")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="tv_first"))
    nmrkup.row(types.KeyboardButton(text="tv_HTB"))
    nmrkup.row(types.KeyboardButton(text="tv_star"))
    nmrkup.row(types.KeyboardButton(text="tv_24"))
    nmrkup.adjust(2, 2)
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Выберете телеканал",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie)


@router.message(state=admin.tv_lie)
async def menu(message: types.Message, state: FSMContext):
    await state.update_data(tv_channel=message.text)
    await message.answer(
        "Что вы хотите сделать?",
        reply_markup=game_keys())
    await state.set_state(admin.tv_lie_lobby)


@router.message((F.text == "Удалить сюжет"), state=admin.tv_lie_lobby)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['tv_channel']
    postgresdata = await data_getter(
        f"select name from assets where name like '%{tag}%' order by name asc")
    nmrkup = ReplyKeyboardBuilder()
    for i in postgresdata:
        nmrkup.row(types.KeyboardButton(text=f'{i[0]}'))
    await message.answer(
        "Выберете сюжет, они идут по порядку. \n!!!!! ВНИМАНИЕ - В этой игре сюжеты идут в паре с опровержением. Утверждения содержат lie а опровержения содержат reb ",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_del)


@router.message(state=admin.tv_lie_del)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    try:
        await message.answer_video(video=media_id[0][0],
                                   caption="Посмотрите внимательно. Этот сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(photo=media_id[0][0],
                                   caption="Посмотрите внимательно. Этот сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_del_apply)


@router.message((F.text == "Редактировать сюжет"), state=admin.tv_lie_lobby)
async def menu(message: types.Message, state: FSMContext):
    mnrkup = ReplyKeyboardBuilder()
    mnrkup.row(types.KeyboardButton(text="Редактировать подпись(текст)"))
    mnrkup.row(types.KeyboardButton(text="Перезалить видео или фото"))
    await message.answer('что именно нуждается в редактировании?', reply_markup=mnrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_upd_text_or_media)


@router.message((F.text == "Редактировать подпись(текст)"), state=admin.tv_lie_upd_text_or_media)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['tv_channel']
    postgresdata = await data_getter(
        f"select name from assets where name like '%{tag}%' order by name asc")
    nmrkup = ReplyKeyboardBuilder()
    for i in postgresdata:
        nmrkup.row(types.KeyboardButton(text=f'{i[0]}'))
    await message.answer(
        "Сюжеты идут по порядку в паре с опровержением. Утверждение сожержит в теге lie, опровержение содержит reb. Ваша задача выбрать сюжет, в котором вы хотите поменять текст  ",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_upd_text)


@router.message((F.text == "Перезалить видео или фото"), state=admin.tv_lie_upd_text_or_media)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag = data['tv_channel']
    postgresdata = await data_getter(
        f"select name from assets where name like '%{tag}%' order by name asc")
    nmrkup = ReplyKeyboardBuilder()
    for i in postgresdata:
        nmrkup.row(types.KeyboardButton(text=f'{i[0]}'))
    await message.answer(
        "Сюжеты идут по порядку в паре с опровержением. Утверждение сожержит в теге lie, опровержение сожержит reb. Ваша задача выбрать сюжет, который хотите перезалить  ",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_upd)


@router.message(state=admin.tv_lie_upd)
async def admin_home(message: types.Message, state: FSMContext):
    from handlers.admin_handlers.new_admin_hand import edit_media
    await edit_media(message, state)


@router.message(state=admin.tv_lie_upd_text)
async def admin_home(message: types.Message, state: FSMContext):
    from handlers.admin_handlers.new_admin_hand import text_edit_text_tag
    await text_edit_text_tag(message, state)


@router.message(state=admin.tv_lie_del_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    if message.text == "Да":
        await data_getter(f"delete from assets where name = '{media_id}'; commit;")
        await data_getter(f"delete from text where name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()


@router.message((F.text == "Добавить сюжет"), state=admin.tv_lie_lobby)
async def menu(message: types.Message, state: FSMContext):
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer(
        "Утверждение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.tv_lie_st)


@router.message(state=admin.tv_lie_st)
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
    postgressdata = await data_getter(f"select name from assets where name like '%{data['tv_channel']}_lie%'")
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


@router.message(state=admin.tv_lie_reb)
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


@router.message(F.text.contains('Удаление медиа из игры'))
async def menu(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))
    await state.set_state(admin.game_deleting)


"""***************************************MASS MEDIA************************************************"""


@router.message(F.text == "Ложь других СМИ 🧮", state=admin.game_menu)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующее вас действие", reply_markup=admin_games_keyboard())
    await state.set_state(admin.mass_media_menu)


@router.message((F.text.contains('Добавить сюжет')), state=admin.mass_media_menu)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='РИА Новости', callback_data='RIANEWS_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='Russia Today', callback_data='RUSSIATODAY_media_ RUSSIATODAY_exposure_')
    nmarkup.button(text='Телеграм-канал: Война с фейками', callback_data='TCHANEL_WAR_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='ТАСС / Комсомольская правда..', callback_data='TACC_media_ TACC_exposure_')
    nmarkup.button(text='Министерство обороны РФ', callback_data='MINISTRY_media_ MINISTRY_exposure_')
    nmarkup.adjust(1, 1, 1, 1, 1)
    await message.answer("Выберите источник, в который хотите добавить сюжет", reply_markup=nmarkup.as_markup())


@router.callback_query(lambda call: "media" in call.data and "exposure" in call.data)
async def add_media(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if 'pop' not in query.data and 'edit' not in query.data:
        await state.update_data(tag_media=query.data[3:])
        await query.message.delete()
        await query.message.answer('Загрузите медиа и напишите описание')
        await state.set_state(admin.add_news)
    elif 'pop' in query.data:
        await state.update_data(tag_media=query.data[3:])
        old_exposure = query.data.split()
        last_tag_numner = len(await data_getter(f"select name from assets where name like '%{old_exposure[-1]}%'"))
        print(last_tag_numner)
        if last_tag_numner != 1:
            await query.message.delete()
            keyboard = range(1, last_tag_numner + 1)
            nmarkup = ReplyKeyboardBuilder()
            for button in keyboard:
                nmarkup.row(types.KeyboardButton(text=button))
                nmarkup.adjust(3)
            await state.set_state(admin.mass_media_del)
            await query.message.answer('Выберите номер сюжета', reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await query.answer('Сюжеты в этом блоке отсутствуют')
    elif 'edit' in query.data:
        await state.update_data(tag_media=query.data[4:])
        old_exposure = query.data.split()
        last_tag_numner = len(await data_getter(f"select name from assets where name like '%{old_exposure[-1]}%'"))
        if last_tag_numner != 1:
            await query.message.delete()
            keyboard = range(1, last_tag_numner + 1)
            nmarkup = ReplyKeyboardBuilder()
            for button in keyboard:
                nmarkup.row(types.KeyboardButton(text=button))
                nmarkup.adjust(3)
            await state.set_state(admin.mass_media_edit)
            await query.message.answer('Выберите номер сюжета', reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await query.answer('Сюжеты в этом блоке отсутствуют')


@router.message(state=admin.add_news)
async def admin_home(message: types.Message, state: FSMContext):
    caption = message.html_text
    media = str()
    try:
        if message.content_type == 'photo':
            media = message.photo[0].file_id
            await message.answer_photo(media, caption=caption)
        elif message.content_type == 'video':
            media = message.video.file_id
            await message.answer_photo(media, caption=caption)
        await state.update_data(media_mass=media)
        await state.update_data(caption_mass=caption)
        await message.answer("Теперь отправьте мне опровержение этой новости")
        await state.set_state(admin.mass_media_add_exposure)
    except Exception as er:
        print(er)
        await message.answer("Упс.. Что-то пошло не так, пожалуйста повторите попытку")


@router.message(state=admin.mass_media_add_exposure)
async def admin_home(message: types.Message, state: FSMContext):
    caption = message.html_text
    media = str()
    try:
        if message.content_type == 'photo':
            media = message.photo[0].file_id
            await message.answer_photo(media, caption=caption)
        elif message.content_type == 'video':
            media = message.video.file_id
            await message.answer_photo(media, caption=caption)
        await state.update_data(media_mass_exposure=media)
        await state.update_data(caption_mass_exposure=caption)
        await message.answer("Всё верно?", reply_markup=app_admin_keyboard())
        await state.set_state(admin.mass_media_Done)
    except Exception as er:
        print(er)
        await message.answer("Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками")


@router.message((F.text.contains('Отменить изменения')),
                state=(admin.mass_media_Done, admin.mass_media_pop_Done, admin.mass_media_edit_add))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(admin.mass_media_menu)
    await message.answer('Отмена..', reply_markup=admin_games_keyboard())


@router.message((F.text.contains('Подтвердить')), state=admin.mass_media_Done)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tags = data['tag_media'].split()
    old_media_tag = tags[0]
    old_exposure_tag = tags[1]
    new_media = data['media_mass']
    new_caption = data['caption_mass']
    new_caption_exposure = data['media_mass_exposure']
    new_media_exposure = data['caption_mass_exposure']
    last_tag_numner = len(await data_getter(f"select name from assets where name like '%{old_exposure_tag}%'"))
    try:
        await sql_safe_insert('assets', {'t_id': new_media, 'name': f"{old_media_tag}{last_tag_numner + 1}"})
        await sql_safe_insert('assets',
                              {'t_id': new_media_exposure, 'name': f"{old_exposure_tag}{last_tag_numner + 1}"})
        await sql_safe_insert('texts', {'text': new_caption, 'name': f"{old_media_tag}{last_tag_numner + 1}"})
        await sql_safe_insert('texts',
                              {'text': new_caption_exposure, 'name': f"{old_exposure_tag}{last_tag_numner + 1}"})
        await state.set_state(admin.mass_media_menu)
        await message.answer("Сюжет был успешно добавлен в базу", reply_markup=admin_games_keyboard())
    except:
        await message.answer('Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками')


@router.message((F.text.contains('Удалить сюжет')), state=admin.mass_media_menu)
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующее вас действие", reply_markup=admin_games_keyboard())
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='РИА Новости', callback_data='popRIANEWS_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='Russia Today', callback_data='popRUSSIATODAY_media_ RUSSIATODAY_exposure_')
    nmarkup.button(text='Телеграм-канал: Война с фейками', callback_data='popTCHANEL_WAR_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='ТАСС / Комсомольская правда..', callback_data='popTACC_media_ TACC_exposure_')
    nmarkup.button(text='Министерство обороны РФ', callback_data='popMINISTRY_media_ MINISTRY_exposure_')
    nmarkup.adjust(1, 1, 1, 1, 1)
    await message.answer("Выберите источник, в котором хотите удалить сюжет", reply_markup=nmarkup.as_markup())


@router.message(state=admin.mass_media_del)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_input = message.text
    data = data['tag_media'].split()
    await message.answer('Сюжет лжи:')
    await simple_media(message, f'{data[0]}{user_input}')
    await message.answer('Сюжет правды:')
    await simple_media(message, f'{data[1]}{user_input}')
    await state.update_data(pop_media=f'{data[0]}{user_input}')
    await state.update_data(pop_exposure=f'{data[1]}{user_input}')
    await state.set_state(admin.mass_media_pop_Done)
    await message.answer('Хотите удалить этот сюжет?', reply_markup=app_admin_keyboard())


@router.message((F.text.contains('Подтвердить')), state=admin.mass_media_pop_Done)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pop_media = data['pop_media']
    pop_exposure = data['pop_exposure']
    try:
        await sql_delete('assets', {'name': pop_media})
        await sql_delete('assets', {'name': pop_exposure})
        await sql_delete('texts', {'name': pop_media})
        await sql_delete('texts', {'name': pop_exposure})
        await state.set_state(admin.mass_media_menu)
        await message.answer("Сюжет успешно удалён из базы", reply_markup=admin_games_keyboard())
    except:
        await message.answer("Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками")


@router.message((F.text.contains('Редактировать сюжет')), state=admin.mass_media_menu)
async def admin_home(message: types.Message, state: FSMContext):
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='РИА Новости', callback_data='editRIANEWS_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='Russia Today', callback_data='editRUSSIATODAY_media_ RUSSIATODAY_exposure_')
    nmarkup.button(text='Телеграм-канал: Война с фейками', callback_data='editTCHANEL_WAR_media_ TCHANEL_WAR_exposure_')
    nmarkup.button(text='ТАСС / Комсомольская правда..', callback_data='editTACC_media_ TACC_exposure_')
    nmarkup.button(text='Министерство обороны РФ', callback_data='editMINISTRY_media_ MINISTRY_exposure_')
    nmarkup.adjust(1, 1, 1, 1, 1)
    await message.answer("Выберите источник, в котором хотите изменить сюжет", reply_markup=nmarkup.as_markup())


@router.message(state=admin.mass_media_edit)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_input = message.text
    data = data['tag_media'].split()
    await message.answer('Сюжет лжи:')
    await simple_media(message, f'{data[0]}{user_input}')
    await message.answer('Сюжет правды:')
    await simple_media(message, f'{data[1]}{user_input}')
    await state.update_data(edit_media=f'{data[0]}{user_input}')
    await state.update_data(edit_exposure=f'{data[1]}{user_input}')
    await state.set_state(admin.mass_media_edit_add)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Отменить изменения"))
    await message.answer('Если вы хотите обновить этот сюжет, то пришлите мне новую ложь c описанием',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(state=admin.mass_media_edit_add)
async def admin_home(message: types.Message, state: FSMContext):
    try:
        caption = message.html_text
        if message.content_type == 'photo':
            media = message.photo[0].file_id
            await message.answer_photo(media, caption=caption)
        elif message.content_type == 'video':
            media = message.video.file_id
            await message.answer_photo(media, caption=caption)
        await state.update_data(media_mass=media)
        await state.update_data(caption_mass=caption)
        await state.set_state(admin.mass_media_edit_add_exposure)
        await message.answer("Теперь отправьте мне опровержение этой новости")

    except:
        await message.answer('Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками')


@router.message(state=admin.mass_media_edit_add_exposure)
async def admin_home(message: types.Message, state: FSMContext):
    caption = message.html_text
    media = str()
    try:
        if message.content_type == 'photo':
            media = message.photo[0].file_id
            await message.answer_photo(media, caption=caption)
        elif message.content_type == 'video':
            media = message.video.file_id
            await message.answer_photo(media, caption=caption)
        await state.update_data(media_mass_exposure=media)
        await state.update_data(caption_mass_exposure=caption)
        await message.answer("Всё верно?", reply_markup=app_admin_keyboard())
        await state.set_state(admin.mass_media_edit_Done)
    except:
        await message.answer('Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками')


@router.message((F.text.contains('Подтвердить')), state=admin.mass_media_edit_Done)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tag_media = data['edit_media']
    tag_exposure = data['edit_exposure']
    new_media_id = data['media_mass']
    new_caption = data['caption_mass']
    new_media_exposure_id = data['media_mass_exposure']
    new_caption_exposure = data['caption_mass_exposure']

    try:
        await sql_safe_update('assets', {'t_id': new_media_id}, {'name': tag_media})
        await sql_safe_update('assets', {'t_id': new_media_exposure_id}, {'name': tag_exposure})
        await sql_safe_update('texts', {'text': new_caption}, {'name': tag_media})
        await sql_safe_update('texts', {'text': new_caption_exposure}, {'name': tag_exposure})
        await state.set_state(admin.mass_media_menu)
        await message.answer("Сюжет был успешно обновлён в базе", reply_markup=admin_games_keyboard())
    except:
        await message.answer('Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками')
# @router.message(IsAdmin(), state=admin.game_deleting)
# async def menu(message: types.Message, state: FSMContext):
#     await message
