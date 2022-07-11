from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from data_base.DBuse import sql_safe_update, data_getter, sql_safe_insert, sql_delete
from filters.isAdmin import IsAdmin
from keyboards.admin_keys import main_admin_keyboard, games_keyboard, admin_games_keyboard, app_admin_keyboard
from log import logg
from states.admin_states import admin
from utilts import simple_media

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
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Игра в правду - выбор true/false")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Напишите True Или False ",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame)


@router.message(IsAdmin(), state=admin.truthgame)
async def menu(message: types.Message, state: FSMContext):
    if message.text.lower() == 'true' or message.text.lower() == 'false':
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              "Игра в правду - редактирование")
        await state.clear()
        nmrkup = ReplyKeyboardBuilder()
        nmrkup.row(types.KeyboardButton(text="Назад"))
        await message.answer(
        "Утверждение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
        await state.update_data(truthgamebool=message.text)
        await state.set_state(admin.truthgame_media_statement)
    else:
        await message.answer("Что-то пошло не так, отправьте либо True либо False")

@router.message(IsAdmin(), state=admin.truthgame_media_statement)
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
    await state.update_data(truthgamestatement=text)
    await state.update_data(truthgamestatementasset=media_id)


    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    bool = data['truthgamebool']
    postgressdata = await data_getter(f"select name from assets where name like '%truthgame%'")
    count = len(postgressdata)+1
    print(postgressdata)
    tagdata = list()
    for everytag in postgressdata:
        tagdata.append(everytag[0])
    print(tagdata)
    tag = f'truthgame_{count}'
    while tag in tagdata:
        count+=1
        tag = f'truthgame_{count}'
        print(tag)
    print(tag)
    await state.update_data(truthgame_tag=tag)
    await state.update_data(tagcount=count)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))

    await message.answer("Опровержение \nОтправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.truthgame_media_rebuttal)


@router.message(IsAdmin(), state=admin.truthgame_media_rebuttal)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        media_id = message.video.file_id
    except:
        try:
            media_id = message.photo[0].file_id
        except:
            await message.answer("Не вижу медиа")
    st_text = data['truthgamestatement']
    st_asset = data['truthgamestatementasset']
    reb_text = message.html_text
    reb_asset = media_id
    tag_count=data['tagcount']
    tag=data['truthgame_tag']
    isTrue=data['truthgamebool']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))

    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          f"Игра в правду - Запись в базу данных \n {reb_asset} , {tag}")
    # await sql_safe_update('assets', {"t_id": media_id}, {'name': f"statement_{surname}_{count}"})
    try:
        await data_getter(
            f"insert into assets(t_id,name) values('{st_asset}', '{tag}'); commit;")
        await data_getter(
            f"insert into assets(t_id,name) values('{reb_asset}', 'tgame_reb_{tag_count}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{st_text}', '{tag}'); commit;")
        await data_getter(
            f"insert into texts(text,name) values('{reb_text}', 'tgame_reb_{tag_count}'); commit;")
        await data_getter(
            f"insert into truthgame(truth,asset_name,text_name,belivers,nonbelivers,rebuttal,reb_asset_name) values ({isTrue},'{tag}','{tag}', 1,1,'tgame_reb_{tag_count}','tgame_reb_{tag_count}'); commit; ")
    except Exception as ex:
        await logg.admin_logs(message.from_user.id, message.from_user.username,
                              f"Ошибка или ложь(пропагандисты) - Запись в базу данных" )
        await message.answer(str(ex))
    await message.answer(f"Добавлено новая пара для игры в правду под тегами {tag}/tgame_reb_{tag_count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()
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

    text=message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%putin_lie_game_%'")
    count = len(postgressdata)+1
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

    text=message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%putin_oldlie_game%'")
    count = len(postgressdata)+1
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

    text=message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%normal_game%'")
    count = len(postgressdata)+1
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
    data=state.get_data()
    truth = data['ucranebool']
    text=message.html_text
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    postgressdata = await data_getter(f"select name from assets where name like '%country_game%'")
    count = len(postgressdata)+1
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
    tag_count=data['tv_tag_count']
    tv_channel=data['tv_channel']

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
                              f"Ошибка или ложь(пропагандисты) - Запись в базу данных" )
        await message.answer(str(ex))
    await message.answer(f"Добавлено новая пара для игры Ложь На ТВ под тегами {tv_channel}_lie_{tag_count}/{tv_channel}_reb_{tag_count}",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.clear()

@router.message(IsAdmin(), (F.text.contains('Удаление медиа из игры')))
async def menu(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))
    await state.set_state(admin.game_deleting)

"""***************************************MASS MEDIA************************************************"""
@router.message(IsAdmin(), (F.text == "Ложь других СМИ 🧮"))
async def admin_home(message: types.Message, state: FSMContext):
    await message.answer("Выберите интересующее вас действие", reply_markup=admin_games_keyboard())
    await state.set_state(admin.mass_media_menu)


@router.message(IsAdmin(), (F.text.contains('Добавить сюжет')), state=admin.mass_media_menu)
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
        if last_tag_numner != 1:
            await query.message.delete()
            keyboard = range(1, last_tag_numner)
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
            keyboard = range(1, last_tag_numner)
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
    caption = message.caption
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
    caption = message.caption
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


@router.message((F.text.contains('Отменить изменения')), state=admin.mass_media_Done)
async def admin_home(message: types.Message, state: FSMContext):
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
        await sql_safe_insert('assets', {'t_id': new_media, 'name': f"{old_media_tag}{last_tag_numner+1}"})
        await sql_safe_insert('assets', {'t_id': new_media_exposure, 'name': f"{old_exposure_tag}{last_tag_numner+1}"})
        await sql_safe_insert('texts', {'text': new_caption, 'name': f"{old_media_tag}{last_tag_numner+1}"})
        await sql_safe_insert('texts', {'text': new_caption_exposure, 'name': f"{old_exposure_tag}{last_tag_numner+1}"})
        await state.set_state(admin.mass_media_menu)
        await message.answer("Сюжет был успешно добавлен в базу", reply_markup=admin_games_keyboard())
    except:
        await message.answer('Упс.. Что-то пошло не так, пожалуйста обратитесь к разработчиками')


@router.message(IsAdmin(), (F.text.contains('Удалить сюжет')), state=admin.mass_media_menu)
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


@router.message(IsAdmin(), (F.text.contains('Редактировать сюжет')), state=admin.mass_media_menu)
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
    await message.answer('Если вы хотите обновить этот сюжет, то пришлите мне новую ложь c описанием', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(state=admin.mass_media_edit_add)
async def admin_home(message: types.Message, state: FSMContext):
    try:
        caption = message.caption
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
    caption = message.caption
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