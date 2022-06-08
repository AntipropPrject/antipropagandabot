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

from states.donbass_states import donbass_state
from DBuse import data_getter, poll_get, poll_write

router = Router()
router.message.filter(state = (donbass_state.eight_years, donbass_state.eight_years_selection))

@router.message(text_contains=('значит'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'donbas_years_add';")[0][0]
    await message.answer(text)

@router.message(text_contains=('знал'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    photo_id = data_getter("SELECT t_id from public.assets WHERE name = 'donbass_chart_2';")[0][0]
    text = data_getter("SELECT text from public.texts WHERE name = 'donbas_years_select';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Получить опрос"))
    await message.answer_photo(photo_id, caption=text, parse_mode="HTML", reply_markup=nmarkup.as_markup(resize_keyboard=True, input_field_placeholder="В истории много странностей, не находите?"))


@router.message(text_contains=('опрос'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years_selection)
    options = await poll_get('Donbas: Poll_answers: Base')
    await message.reply_poll("Отметьте один или более вариантов, с которыми вы согласны или частично согласны", options, is_anonymous=False, allows_multiple_answers=True)


@router.poll_answer(state = donbass_state.eight_years_selection)
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    base_options = await poll_get('Donbas: Poll_answers: Base')
    indexes = poll_answer.option_ids
    print (indexes)
    true_options = list()
    for index in indexes:
        true_options.append(base_options[index])
    print (true_options)
    for true_option in true_options:
        await poll_write(poll_answer.user.id, 'Donbas', true_option)
    await state.set_state(donbass_state.after_poll)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Договорились"))
    await Bot(all_data().bot_token).send_message(poll_answer.user.id, text='Хорошо, давайте разберемся по-порядку.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


