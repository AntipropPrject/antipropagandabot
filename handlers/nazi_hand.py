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
from resources.all_polls import donbass_first_poll, donbass_second_poll, nazizm_pr
from filters.All_filters import option_filter, PutinFilter, second_donbass_filter, AntisemitFilter
from handlers.stopwar_hand import StopWarState
from handlers import true_resons_hand

class NaziState(StatesGroup):
    main = State()


router = Router()
router.message.filter(state=NaziState)

class nazizm(StatesGroup):
    start_nazizm = State()


@router.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    nazizm_answers = poll_answer.option_ids
    await state.update_data(nazizm_answers=nazizm_answers)
    if 0 in nazizm_answers:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Давай"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_word"})
        await Bot(bata.all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="А как же неонацизм?"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_negative"})
        await Bot(bata.all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Давай')))
async def nazi_in_masses(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_in_masses"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Давай')))
async def nazi_propaganda(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="А как же неонацизм?"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_propaganda"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('А как же неонацизм?')))
async def nazi_neonazi(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Понятно"))
    markup.row(types.KeyboardButton(text="Черт ногу сломит"))
    markup.row(types.KeyboardButton(text="А можно попроще?"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_neonazi"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Черт ногу сломит')) | (F.text.contains('А можно попроще?')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Так понятнее!"))
    markup.row(types.KeyboardButton(text="Ты всё слишком упрощаешь"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_many_forms"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Ты всё слишком упрощаешь')))
async def nazi_simple(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_simple"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

class poll(StatesGroup):
    poll_answer = State()
@router.message((F.text.contains('Хорошо, продолжим')) | (F.text.contains('Так понятнее!')) | (F.text.contains('Понятно!'))) #AntisemitFilter(if answer != 'Ничего из вышеперечисленного...')
async def nazi_how_many(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_how_many"})
    question = 'Выберите один ответ'
    await message.answer_poll(question=question, options=nazizm_pr, is_anonymous=False)
    await state.set_state(poll.poll_answer)

@router.poll_answer(state=poll.poll_answer)
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    data = await state.get_data()
    pr_answers = poll_answer.option_ids
    if 'Менее 5%' in pr_answers:
        if 'Многие украинцы ненавидят русских только за то, что они русские' not in data['nazizm_answers']:
            markup = ReplyKeyboardBuilder()
            markup.row(types.KeyboardButton(text="Продолжай"))
            text = await sql_safe_select("text", "texts", {"name": "nazi_piechart"})
            media  = await sql_safe_select('t_id', 'assets', {'name': 'nazi_piechart'})
            await Bot(bata.all_data().bot_token).send_photo(chat_id=poll_answer.user.id, photo=media, text=text,
                                                            reply_markup=markup.as_markup(resize_keyboard=True))
    markup_1 = ReplyKeyboardBuilder()
    markup_1.row(types.KeyboardButton(text="Хорошо, продолжим"))
    await Bot(bata.all_data().bot_token).send_message('Спасибо, я запомнил ваш ответ. Позже в разговоре мы его обсудим', reply_markup=markup_1.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Продолжай')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Посмотрел(а)"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_canny"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Посмотрел(а)')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_feels"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

@router.message(AntisemitFilter(answer='В Украине происходит геноцид русскоязычного населения'), (F.text.contains('Хорошо, продолжим')) | (F.text.contains('Продолжим')))
async def nazi_many_forms(message: Message):
    #тут нужно делать либо иф либо еще как-то
    pass