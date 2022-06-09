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
router.message.filter(option_filter(option = 'Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны'), state = donbass_state)

@router.message((F.text == 'Договорились') | (F.text == 'Хорошо') | (F.text == 'Понятно'))
async def eight_years_add_point(message: Message, state=FSMContext):
    #video_id =
    text = data_getter("SELECT text from public.texts WHERE name = 'reasons_here';")[0][0]
    data = await state.get_data()
    reason_list = data.values()
    reason_text = ''
    for reason in reason_list:
        reason_text = reason_text + '- ' + reason + '\n'
    text = text + '\n\n' + reason_text + '\n\nОбязательно их все обсудим, а пока что вернемся к теме Донбасса'
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")

