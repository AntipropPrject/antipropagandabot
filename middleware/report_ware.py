from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

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
        report_dict = dict()
        report_dict["last_message"] = event.message_id
        report_dict["date_message"] = event.date
        report_dict["user_id"] = event.chat.id
        report_dict["username"] = event.from_user.username
        report_dict["message_from_user"] = event.text
        report_dict["state"] = data.get('raw_state')
        await redis_just_one_write(f'{event.chat.id}: report', str(report_dict).replace("'", '"'))
        return await handler(event, data)
