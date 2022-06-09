import asyncio
import pathlib

from psycopg2 import sql
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message, PollAnswer
from bata import all_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from filters.donbas_filters import option_filter
from states.donbass_states import donbass_state
from DBuse import data_getter, redis_pop
from keyboards.main_keys import filler_kb

router = Router()
router.message.filter(state = propaganda_victim)

#Подразумевается, что человеку был присвоен статус "жертва пропаганды", после чего он нажал на кнопку "Поехали!".
#Файл временно в за



@router.message(PropagandaFilter("Скорее да"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'rather_yes_TV';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup())


@router.message(PropagandaFilter("Да, полностью доверяю"), (F.text == 'Поехали!'))
async def antiprop_all_yes_start(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'antip_all_yes_TV';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await message.answer(text, reply_markup=nmarkup.as_markup())


@router.message(PropagandaFilter("Да, полностью доверяю"), (F.text == 'Продолжай!'))
async def antiprop_all_yes_second(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'antip_all_yes_TV_2';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup())


@router.message(PropagandaFilter("Скорее нет"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'rather_no_TV';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup())

@router.message(PropagandaFilter("Нет, не верю ни слову"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'all_no_TV';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup())

@router.message((F.text @ ('Открой мне глаза 👀', "Ну удиви меня 🤔"))
async def eight_years_add_point(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'big_pile_of_lies';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text)

