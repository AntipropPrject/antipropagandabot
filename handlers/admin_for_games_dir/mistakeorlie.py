from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import data_getter
from keyboards.admin_keys import game_keys
from log import logg
from states.admin_states import admin

router = Router()
router.message.filter(state=admin)


@router.message((F.text == "Пропагандисты 💢"), state=admin.game_menu)
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ошибка или ложь(пропагандисты) - выбор пропагандиста")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте фамилию пропагандиста без опечаток(ТОЛЬКО ФАМИЛИЮ с БОЛЬШОЙ БУКВЫ)",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie)


@router.message(state=admin.addingMistakeOrLie)
async def menu(message: types.Message, state: FSMContext):
    await state.update_data(surnameOfPerson=message.text)
    await message.answer(
        "Что вы хотите сделать?",
        reply_markup=game_keys())
    await state.set_state(admin.addingMistakeOrLie_adding)


@router.message((F.text == "Добавить сюжет"), state=admin.addingMistakeOrLie_adding)
async def menu(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ошибка или ложь(пропагандисты) - добавление")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer(
        "Отправьте новый медиафайл и текст к посту с необходимой разметкой",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))

    await state.set_state(admin.addingMistakeOrLie_media)


@router.message(state=admin.addingMistakeOrLie_media)
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


@router.message((F.text == "Удалить сюжет"), state=admin.addingMistakeOrLie_adding)
async def menu(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username,
                          "Ошибка или ложь(пропагандисты) - удаление")
    data = await state.get_data()
    tag = data['surnameOfPerson']
    postgresdata = await data_getter(
        f"select asset_name from mistakeorlie where asset_name like '%{tag}%' order by asset_name asc")
    nmrkup = ReplyKeyboardBuilder()
    for i in postgresdata:
        nmrkup.row(types.KeyboardButton(text=i[0]))
    await message.answer(
        "Выберете сюжет, они идут по порядку",
        reply_markup=nmrkup.as_markup(resize_keyboard=True))

    await state.set_state(admin.addingMistakeOrLie_deleting)


@router.message(state=admin.addingMistakeOrLie_deleting)
async def admin_home(message: types.Message, state: FSMContext):
    await state.update_data(media_to_delete=message.text)
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Да"))
    nmrkup.row(types.KeyboardButton(text="Нет"))
    media_id = await data_getter(f"select t_id from assets where name = '{message.text}'")
    print('asdqawddasdad')
    print(media_id)
    print(media_id[0])
    try:
        await message.answer_video(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_photo(media_id[0][0], caption="Посмотрите внимательно. Это сюжет вы хотите удалить?",
                                   reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie_deleting_apply)


@router.message(state=admin.addingMistakeOrLie_deleting_apply)
async def admin_home(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_to_delete']
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    surname = data['surnameOfPerson']
    if message.text == "Да":
        await data_getter(f"delete from mistakeorlie where asset_name = '{media_id}'; commit;")
        await message.answer(f"Медиа под тегом <b>{media_id}</b> удалено из игры ", parse_mode='html',
                             reply_markup=nmrkup.as_markup())
        how_many_rounds = await data_getter(f"select asset_name from mistakeorlie where asset_name like '%{surname}%'")

    elif message.text == "Нет":
        await message.answer("Вернемся назад", reply_markup=nmrkup.as_markup())
    else:
        await message.answer("Что-то не так, попробуйте нажать /start и снова зайти в админку")
    await state.clear()
