import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.filters.command import CommandStart, CommandObject, Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, User, CallbackQuery, Update, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_is_done, mongo_stat, mongo_stat_new, advertising_value
from data_base.DBuse import mongo_user_info, sql_safe_select, mongo_ez_find_one, redis_just_one_write
from day_func import day_count
from filters.isAdmin import IsAdmin
from handlers.shop import shop_welcome
from handlers.story import true_resons_hand
from handlers.story import main_menu_hand
from handlers.story.anti_prop_hand import antip_what_is_prop
from handlers.story.donbass_hand import donbass_big_tragedy
from handlers.story.main_menu_hand import mainmenu_really_menu
from handlers.story.preventive_strike import prevent_strike_any_brutality
from handlers.story.putin_hand import stopwar_start
from handlers.story.stopwar_hand import stopwar_first_manipulation_argument
from handlers.story.true_goals_hand import goals_war_point_now
from handlers.story.true_resons_hand import reasons_who_to_blame
from handlers.story.welcome_messages import message_2
from handlers.story.welcome_stories import start_how_to_manipulate
from resources.variables import all_test_commands
from states.antiprop_states import propaganda_victim
from states.main_menu_states import MainMenuStates
from states.true_goals_states import TrueGoalsState
from states.welcome_states import start_dialog
from utilts import MasterCommander

flags = {"throttling_key": "True"}
router = Router()


@router.message(CommandStart(command_magic=F.args), flags=flags)
async def adv_company(message: Message, bot: Bot, state: FSMContext, command: CommandObject):
    asyncio.create_task(advertising_value(command.args, message.from_user))
    await commands_start(message, bot, state)


@router.callback_query(text="restarting")
@router.message(commands=['start', 'restart'], state='*', flags=flags)
async def commands_start(update: Message | CallbackQuery, bot: Bot, state: FSMContext):  # Первое сообщение
    user_obj = update.from_user
    if isinstance(update, CallbackQuery):
        await update.answer()
    else:
        user_info = await mongo_ez_find_one('database', 'userinfo', {'_id': user_obj.id})
        if user_info:
            if user_info.get('datetime_end', False) is None:
                inmarkup = InlineKeyboardBuilder()
                inmarkup.add(types.InlineKeyboardButton(text="♻️ Начать заново! ♻️", callback_data="restarting"))
                text = await sql_safe_select("text", "texts", {"name": "restart_are_you_sure"})
                await update.answer(text, reply_markup=inmarkup.as_markup())
                return
        else:
            await MasterCommander(bot, 'chat', user_obj.id).rewrite({})
    asyncio.create_task(start_base(user_obj))
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Начнём 🇷🇺🇺🇦"))
    markup.row(types.KeyboardButton(text="А с чего мне тебе верить? 🤔"))
    markup.row(types.KeyboardButton(text="Сначала расскажи про 50 000 руб за ложь 💵"))
    text = await sql_safe_select("text", "texts", {"name": "start_hello"})
    await bot.send_message(user_obj.id, text,
                           reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(start_dialog.big_story)


async def start_are_you_sure(message):
    text = await sql_safe_select("text", "texts", {"name": "restart_are_you_sure"})
    await redis_just_one_write(f'Usrs: {message.from_user.id}: want_to_restart', 'True', ttl=120)



async def start_base(user: User):
    await day_count()
    user_id = user.id  # if old is None:
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {user.id}:*"):
        redis.delete(key)
    await mongo_stat(user_id)
    await mongo_stat_new(user_id)
    await mongo_user_info(user_id, user.username)
    if await mongo_ez_find_one('database', 'userinfo', {'_id': user.id, 'ref_parent': {'$exists': True},
                                                        'datetime_end': {'$eq': None}}):
        await redis_just_one_write(f'Usrs: {user.id}: Ref', 1)


@router.message(commands=['menu'], flags=flags)
async def commands_start_menu(message: types.Message, state: FSMContext):
    if await mongo_is_done(message.from_user.id):
        await state.set_state(MainMenuStates.main)
        await main_menu_hand.mainmenu_really_menu(message, state)
    else:
        await message.answer('Эта команда будет доступна только после первого прохождения бота')


@router.message(IsAdmin(level=['Тестирование']), commands=["testend"], flags=flags)
async def cmd_testend(message: Message, state: FSMContext):
    await stopwar_first_manipulation_argument(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["testnazi"], flags=flags)
async def cmd_testnazi(message: Message, state: FSMContext):
    await true_resons_hand.reasons_denazi(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["mainskip69"], flags=flags)
async def cmd_mainskip(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.main)
    await mainmenu_really_menu(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["teststrike"], flags=flags)
async def cmd_teststrike(message: Message, state: FSMContext):
    await prevent_strike_any_brutality(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["putest"], flags=flags)
async def cmd_putest(message: Message, state: FSMContext):
    await reasons_who_to_blame(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["proptest"], flags=flags)
async def cmd_putest(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.start)
    await antip_what_is_prop(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["donbass"], flags=flags)
async def cmd_donbass(message: Message, state: FSMContext):
    await donbass_big_tragedy(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["teststop"], flags=flags)
async def cmd_donbass(message: Message, state: FSMContext):
    await stopwar_start(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["test_reasons"], flags=flags)
async def commands_test_reasons(message: Message, bot: Bot, state: FSMContext):
    await message_2(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=['polls_start'], flags=flags)
async def command_polls_start(message: Message, state: FSMContext):
    await state.set_state(start_dialog.big_story)
    await start_how_to_manipulate(message)


@router.message(IsAdmin(level=['Тестирование']), commands=['test_goals'], flags=flags)
async def command_test_goals(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.main)
    await goals_war_point_now(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=['shop'], flags=flags)
async def command_shop(message: Message, state: FSMContext):
    await shop_welcome(message, state)


@router.message(IsAdmin(level=['Тестирование']), commands=["commands_сlear"], flags=flags)
async def commands_restore(message: Message, bot: Bot, state: FSMContext):
    await MasterCommander(bot, 'chat', message.from_user.id).clear()


@router.message(IsAdmin(level=['Тестирование']), commands=["commands_restore"], flags=flags)
async def commands_restore(message: Message, bot: Bot, state: FSMContext):
    await MasterCommander(bot, 'chat', message.from_user.id).add(all_test_commands)
