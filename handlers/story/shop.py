from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import data_getter, sql_safe_select, mongo_game_answer
from filters.MapFilters import PutinFilter
from handlers.story.stopwar_hand import StopWarState
from utilts import simple_media


class Shop(StatesGroup):
    main = State()
    game1 = State()
    game2 = State()
    final = State()


flags = {"throttling_key": "True"}
router = Router()


@router.message(commands=['start2'], flags=flags)
async def putin_love_putin(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='started_putin', value='Да')
    await state.set_state(Shop.main)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), кто, если не Путин? 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен 🙅‍♂️"))
    await simple_media(message, tag='putin_love_putin', reply_markup=nmarkup.as_markup(resize_keyboard=True))