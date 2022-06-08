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
router.message.filter(option_filter(option = 'Так они используют население как живой щит! Поэтому погибают мирные жители'), state = donbass_state)

@router.message((F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def live_shield_start_point(message: Message, state=FSMContext):
    text = 'Еще одна заглушка. Блок про живой щит начинается здесь'
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")

@router.message(text_contains=('сопротивлялись', 'добра'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message, state=FSMContext):
    await state.update_data(surrender = 'Украинцам нужно было просто сдаться, тогда не было бы стольких жертв')
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await message.answer('Об этом чуть позже, но не волнуйтесь: до всего дойдет свой черед.', reply_markup=filler_kb(),
                         parse_mode="HTML")




