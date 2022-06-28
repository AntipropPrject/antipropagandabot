from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message

import bata
from data_base.DBuse import mongo_select_admins


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admins_list = await mongo_select_admins()
        admins = bata.all_data().super_admins
        for admin in admins_list:
            admins.append(int(admin["_id"]))
        if int(message.from_user.id) in admins:
            return True
        else:
            return False


class IsSudo(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in bata.all_data().super_admins:
            return True
        else:
            return False
