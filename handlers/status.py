from aiogram import Router
from aiogram import types

from filters.filter_status import Status
from middleware import CounterMiddleware
from middleware.trottling import ThrottlingMiddleware

flags = {"throttling_key": "True"}
router = Router()


@router.message(Status(), flags=flags)
async def tec_mode(message: types.Message):
    await message.answer("Приносим свои извинения 🙏\n\n"
                         "В данный момент на сервере ведутся технические работы\n\n"
                         "Попробуйте написать мне через 5-10 минут 😊")