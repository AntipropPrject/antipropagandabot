import csv
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers import true_resons_hand
from handlers import stopwar_hand
from handlers.true_resons_hand import reasons_who_to_blame
from states.donbass_states import donbass_state
from states.main_menu_states import MainMenuStates
from handlers.main_menu_hand import mainmenu_really_menu

flags = {"throttling_key": "True"}
router = Router()

@router.message(commands=["testend"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(stopwar_hand.StopWarState.main)
@router.message(commands=["testnazi"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await true_resons_hand.reasons_denazi(message, state)


@router.message(commands=["mainskip69"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.main)
    await mainmenu_really_menu(message, state)


@router.message(commands=["teststrike"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await true_resons_hand.prevent_strike_start(message, state)


@router.message(commands=["putest"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await reasons_who_to_blame(message, state)


@router.message(commands=["donbass"], flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(donbass_state.eight_years)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное? 🤔'))
    nmarkup.adjust(1, 2)
    await message.answer('Вход в донбасс', reply_markup=nmarkup.as_markup(resize_keyboard=True))




class add_id(StatesGroup):
    one = State()


@router.message(commands=["load"], flags=flags)
async def csv_dump(message: Message, state: FSMContext):
    await message.answer("Отправьте фото с тегом")
    await state.set_state(add_id.one)


@router.message(state=add_id.one, flags=flags)
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

