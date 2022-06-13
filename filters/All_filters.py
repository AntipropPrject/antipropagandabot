from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
from typing import Union, Dict, Any
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
        user_thoughts = await poll_get(f'Start_answers: tv: {message.from_user.id}')
        for answ in user_thoughts:
            if self.option == answ:
                return True
        return False

class WebPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        web_lies_list = await poll_get(f'Start_answers: ethernet: {message.from_user.id}')
        bad_lies = ("РИА Новости", "Russia Today",
               "Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews",
               "Телеграм-канал: Война с фейками", "РБК",
               "ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс",
               "Яндекс.Новости")
        for bad_lie in bad_lies:
            if bad_lie in web_lies_list:
                print("ОН ВЕРНУЛСЯ")
                return {'web_lies_list': web_lies_list}
        return False


class PplPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        ppl_lies_list = await poll_get(f'Start_answers: who_to_trust: {message.from_user.id}')
        bad_ppl_lies = ("Дмитрий Песков", "Рамзан Кадыров",
               "Сергей Лавров", "Юрий Подоляка", "Владимир Соловьев",
               "Ольга Скабеева")
        for bad_lie in bad_ppl_lies:
            if bad_lie in ppl_lies_list:
                return {'ppl_lies_list': ppl_lies_list}
        return False