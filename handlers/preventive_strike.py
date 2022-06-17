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


class PreventStrikeState(StatesGroup):
    main = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()


router = Router()
router.message.filter(state=PreventStrikeState)



@router.message((F.text == 'Давай разберем'))
async def prevent_strike_any_brutality(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_any_brutality'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Каким образом?'))
    nmarkup.row(types.KeyboardButton(text='Ну попробуй'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Каким образом?', 'Ну попробуй'})))
async def prevent_strike_some_days(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_some_days'})
    await state.set_state(PreventStrikeState.q1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Какие?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Какие?'})), state=PreventStrikeState.q1)
async def prevent_strike_q1(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного'))
    await state.set_state(PreventStrikeState.q2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Да, это странно', 'Ничего подозрительного'})), state=PreventStrikeState.q2)
async def prevent_strike_q2(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.q3)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Да, это странно', 'Ничего подозрительного'})), state=PreventStrikeState.q3)
async def prevent_strike_q3(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.q4)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message((F.text.in_({'Да, это странно', 'Ничего подозрительного'})), state=PreventStrikeState.q4)
async def prevent_strike_q4(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q4'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message((F.text.in_({'Да, это странно', 'Ничего подозрительного'})), state=PreventStrikeState.main)
async def prevent_strike_now_you(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_now_you'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, превентивный удар -- лишь повод'))
    nmarkup.row(types.KeyboardButton(text='Я и так не верил(а), что Украина готовит нападение'))
    nmarkup.row(types.KeyboardButton(text='Нет, это настоящая причина начала военных действий'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.in_({'Да, превентивный удар -- лишь повод', 'Я и так не верил(а), что Украина готовит нападение'}))
async def prevent_strike_hilter_allright(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_hilter_allright'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Нет, продолжим разговор'))
    nmarkup.row(types.KeyboardButton(text='Да, хочу'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Нет, это настоящая причина начала военных действий')
async def prevent_strike_hilter_did_it(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_hilter_did_it'})
    await state.set_state(true_resons_hand.truereasons_state.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Нет, продолжим разговор'))
    nmarkup.row(types.KeyboardButton(text='Да, хочу'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('продолжим'))
async def prevent_strike_end_point(message: Message, state: FSMContext):
    text = 'Договорились. У нас еще есть что обсудить.'
    await state.set_state(true_resons_hand.truereasons_state.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='И что дальше?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Да, хочу')
async def prevent_strike_will_show(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_will_show'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а)'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.in_({'Посмотрел(а)', '😁', '🙂', '😕', 'Достаточно, продолжим'}))
async def prevent_strike_memes(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['lgamecount']
    except:
        count = 0
    try:
        count += 1
        media = await sql_safe_select('t_id', 'assets', {'name': f'prevent_strike_meme_{count}'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text='😁'))
        nmarkup.row(types.KeyboardButton(text='🙂'))
        nmarkup.row(types.KeyboardButton(text='😕'))
        nmarkup.row(types.KeyboardButton(text='Достаточно, продолжим'))
        try:
            await message.answer_photo(media, reply_markup=nmarkup.as_markup(resize_keyboard=True))
        except:
            await message.answer_video(media, reply_markup=nmarkup.as_markup(resize_keyboard=True))
        await state.update_data(lgamecount=count)
    except:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text='Да, давай продолжим'))
        await message.answer('В моем хранилище закончились мемы по этому поводу, но вы можете легко найти новые в интернете.\nГотовы продолжить?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))

