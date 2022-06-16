import csv

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get, sql_safe_update
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll, donbass_second_poll
from filters.All_filters import option_filter, PutinFilter, second_donbass_filter
from handlers.stopwar_hand import StopWarState
from handlers import true_resons_hand

class NaziState(StatesGroup):
    main = State()


router = Router()
router.message.filter(state=NaziState)


@router.message()
async def empty(message: types.Message, state: FSMContext):
    await state.set_state(true_resons_hand.truereasons_state.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Почему бы и нет"))
    await message.answer("Блок в разработке, возвращаю вас в причины войны", reply_markup=nmarkup.as_markup())