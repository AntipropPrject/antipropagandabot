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
from DBuse import data_getter, redis_pop
from keyboards.main_keys import filler_kb

router = Router()
router.message.filter(option_filter(option = 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было'), state = donbass_state)

@router.message((F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def seven_start_point(message: Message, state=FSMContext):
    #video_id =
    await state.update_data(nazi = 'В Украине процветает неонацизм и геноцид русскоязычного населения')
    text = data_getter("SELECT text from public.texts WHERE name = 'war_beginning';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Тут другое дело! Мы шли освобождать их от неонацистов, захвативших власть."))
    nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
    nmarkup.row(types.KeyboardButton(text="Не согласен, в случае нападения на Россию пусть лучше солдаты сложат оружие, зато не будет жертв."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('другое', 'освобождать'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def surrender_endpoint_one(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'putin_24';")[0][0]
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await state.update_data(neonazi = 'В Украине процветает неонационализм и геноцид русского населения.')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('на', 'россию', 'сложат'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def surrender_surrender(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'ideal_world';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
    nmarkup.row(types.KeyboardButton(text="Лучше бы никто ни на кого не нападал."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")

@router.message(text_contains=('Лучше', 'никто', 'кого'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def surrender_endpoint_two(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'sentient_bot';")[0][0]
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")

@router.message(text_contains=('Согласен', 'понимаю', 'начали'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def surrender_endpoint_three(message: Message, state=FSMContext):
    text = 'Рад, что мы пришли к пониманию в этом вопросе. Для украинцев эта война -- Отечественная. Они верят в то, что защищают' \
           'свои земли, свои семьи и свою независимость. Двигаемся дальше.'
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")