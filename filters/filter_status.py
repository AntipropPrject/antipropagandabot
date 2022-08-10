from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message

from data_base.DBuse import redis_just_one_read


class Status(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        status = await redis_just_one_read('Usrs: admins: state: status:')
        try:
            if '1' in status:
                return True
            else:
                return False
        except TypeError:
            return False


class StatusSpam(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        status = await redis_just_one_read('Usrs: admins: spam: status:')
        try:
            if '1' in status:
                return True
            else:
                return False
        except TypeError:
            return False
