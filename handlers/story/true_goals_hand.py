from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_select
from filters.MapFilters import OperationWar
from states.true_goals_states import TrueGoalsState

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


@router.message(OperationWar(answer='(СВО)'), (F.text == "Продолжай ⏳"),
                state=TrueGoalsState.before_shop, flags=flags)
async def goals_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop_operation)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Продолжай ⏳", state=TrueGoalsState.before_shop_operation, flags=flags)
async def goals_not_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_not_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 🤝"))
    nmarkup.add(types.KeyboardButton(text="*презрительно хмыкнуть* 🤨"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
