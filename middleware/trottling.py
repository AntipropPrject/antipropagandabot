from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, loggers
from aiogram.dispatcher.flags.getter import get_flag
from aiogram.types import Message
from cachetools import TTLCache

from bata import all_data
from data_base.DBuse import mongo_ez_find_one

THROTTLE_TIME = all_data().get_THROTTLE_TIME()


class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "True": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME)
    }

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        redis = all_data().get_data_red()
        redis.set(f"user_last_answer: {event.from_user.id}:", "1", 280)
        if await mongo_ez_find_one('database', 'userinfo', {'_id': event.from_user.id, 'datetime_end': None}):
            redis.set(f"Current_users: {event.from_user.id}", datetime.now().strftime("%m/%d/%Y %H:%M:%S"), 597600)
        if throttling_key is not None and throttling_key in self.caches:
            if event.chat.id in self.caches[throttling_key]:
                loggers.event.info('Throttled')
                return
            else:
                self.caches[throttling_key][event.chat.id] = None
        return await handler(event, data)
