from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, loggers
from aiogram.dispatcher.flags.getter import get_flag
from aiogram.types import Message
from cachetools import TTLCache

from bata import all_data
from data_base.DBuse import mongo_ez_find_one, mongo_update, add_current_user

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
        user_info = await mongo_ez_find_one('database', 'userinfo', {'_id': event.from_user.id})
        if user_info:
            if not user_info.get('datetime_end'):
                add_current_user(event.from_user.id)
            if user_info.get('is_ban'):
                await mongo_update(user_info.get('_id'), 'userinfo', 'is_ban', value=False)
        else:
            add_current_user(event.from_user.id)
        if throttling_key is not None and throttling_key in self.caches:
            if event.chat.id in self.caches[throttling_key]:
                loggers.event.info('Throttled')
                return
            else:
                self.caches[throttling_key][event.chat.id] = None
        return await handler(event, data)
