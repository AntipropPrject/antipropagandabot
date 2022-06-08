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
router.message.filter(option_filter(option = 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше'), state = donbass_state)


@router.message((F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def eight_years_add_point(message: Message, state=FSMContext):
    text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
    nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
    nmarkup.row(types.KeyboardButton(text="Оба варианта"))
    nmarkup.adjust(2,1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(content_types=types.ContentType.TEXT)
async def eight_years_add_point(message: Message, state=FSMContext):
    reason = str
    if message.text == "...на ДНР/ЛНР и Крым":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и Крым'
    if message.text == "...вместе с НАТО на Россию":
        reason = 'Если бы мы не напали первыми, то Украина бы напала вместе с НАТО на Россию'
    if message.text == "Оба варианта":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и вместе с НАТО на Россию'
    await state.update_data(war_reasons = reason)
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    video_id = data_getter("SELECT t_id from public.assets WHERE name = 'putin_may';")[0][0]
    text = data_getter("SELECT text from public.texts WHERE name = 'reason_to_war';")[0][0]
    await message.answer_video(video_id, caption=text, reply_markup=filler_kb())