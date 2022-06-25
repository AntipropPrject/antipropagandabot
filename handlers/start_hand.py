import csv
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import bata
from data_base.DBuse import data_getter, mongo_select_admins, sql_safe_insert
from handlers.admin_hand import admin_home
from keyboards.admin_keys import main_admin_keyboard
from middleware import CounterMiddleware
from states.donbass_states import donbass_state
from utilts import simple_media, phoenix_protocol

router = Router()
router.message.middleware(CounterMiddleware())


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


@router.message(text_contains=('бомбила', '8', 'лет'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def eight_years_point(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years)
    photo_id = data_getter("SELECT t_id from public.assets WHERE name = 'donbass_chart_1';")[0][0]
    text = data_getter("SELECT text from public.texts WHERE name = 'donbas_years';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что значит 'гражданские'?"))
    nmarkup.row(types.KeyboardButton(text="Да, знал"))
    nmarkup.row(types.KeyboardButton(text="Нет, не знал"))
    nmarkup.adjust(1, 2)
    try:
        await message.answer_photo(photo_id,
                                   caption=text,
                                   reply_markup=nmarkup.as_markup(resize_keyboard=True,
                                   input_field_placeholder="Найдите по-настоящему независимые источники"))
    except:
        await message.answer_video(photo_id,
                                   caption=text,
                                   reply_markup=nmarkup.as_markup(resize_keyboard=True,
                                   input_field_placeholder="Найдите по-настоящему независимые источники"))


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

