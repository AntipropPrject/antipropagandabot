import asyncio

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new, mongo_update_stat
from data_base.DBuse import poll_get, poll_write, del_key, data_getter, mongo_game_answer, redis_delete_from_list
from data_base.DBuse import sql_safe_select, mongo_count_docs
from filters.MapFilters import FakeGoals, WarGoals
from filters.MapFilters import OperationWar
from handlers.story.donbass_hand import donbass_big_tragedy
from handlers.story.nato_hand import nato_start
from handlers.story.nazi_hand import NaziState, nazi_first_poll
from handlers.story.preventive_strike import prevent_strike_any_brutality
from middleware.report_ware import Reportware
from resources.all_polls import welc_message_one
from resources.variables import mobilisation_date
from states.stopwar_states import StopWarState
from states.true_goals_states import TrueGoalsState, WarGoalsState
from utils.fakes import fake_message
from utilts import simple_media, CoolPercReplacer, get_time_from_war_started

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=(TrueGoalsState, WarGoalsState))
router.poll_answer.filter(state=TrueGoalsState)
router.message.middleware(Reportware())


@router.message((F.text.contains('на факты 👀')), state=TrueGoalsState.power_change, flags=flags)
async def goals_fact_1(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Например, чтобы не дать перебросить украинские войска в Донбасс ☝"))
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    await simple_media(message, 'goals_fact_1', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Донбасс ☝')), state=TrueGoalsState.goals_fact_1, flags=flags)
async def goals_arg(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    text = await sql_safe_select('text', 'texts', {'name': 'goals_arg'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_1, flags=flags)
async def goals_fact_2(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_2)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_2', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_2, flags=flags)
async def goals_fact_3(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_3)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_3', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_3, flags=flags)
async def goals_fact_4(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_3)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_4', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_3, flags=flags)
async def goals_fact_4(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_4)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_4', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_4, flags=flags)
async def goals_fact_5(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_5)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_5', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_5, flags=flags)
async def goals_fact_6(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_6)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Следующий факт 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно фактов ✋"))
    await simple_media(message, 'goals_fact_6', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('факт 👉')), state=TrueGoalsState.goals_fact_6, flags=flags)
async def goals_fact_7(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.goals_fact_7)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, продолжим 👌"))
    await simple_media(message, 'goals_fact_7', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    import time
    time.sleep(3)
    await message.answer('У меня есть ещё 9 фактов, но разработчики их ещё не успели добавить. Поэтому давайте продолжим. 🙂', reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
