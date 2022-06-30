from aiogram import Router
from aiogram import types

flags = {"throttling_key": "True"}
router = Router()


@router.message(flags=flags)
async def empty(message: types.Message):
    await message.answer("Неправильная команда, вы можете выбрать ответ на клиаватуре или в опросе.\n\n Если желаете начать сначала - нажмите /start")