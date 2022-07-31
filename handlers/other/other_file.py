import asyncio

from aiogram import Router
from aiogram import types

flags = {"throttling_key": "True"}
router = Router()


@router.message()
async def empty(message: types.Message):
    if str(message.content_type) == 'pinned_message':
        await asyncio.sleep(0.8)
        await message.delete()
    else:
        await message.answer(
            "Неправильная команда, вы можете выбрать ответ на клиаватуре или в опросе.\n\n Если желаете начать сначала - нажмите /start")
