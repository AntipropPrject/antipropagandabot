from typing import Union

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message

import bata
from data_base.DBuse import mongo_select_admin_levels


class IsAdmin(BaseFilter):
    level: Union[list, None]

    async def __call__(self, message: Message) -> bool:
        user_access_levels = await mongo_select_admin_levels(message.from_user.id)
        superadmins = bata.all_data().super_admins
        if message.from_user.id in superadmins:
            return True
        if self.level is None and user_access_levels:
            return True
        elif self.level is not None and user_access_levels is not False:
            if not set(self.level).isdisjoint(set(user_access_levels)):
                return True
        else:
            return False


class IsSudo(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in bata.all_data().super_admins:
            return True
        else:
            return False


class IsKamaga(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id == 784006905:
            return True
        else:
            return False
