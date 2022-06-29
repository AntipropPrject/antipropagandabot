from aiogram import Router
from aiogram import types

from filters.filter_status import Status
from middleware import CounterMiddleware

router = Router()
router.message.middleware(CounterMiddleware())


@router.message(Status())
async def tec_mode(message: types.Message):
    await message.answer("Приносим свои извинения 🙏\n\n"
                         "В данный момент на сервере ведутся технические работы\n\n"
                         "Попробуйте написать мне, примерно, через 5-10 минут 😊")