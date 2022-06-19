from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
from typing import Union, Dict, Any
from data_base.DBuse import poll_get


class option_filter(BaseFilter):
    option: Union[str, list]

    # async def __call__(self, key_one, key_two, message: Message) -> bool:
    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
        # user_lies = await poll_get(f'{key_one}: {key_two}: {message.from_user.id}')
        for lie in user_lies:
            if self.option == lie:
                return True
        return False


class INFOStateFilter(BaseFilter):
    infostate: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_thoughts = await poll_get(f'Usrs: {poll_answer.user.id}: INFOState:')
        for answ in user_thoughts:
            if self.infostate == answ:
                return True
        return False


class second_donbass_filter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')
        print(user_lies)
        for lie in user_lies:
            if self.option == lie:
                return True
        return False


class TVPropagandaFilter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_thoughts = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: tv:')
        for answ in user_thoughts:
            if self.option == answ:
                return True
        return False


class WebPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        web_lies_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: ethernet:')
        bad_lies = ("РИА Новости", "Russia Today", "Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews",
                    "Телеграм-канал: Война с фейками", "РБК",
                    "ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс", "Яндекс.Новости")
        for bad_lie in bad_lies:
            if bad_lie in web_lies_list:
                print("ОН ВЕРНУЛСЯ")
                return {'web_lies_list': web_lies_list}
        return False


class PplPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        ppl_lies_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')
        bad_ppl_lies = (
        "Дмитрий Песков", "Рамзан Кадыров", "Сергей Лавров", "Юрий Подоляка", "Владимир Соловьев", "Ольга Скабеева")
        for bad_lie in bad_ppl_lies:
            if bad_lie in ppl_lies_list:
                return {'ppl_lies_list': ppl_lies_list}
        return False


# Этот можно ифом, но я не знаю насколько там длинная цепочка с переубеждением
class OperationWar(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        war_or_not = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:')
        if war_or_not[0] == self.answer:
            return True
        else:
            return False


class WarReason(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        reason_list = await poll_get(f"Usrs: {message.from_user.id}: Start_answers: Invasion:")
        if self.answer in reason_list:
            return True
        else:
            return False


class PutinFilter(BaseFilter):
    async def __call__(self, message: Message):
        if 'Владимир Путин' in await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:'):
            return True
        else:
            return False


class NaziFilter(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        print(self.answer)
        if self.answer in await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:'):
            return True
        else:
            return False


class RusHate_pr(BaseFilter):
    async def __call__(self, message: Message):
        if "Менее 5%" in await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: second_poll:'):
            return True
        else:
            return False


class NotNothingNazi(BaseFilter):
    async def __call__(self, message: Message):
        if "Ничего из вышеперечисленного..." in await poll_get(
                f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:'):
            return False
        else:
            return True
