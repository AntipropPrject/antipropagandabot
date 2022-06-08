from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
from typing import Union

from DBuse import poll_get


class option_filter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        print ('filtering')
        user_lies = await poll_get(f'Poll_answers: Donbas: {message.from_user.id}')
        print (user_lies)
        for lie in user_lies:
            print (lie)
            if self.option == lie:
                print ('true')
                return True
        return False