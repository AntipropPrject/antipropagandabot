from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from DBuse import data_getter, pandas_csv_add
from handlers.admin_hand import admin_home
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state

router = Router()


@router.message(commands=["start"])
async def cmd_start(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="8 лет Украина бомбила Донбасс и убивала там детей"))
    await message.answer("Здравствуйте. Вы решили поговорить о Донбассе, не так ли?",
                         reply_markup=nmarkup.as_markup(resize_keyboard=True,
                                                        input_field_placeholder="Кстати, я разместил тут разные фразы поддержки и советы, как вам?"))



@router.message(F.from_user.id.in_(bata.all_data().admins), commands=["admin"])
async def admin_hi(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(admin_home.admin)
    await message.answer("Добро пожаловать в режим администрации. Что вам угодно сегодня?",
                         reply_markup=main_admin_keyboard())


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
    await message.answer_photo(photo_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True,
                                                                                      input_field_placeholder="Найдите по-настоящему независимые источники"))
