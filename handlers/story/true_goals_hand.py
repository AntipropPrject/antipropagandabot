import asyncio

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import data_getter, sql_safe_select, redis_just_one_write, poll_write, mongo_game_answer
from data_base.DBuse import redis_delete_from_list
from filters.MapFilters import OperationWar, WarReason, PoliticsFilter
from filters.isAdmin import IsAdmin
from handlers.story import anti_prop_hand
from handlers.story.nazi_hand import NaziState
from handlers.story.preventive_strike import PreventStrikeState
from handlers.story.putin_hand import StateofPutin
from handlers.story.true_resons_hand import TruereasonsState
from resources.all_polls import welc_message_one
from states.donbass_states import donbass_state
from states.true_goals_states import TrueGoalsState
from utilts import simple_media


flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=TrueGoalsState)


@router.message((F.text.contains('нтересно')) | (F.text.contains('скучно')), flags=flags)
async def goals_war_point_now(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_war_point_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

