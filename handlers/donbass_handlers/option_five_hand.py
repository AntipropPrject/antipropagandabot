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
router.message.filter(option_filter(option = 'Это укронацисты стреляют по своим же жителям! Мы же бьем только по военным объектам'), state = donbass_state)


@router.message((F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def casualties_start_point(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'only_war_objects';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
    nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
    nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('российские', 'провокация'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'protection';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
    nmarkup.row(types.KeyboardButton(text="Жертвы среди мирного населения - плохо, но все ради важных целей."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")

@router.message(text_contains=('укронацисты', 'жилых'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def exit_point_one(message: Message, state=FSMContext):
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await state.update_data(live_shield = 'Украинская армия использует население, как живой щит!')
    await message.answer('Что же, я услышал ваш ответ.\nДавайте поговорим об этом позже.', reply_markup=filler_kb(), parse_mode="HTML")

@router.message(text_contains=('жертвы', 'плохо', 'важных'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def exit_point_two(message: Message, state=FSMContext):
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await state.update_data(big_game = 'Помимо защиты жителей Донбасса есть более весомые причины для начала войны.')
    await message.answer('Возможно вы правы. Обязательно обсудим все причины\nА пока вернемся к теме Донбасса',
                         reply_markup=filler_kb(), parse_mode="HTML")

@router.message(text_contains=('ужас', 'следующей', 'теме'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def exit_point_zero(message: Message, state=FSMContext):
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    await state.update_data(live_shield = 'Украинская армия использует население, как живой щит!')
    await message.answer('Полностью разделяю ваши чувства.',
                         reply_markup=filler_kb(), parse_mode="HTML")

