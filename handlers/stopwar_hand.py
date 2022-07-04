from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers.welcome_messages import commands_restart

from data_base.DBuse import sql_safe_select
from stats.stat import mongo_update_stat


class StopWarState(StatesGroup):
    main = State()

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=StopWarState)


@router.message(F.text == "Скорее да ✅", flags=flags)
async def stopwar_rather_yes(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_yes'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_rather_yes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Не знаю 🤷‍♂️", flags=flags)
async def stopwar_idk(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_idk'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_idk'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Скорее нет ❌", flags=flags)
async def stopwar_rather_no(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_no'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не согласен(а) 🙅") | (F.text == "Согласен(а) 👌") | (F.text == "Продолжим 👌"), flags=flags)
async def stopwar_will_it_stop(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_will_it_stop'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, это закончит войну 🕊"))
    nmarkup.row(types.KeyboardButton(text="Не обязательно, новый президент может продолжить войну 🗡"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, это закончит войну 🕊"), flags=flags)
async def stopwar_ofc(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ofc'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не знаю 🤷‍♀️") | (F.text == "Не обязательно, новый президент может продолжить войну 🗡"), flags=flags)
async def stopwar_war_eternal(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_war_eternal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), flags=flags)
async def stopwar_isolation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_isolation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжим👌"), flags=flags)
async def stopwar_stop_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stop_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В результате выборов 📊"))
    nmarkup.row(types.KeyboardButton(text="По иным причинам 💀"))
    nmarkup.row(types.KeyboardButton(text="Сложно сказать 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "В результате выборов 📊") | (F.text == "Сложно сказать 🤔"), flags=flags)
async def stopwar_stolen_votes(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stolen_votes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "По иным причинам 💀"), flags=flags)
async def stopwar_just_a_scene(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_just_a_scene'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "А что главное?"), flags=flags)
async def stopwar_end_it_now(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_it_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что ты предлагаешь ❓ ❓ ❓"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Что ты предлагаешь ❓ ❓ ❓"), flags=flags)
async def stopwar_lets_fight(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_lets_fight'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Спасибо 🤝"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Спасибо 🤝"), flags=flags)
async def stopwar_lets_fight(message: Message):
    await mongo_update_stat(message.from_user.id, 'end')
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_hello_world'})
    text2 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начать общение заново ♻️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await message.answer(text2, disable_web_page_preview=True)


@router.message((F.text == "Начать общение заново ♻️"), flags=flags)
async def stopwar_lets_anew(message: Message, state: Message):
    await commands_restart(message, state)
