from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import data_getter
from handlers.admin_handlers.admin_for_games import admin_home_games
from keyboards.admin_keys import game_keys
from log import logg
from states.admin_states import admin

router = Router()
router.message.filter(state=admin)




