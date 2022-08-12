from aiogram import Router
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_is_done
from handlers.story import true_resons_hand
from handlers.story.main_menu_hand import mainmenu_really_menu
from handlers.story.stopwar_hand import stopwar_first_manipulation_argument
from handlers.story.true_resons_hand import reasons_who_to_blame
from states.donbass_states import donbass_state
from states.main_menu_states import MainMenuStates

flags = {"throttling_key": "True"}
router = Router()


@router.message(commands=['menu'], flags=flags)
async def commands_start(message: types.Message, state: FSMContext):
    if await mongo_is_done(message.from_user.id):
        await state.set_state(MainMenuStates.main)
        await mainmenu_really_menu(message, state)
    else:
        await message.answer('Эта команда будет доступна только после первого прохождения бота')


@router.message(commands=["testend"], flags=flags)
async def cmd_testend(message: Message, state: FSMContext):
    await stopwar_first_manipulation_argument(message, state)


@router.message(commands=["testnazi"], flags=flags)
async def cmd_testnazi(message: Message, state: FSMContext):
    await true_resons_hand.reasons_denazi(message, state)


@router.message(commands=["mainskip69"], flags=flags)
async def cmd_mainskip(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.main)
    await mainmenu_really_menu(message, state)


@router.message(commands=["teststrike"], flags=flags)
async def cmd_teststrike(message: Message, state: FSMContext):
    await true_resons_hand.prevent_strike_start(message, state)


@router.message(commands=["putest"], flags=flags)
async def cmd_putest(message: Message, state: FSMContext):
    await reasons_who_to_blame(message, state)


@router.message(commands=["donbass"], flags=flags)
async def cmd_donbass(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(donbass_state.eight_years)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное? 🤔'))
    nmarkup.adjust(1, 2)
    await message.answer('Вход в донбасс', reply_markup=nmarkup.as_markup(resize_keyboard=True))
