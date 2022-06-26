import csv
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import bata
from data_base.DBuse import data_getter, mongo_select_admins, sql_safe_insert
from handlers import true_resons_hand
from handlers.admin_hand import admin_home
from keyboards.admin_keys import main_admin_keyboard
from middleware import CounterMiddleware
from states.donbass_states import donbass_state
from utilts import simple_media, phoenix_protocol

router = Router()
router.message.middleware(CounterMiddleware())

@router.message(commands=["testnazi"])
async def cmd_start(message: Message, state: FSMContext):
    await true_resons_hand.reasons_denazi(message, state)


@router.message(commands=["teststrike"])
async def cmd_start(message: Message, state: FSMContext):
    await true_resons_hand.prevent_strike_start(message, state)


@router.message(commands=["donbass"])
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(donbass_state.eight_years)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное? 🤔'))
    nmarkup.adjust(1, 2)
    await message.answer('Вход в донбасс', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Вернуться в меню'))
@router.message(commands=["admin"])
async def admin_hi(message: Message, state: FSMContext) -> None:
    admins_list = await mongo_select_admins()
    admins = bata.all_data().super_admins
    for admin in admins_list:
        admins.append(int(admin["_id"]))
    if int(message.from_user.id) in admins:
        await state.clear()
        await state.set_state(admin_home.admin)
        await message.answer("Добро пожаловать в режим администрации. Что вам угодно сегодня?",
                             reply_markup=main_admin_keyboard(message.from_user.id))


class add_id(StatesGroup):
    one = State()


@router.message(commands=["load"])
async def csv_dump(message: Message, state: FSMContext):
    await message.answer("Отправьте фото с тегом")
    await state.set_state(add_id.one)


@router.message(state=add_id.one)
async def csv_dump(message: Message, state: FSMContext):
    ph_id = message.photo[0].file_id
    capt = message.caption

    data = [['t_id', 'name'],
            [ph_id, capt]]

    with open('resources/assets.csv', 'w') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)
    try:
        await message.answer_photo(ph_id, caption=capt)
    except:
        await message.answer_video(ph_id, caption=capt)
        await state.clear()

