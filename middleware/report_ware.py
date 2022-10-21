from functools import wraps
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from data_base.DBuse import redis_just_one_write


class Reportware(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        return await handler(event, data)

class Myware(BaseMiddleware):
    def test_deco(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            print(f'Вызвана {fn}')
            await fn(*args, **kwargs)

        return wrapper

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        print("Before handler")

        result = await handler(event, data)
        print(data)
        print(event.json())
        print("After handler")
        return result
