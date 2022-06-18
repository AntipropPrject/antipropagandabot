from aiogram import Router
from aiogram import types

from middleware import CounterMiddleware

router = Router()
router.message.middleware(CounterMiddleware())

@router.message()
async def empty(message: types.Message):
    await message.answer("Неправильная команда, вы можете выбрать ответ на клиаватуре или в опросе.\n\n Если желаете начать сначала - нажмите /start")