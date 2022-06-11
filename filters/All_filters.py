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


class TVPropagandaFilter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        print('filtering propaganda')
        user_thoughts = await poll_get(f'Start_answers: tv: {message.from_user.id}')
        print(user_thoughts)
        for answ in user_thoughts:
            if self.option == answ:
                return True
        return False

class WebPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, dict]:
        print('filtering web propaganda')
        web_lies_list = await poll_get(f'Start_answers: ethernet: {message.from_user.id}')
        print(web_lies_list)
        bad_lies = ("РИА Новости", "Russia Today",
               "Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews",
               "Телеграм-канал: Война с фейками", "РБК",
               "ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс",
               "Яндекс.Новости", "Никому из них...")
        for bad_lie in bad_lies:
            if bad_lie in web_lies_list:
                return {'web_lies_list': web_lies_list}
        return False


class PplPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, dict]:
        print('filtering ppl')
        ppl_lies_list = await poll_get(f'Start_answers: who_to_trust: {message.from_user.id}')
        print(ppl_lies_list)
        bad_ppl_lies = ("Дмитрий Песков", "Рамзан Кадыров",
               "Сергей Лавров", "Юрий Подоляка", "Владимир Соловьев",
               "Ольга Скабеева")
        for bad_lie in bad_ppl_lies:
            if bad_lie in ppl_lies_list:
                return {'ppl_lies_list': ppl_lies_list}
        return False