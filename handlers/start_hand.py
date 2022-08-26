import asyncio

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.filters.command import CommandStart, CommandObject
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_is_done, mongo_stat, mongo_stat_new
from data_base.DBuse import mongo_user_info, sql_safe_select, advertising_value, mongo_ez_find_one, redis_just_one_write
from day_func import day_count
from handlers.story import true_resons_hand
from handlers.story import main_menu_hand
from handlers.story.putin_hand import stopwar_start
from handlers.story.stopwar_hand import stopwar_first_manipulation_argument
from handlers.story.true_resons_hand import reasons_who_to_blame
from states.donbass_states import donbass_state
from states.main_menu_states import MainMenuStates
from states.welcome_states import start_dialog

flags = {"throttling_key": "True"}
router = Router()


@router.message(CommandStart(command_magic=F.args), flags=flags)
async def adv_company(message: Message, state: FSMContext, command: CommandObject):
    asyncio.create_task(advertising_value(command.args, message.from_user))
    await commands_start(message, state)


@router.message(commands=['start', 'help', 'restart'], state='*', flags=flags)
async def commands_start(message: Message, state: FSMContext):  # Первое сообщение
    asyncio.create_task(start_base(message))
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Начнём 🇷🇺🇺🇦"))
    markup.row(types.KeyboardButton(text="А с чего мне тебе верить? 🤔"))
    markup.row(types.KeyboardButton(text="Сначала расскажи про 50 000 руб за ложь 💵"))
    text = await sql_safe_select("text", "texts", {"name": "start_hello"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(start_dialog.big_story)


async def start_base(message):
    await day_count()
    user_id = message.from_user.id  # if old is None:
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}:*"):
        redis.delete(key)
    await mongo_stat(user_id)
    await mongo_stat_new(user_id)
    await mongo_user_info(user_id, message.from_user.username)
    if await mongo_ez_find_one('database', 'userinfo', {'_id': message.from_user.id, 'ref_parent': {'$exists': True}}):
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Ref', 1)



@router.message(commands=['menu'], flags=flags)
async def commands_start_menu(message: types.Message, state: FSMContext):
    if await mongo_is_done(message.from_user.id):
        await state.set_state(MainMenuStates.main)
        await main_menu_hand.mainmenu_really_menu(message, state)
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


@router.message(commands=["teststop"], flags=flags)
async def cmd_donbass(message: Message, state: FSMContext):
    await stopwar_start(message, state)