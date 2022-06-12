from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from DBuse import poll_get, poll_write
from bata import all_data
from states import welcome_states
from DBuse import sql_safe_select
from states.antiprop_states import propaganda_victim

router = Router()

@router.message()
async def empty(message: types.Message):
    await message.answer("Неправильная команда, вы можете выбрать ответ на клиаватуре или в опросе.\n\n Если желаете начать сначала - нажмите /start")