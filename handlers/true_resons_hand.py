from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll
from filters.All_filters import OperationWar, WarReason

class truereasons_state(StatesGroup):
    main = State()


router = Router()
router.message.filter(state=truereasons_state)


@router.message(OperationWar(answer='Специальная военная операция (СВО)'), (F.text == 'Продолжай'))
async def reasons_operation(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо -- "война".'))
    nmarkup.row(types.KeyboardButton(text='Нет, это спецоперация.'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('война')))
@router.message(OperationWar(answer='Война / Вторжение в Украину'), (F.text == 'Продолжай'))
async def reasons_war(message: Message, state: FSMContext):
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


