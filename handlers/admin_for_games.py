from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_update, data_getter
from filters.isAdmin import IsAdmin
from keyboards.admin_keys import main_admin_keyboard, games_keyboard
from log import logg
from states.admin_states import admin

router = Router()


@router.message(IsAdmin(),(F.text.contains('Добавить позицию к играм')), state=admin.menu)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вошел в режим редактирования игр")
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=games_keyboard(message.from_user.id))


@router.message(IsAdmin(), (F.text.contains('Ошибка или ложь(пропагандисты)')))
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


@router.message(IsAdmin(), (F.text.contains('Игра в правду')))
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
@router.message(IsAdmin(), (F.text.contains('Путин')))
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


@router.message(IsAdmin(), (F.text.contains('Путин - обещания')))
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

@router.message(IsAdmin(), (F.text.contains('Игра в нормальность')))
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

@router.message(IsAdmin(), (F.text.contains('Украина или нет?')))
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

@router.message(IsAdmin(), (F.text.contains('Ложь по тв')))
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

# @router.message(IsAdmin(), state=admin.game_deleting)
# async def menu(message: types.Message, state: FSMContext):
#     await message