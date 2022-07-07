import asyncio

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import data_getter, sql_safe_select, sql_safe_update, redis_just_one_write, poll_write
from data_base.DBuse import redis_delete_from_list
from filters.MapFilters import OperationWar, WarReason
from handlers import anti_prop_hand
from handlers.nazi_hand import NaziState
from handlers.preventive_strike import PreventStrikeState
from handlers.putin_hand import StateofPutin
from resources.all_polls import welc_message_one
from states.main_menu_states import MainMenuStates
from stats.stat import mongo_update_stat
from utilts import simple_media


router = Router()
router.message(flags={"throttling_key": "True"}).filter(state=MainMenuStates)


@router.message((F.text == 'Перейти в главное меню 👇') | (F.text == 'Вернуться в Базу Лжи 👈'))
async def mainmenu_really_menu(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_really_menu'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="База Лжи 👀"))
    nmarkup.row(types.KeyboardButton(text="Мини-игры 🎲"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Перейти в главное меню 👇'))
async def mainmenu_baseoflie(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_baseoflie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Трупы в Буче шевелятся 🧎‍♂️"))
    nmarkup.add(types.KeyboardButton(text="Распятый мальчик ☦️"))
    nmarkup.row(types.KeyboardButton(text="Ложь по ТВ 📺"))
    nmarkup.add(types.KeyboardButton(text="Ложь прочих СМИ 👀"))
    nmarkup.add(types.KeyboardButton(text="Ложь политиков и пропагандистов 🗣"))
    nmarkup.add(types.KeyboardButton(text="Обещания Путина 🗣"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Распятый мальчик ☦️'), state=MainMenuStates.baseoflie)
async def mainmenu_crossed_boy_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, 'mainmenu_crossed_boy_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'), state=MainMenuStates.crossed_boy)
async def mainmenu_crossed_boy_2(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_crossed_boy_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай ⏳'), state=MainMenuStates.crossed_boy)
async def mainmenu_crossed_boy_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_crossed_boy_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Трупы в Буче шевелятся 🧎‍♂️'), state=MainMenuStates.baseoflie)
async def mainmenu_bucha_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.about_bucha)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В чём подвох? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Я заметил(а)! 😯"))
    await simple_media(message, 'mainmenu_bucha_1', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'В чём подвох? 🤔') | (F.text == 'Я заметил(а)! 😯')), state=MainMenuStates.about_bucha)
async def mainmenu_bucha_2(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_bucha_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_bucha_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=MainMenuStates.about_bucha)
async def mainmenu_bucha_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_bucha_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)



