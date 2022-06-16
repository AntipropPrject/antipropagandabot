from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from filters.All_filters import option_filter, WarReason, second_donbass_filter
import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll
from filters.All_filters import OperationWar, WarReason
from handlers.nazi_hand import NaziState
from data_base.DBuse import redis_delete_from_list

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
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Защитить русских в Донбассе'))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Денацификация / Уничтожить нацистов'))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await state.set_state(NaziState.main)
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', 'Денацификация / Уничтожить нацистов')
    text = "Кусок про нацистов будет тут"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message(WarReason(answer="Предотвратить вторжение на территорию России или ЛНР/ДНР"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Предотвратить вторжение на территорию России или ЛНР/ДНР")
    text = "Кусок про вторжение тут"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Демилитаризация / Снижение военной мощи"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Демилитаризация / Снижение военной мощи")
    text = "Кусок про демилитаризацию начинается здесь"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Предотвратить размещение военных баз НАТО в Украине"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Предотвратить размещение военных баз НАТО в Украине")
    text = "Кусок про военные базы"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Уничтожить биолаборатории / Предотвратить создание ядерного оружия"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Уничтожить биолаборатории / Предотвратить создание ядерного оружия")
    text = "Кусок про голубей и славянский геном"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Захватить территории Донбасса и юга Украины"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Захватить территории Донбасса и юга Украины")
    text = "Кусок про имперское шило в одном месте."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Сменить власть в Украине"))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Start_answers: Invasion: {message.from_user.id}', "Сменить власть в Украине")
    text = "Кусок про смену власти в Украине."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))