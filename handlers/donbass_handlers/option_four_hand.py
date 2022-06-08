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
router.message.filter(option_filter(option = 'Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко'), state = donbass_state)

@router.message((F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def eight_years_add_point(message: Message, state=FSMContext):
    #video_id =
    await state.update_data(nazi = 'В Украине процветает неонацизм и геноцид русскоязычного населения')
    text = 'Считать, что люди заслуживают смерти только потому, что у них есть украинский паспорт — и есть нацизм.\n' \
           'В любом случае этот хэндлер будет готов принять любой сценарий, но пока что перейдите к следующей части.'
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")



