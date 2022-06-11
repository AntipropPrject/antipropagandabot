from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
from typing import Union

from DBuse import poll_get


class option_filter(BaseFilter):
    option: Union[str, list]

    #async def __call__(self, key_one, key_two, message: Message) -> bool:
    async def __call__(self, message: Message, key_one, key_tho) -> bool:
        print('filtering')
        user_lies = await poll_get(f'Donbas: Poll_answers: {message.from_user.id}')
        #user_lies = await poll_get(f'{key_one}: {key_two}: {message.from_user.id}')
        print(user_lies)
        for lie in user_lies:
            print (lie)
            if self.option == lie:
                print('true')
                return True
        return False


