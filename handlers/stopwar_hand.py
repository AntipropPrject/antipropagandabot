from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from data_base.DBuse import sql_safe_select
from middleware import CounterMiddleware


class StopWarState(StatesGroup):
    main = State()


router = Router()
router.message.middleware(CounterMiddleware())
router.message.filter(state=StopWarState)


@router.message(F.text == "Скорее да ✅")
async def stopwar_rather_yes(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_yes'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_rather_yes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.row(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Не знаю 🤷‍♂️")
async def stopwar_idk(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_idk'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_idk'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.row(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(F.text == "Скорее нет ❌")
async def stopwar_rather_no(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_no'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не согласен(а) 🙅") | (F.text == "Согласен(а) 👌") | (F.text == "Продолжим 👌"))
async def stopwar_will_it_stop(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_will_it_stop'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, это закончит войну 🕊"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Не обязательно, новый президент может продолжить войну 🗡"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, это закончит войну 🕊"))
async def stopwar_ofc(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ofc'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не знаю 🤷‍♀️") | (F.text == "Не обязательно, новый президент может продолжить войну 🗡"))
async def stopwar_war_eternal(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_war_eternal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"))
async def stopwar_isolation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_isolation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжим👌"))
async def stopwar_stop_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stop_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В результате выборов 📊"))
    nmarkup.row(types.KeyboardButton(text="Сложно сказать 🤔"))
    nmarkup.row(types.KeyboardButton(text="По иным причинам 💀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "В результате выборов 📊") | (F.text == "Сложно сказать 🤔"))
async def stopwar_stolen_votes(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stolen_votes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "По иным причинам 💀"))
async def stopwar_just_a_scene(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_just_a_scene'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "А что главное?"))
async def stopwar_end_it_now(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_it_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что ты предлагаешь ❓ ❓ ❓"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Что ты предлагаешь ❓ ❓ ❓"))
async def stopwar_lets_fight(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_lets_fight'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Спасибо 🤝"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Спасибо 🤝"))
async def stopwar_lets_fight(message: Message):
    text = 'Чтобы рассказать обо мне - отправьте человеку ссылку на Правдобот: \nhttps://t.me/Russia_Ukraine_Bot\n\nИли просто перешлите сообщение ниже.'
    text2 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})
    await message.answer(text, reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
    await message.answer(text2, disable_web_page_preview=True)
