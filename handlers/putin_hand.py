import csv

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll, donbass_second_poll
from filters.All_filters import option_filter, PutinFilter, second_donbass_filter


router = Router()


@router.message(PutinFilter(), (F.text.in_({'Почему бы и нет', "Начнем"})))
async def putin_love_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен, кто, если не Путин?"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Почему бы и нет', "Начнем"})))
async def putin_love_putin(message: Message, state=FSMContext):
    text = "Выберите описание Владимира Путина, которое вы считаете наиболее точным:"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Не лучший президент, но кто, если не Путин?"))
    nmarkup.row(types.KeyboardButton(text="Превосходный лидер и отличный президент"))
    nmarkup.row(types.KeyboardButton(text="Хороший президент, но его указания плохо исполняют"))
    nmarkup.row(types.KeyboardButton(text="Военный преступник"))
    nmarkup.row(types.KeyboardButton(text="Был хорошим раньше"))
    nmarkup.adjust(1,1,1,2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Нет, не согласен.', "Может и есть, но пока их не видно", "Конечно такие люди есть"})))
async def putin_big_love_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_big_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Согласен, кто, если не Путин?") | (F.text == "Не лучший президент, но кто, если не Путин?"))
async def putin_only_one(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_only_one'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Может и есть, но пока их не видно"))
    nmarkup.row(types.KeyboardButton(text="Конечно такие люди есть"))
    nmarkup.row(types.KeyboardButton(text="Не говори так, Путин с нами надолго!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message((F.text == "Хороший президент, но его указания плохо исполняют"))
async def putin_not_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_not_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Скорее да', "Скорее нет"})))
async def putin_game_of_lie(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_game_of_lie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Приступим!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Приступим!") | (F.text == "Продолжаем, давай еще!"))
async def antip_truth_game_start(message: Message, state=FSMContext):
    try:
        count = (await state.get_data())['gamecount']
    except:
        count = 0
