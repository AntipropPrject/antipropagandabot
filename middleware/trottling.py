import asyncio
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, loggers
from aiogram.dispatcher.flags.getter import get_flag
from aiogram.types import Message
from cachetools import TTLCache

from bata import all_data
from data_base.DBuse import mongo_ez_find_one, mongo_update, add_current_user, redis_just_one_write, mongo_count_docs, \
    redis_just_one_read, sql_safe_select
from resources.variables import release_date

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
        asyncio.create_task(unban(event.from_user.id))

        if not await redis_just_one_read(f"Usrs: {event.from_user.id}: old_checked"):
            if await mongo_count_docs("database", "statistics_new",
                                      {'_id': int(event.from_user.id), 'datetime': {"$lt": release_date['v3']}},
                                      current_version_check=False) and event.text != "/start":
                await you_too_old_boy(event.from_user.id)
            await redis_just_one_write(f"Usrs: {event.from_user.id}: old_checked", "ok")

        report_dict = dict()
        report_dict["last_message"] = event.message_id
        report_dict["date_message"] = event.date
        report_dict["user_id"] = event.chat.id
        report_dict["username"] = event.from_user.username
        report_dict["message_from_user"] = event.text
        report_dict["state"] = data.get('raw_state')
        await redis_just_one_write(f'report: Users: {event.chat.id}', str(report_dict).replace("'", '"'))

        throttling_key = get_flag(data, "throttling_key")
        redis = all_data().get_data_red()
        redis.set(f"user_last_answer: {event.from_user.id}:", "1", 280)
        if throttling_key is not None and throttling_key in self.caches:
            if event.chat.id in self.caches[throttling_key]:
                loggers.event.info('Throttled')
                return
            else:
                self.caches[throttling_key][event.chat.id] = None
        return await handler(event, data)


async def you_too_old_boy(user_id):
    bot = all_data().get_bot()
    text = await sql_safe_select('text', 'texts', {'name': 'you_too_old_boy'})
    await bot.send_message(user_id, text)


async def unban(telegram_id):
    user_info = await mongo_ez_find_one('database', 'userinfo', {'_id': telegram_id})
    if user_info:
        if not user_info.get('datetime_end'):
            add_current_user(telegram_id)
        if user_info.get('is_ban'):
            await mongo_update(user_info.get('_id'), 'userinfo', 'is_ban', value=False)
    else:
        add_current_user(telegram_id)
