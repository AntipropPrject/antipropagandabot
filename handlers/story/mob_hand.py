from aiogram import Router, F, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, PollAnswer
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import sql_safe_select, mongo_count_docs
from resources.all_polls import mob_city
from states.mob_states import MobState
from utilts import CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=MobState)
router.poll_answer.filter(state=MobState)


async def mob_lifesaver(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'mob_lifesaver'})
    await state.set_state(MobState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Начнём! 🪖"))
    nmarkup.row(KeyboardButton(text="Не стоит, мне это не интересно 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Не стоит, мне это не интересно 👉", state=MobState.main, flags=flags)
async def mob_how_to_avoid(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'mob_lifesaver'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Хорошо, спасём Вовочку! 🪖"))
    nmarkup.row(KeyboardButton(text="Всё равно продолжить 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Начнём! 🪖', 'Хорошо, спасём Вовочку! 🪖'}), state=MobState.main, flags=flags)
async def mob_save_vv_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.city_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_lifesaver'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Где безопаснее?', mob_city, is_anonymous=False,
                        type='quiz', correct_option_id=0)


@router.poll_answer(MobState.city_poll)
async def mob_size_matters(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.nazi_poll)
    answer = mob_city[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_city_poll', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': {'$exists': True}})
    c_city = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': mob_city[0]})
    c_village = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': mob_city[1]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_size_matters'}), c_all)
    txt.replace('AA', c_city)
    txt.replace('BB', c_village)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Продолжим 👌"))
    await bot.send_message(poll_answer.user.id, txt(), reply_markup=nmarkup.as_markup(), disable_web_page_preview=True)
