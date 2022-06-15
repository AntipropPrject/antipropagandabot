import csv

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll, donbass_second_poll
from filters.All_filters import option_filter, PutinFilter, second_donbass_filter


router = Router()


@router.message(PutinFilter(), (F.text.in_({'Почему бы и нет', "Начнем"})))
async def putin_love_putin(message: Message, state=FSMContext):
    pass
