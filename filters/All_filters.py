from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
from typing import Union, Dict, Any
from DBuse import poll_get


class option_filter(BaseFilter):
    option: Union[str, list]

    #async def __call__(self, key_one, key_two, message: Message) -> bool:
    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Donbass_polls: First: {message.from_user.id}')
        #user_lies = await poll_get(f'{key_one}: {key_two}: {message.from_user.id}')
        for lie in user_lies:
            if self.option == lie:
                return True
        return False

class second_donbass_filter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Donbass_polls: Second: {message.from_user.id}')
        print(user_lies)
        for lie in user_lies:
            if self.option == lie:
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

#Этот можно ифом, но я не знаю насколько там длинная цепочка с переубеждением
class OperationWar(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        war_or_not = await poll_get(f'Start_answers: Is_it_war: {message.from_user.id}')
        print('HELLO WORLD OF BUGS', war_or_not)
        if war_or_not[0] == self.answer:
            return True
        else:
            return False


class WarReason(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        reason_list = await poll_get(f"Start_answers: Invasion: {message.from_user.id}")
        if self.answer in reason_list:
            return True
        else:
            return False


class PutinFilter(BaseFilter):
    async def __call__(self, message: Message):
        if 'Владимир Путин' in await poll_get(f'Start_answers: who_to_trust: {message.from_user.id}'):
            return True
        else:
            return False