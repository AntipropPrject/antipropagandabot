from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache
from bata import all_data

THROTTLE_TIME = all_data().get_THROTTLE_TIME()


class CounterMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.count = 1
        self.cache = TTLCache(maxsize=100, ttl=THROTTLE_TIME)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if self.count >= 2:
            count = self.count
        try:
            if str(data['event_from_user'].id)+str(data['event_router']) in str(self.cache['user_id']):
                self.count +=1

        except:
            self.cache['user_id'] = str(data['event_from_user'].id)+str(data['event_router'])
            return await handler(event, data)


