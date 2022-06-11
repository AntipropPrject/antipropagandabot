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

from filters.All_filters import option_filter
from states.donbass_states import donbass_state
from DBuse import data_getter, poll_get
from keyboards.main_keys import filler_kb

router = Router()
router.message.filter(state = donbass_state.after_poll)

@router.message(content_types=types.ContentType.TEXT)
async def final_donbass_poll(message: Message, state=FSMContext):
    options = await poll_get('Donbas: Poll_answers: Final')
    text = data_getter("SELECT text from public.texts WHERE name = 'big_final_donbass';")[0][0]
    await message.answer(text, parse_mode="HTML")
    await message.reply_poll('Вернемся к текущим событиями, или у вас есть что сказать по этой теме?', options, is_anonymous=False, allows_multiple_answers=True)
    await state.clear()
    await message.answer('На этом все, введите /start чтобы начать заново')
