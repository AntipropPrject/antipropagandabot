from aiogram import Router
from aiogram import types

flags = {"throttling_key": "True"}
router = Router()


@router.message(flags=flags)
async def empty(message: types.Message):
    if message.content_type == 'pinned_message':
        await message.delete()
    else:
        await message.answer("Неправильная команда, вы можете выбрать ответ на клиаватуре или в опросе.\n\n Если желаете начать сначала - нажмите /start")