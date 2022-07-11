from aiogram import Bot
from aiogram.dispatcher.filters import BaseFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from typing import Union, Dict, Any

import bata
from data_base.DBuse import poll_get, redis_just_one_read
from handlers import true_resons_hand
from resources.all_polls import welc_message_one, nazizm, donbass_first_poll


class DonbassOptionsFilter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
        for lie in user_lies:
            if int(lie.find(self.option)) != -1:
                return True
        return False


class INFOStateFilter(BaseFilter):
    infostate: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        restate = await redis_just_one_read(f'Usrs: {message.from_user.id}: INFOState:')
        if self.infostate == restate:
            return True
        return False


class PoliticsFilter(BaseFilter):
    title: Union[str]

    async def __call__(self, message: Message) -> bool:
        user_thoughts = await redis_just_one_read(f'Usrs: {message.from_user.id}: Politics:')
        if self.title == user_thoughts:
            return True
        return False


class second_donbass_filter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_lies = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')
        print(user_lies)
        for lie in user_lies:
            if int(lie.find(self.option)) != -1:
                return True
        return False


class TVPropagandaFilter(BaseFilter):
    option: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        user_thoughts = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: tv:')
        for answ in user_thoughts:
            if int(answ.find(self.option)) != -1:
                return True
        return False


class WebPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        web_lies_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: ethernet:')
        bad_lies = ("РИА Новости", "Russia Today", "Министерство обороны РФ",
                    "Телеграм-канал: Война с фейками",
                    "ТАСС / Комсомольская правда / Коммерсантъ / Lenta.ru / Известия")
        for bad_lie in bad_lies:
            if bad_lie in web_lies_list:
                return {'web_lies_list': web_lies_list}
        return False


class PplPropagandaFilter(BaseFilter):

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        ppl_lies_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')
        bad_ppl_lies = ("Дмитрий Песков", "Сергей Лавров",
                        "Маргарита Симоньян", "Владимир Соловьев", "Никита Михалков")
        for bad_lie in bad_ppl_lies:
            if bad_lie in ppl_lies_list:
                return {'ppl_lies_list': ppl_lies_list}
        return False


# Этот можно ифом, но я не знаю насколько там длинная цепочка с переубеждением
class OperationWar(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        war_or_not = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:')
        if int(war_or_not[0].find(self.answer)) != -1:
            return True
        else:
            return False


class WarReason(BaseFilter):
    answer: str

    async def __call__(self, message: Message):
        reason_list = await poll_get(f"Usrs: {message.from_user.id}: Start_answers: Invasion:")
        for thing in reason_list:
            if int(thing.find(self.answer)) != -1:
                return True
        return False


class PutinFilter(BaseFilter):
    async def __call__(self, message: Message):
        if await redis_just_one_read('Usrs: 5306348087: Start_answers: LovePutin') == 'True':
            return True
        else:
            return False


class NaziFilter(BaseFilter):
    answer: Union[str, list]

    async def __call__(self, message: Message):
        list = await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:')
        for thing in list:
            if int(thing.find(self.answer)) != -1:
                return True
        return False


class RusHate_pr(BaseFilter):
    async def __call__(self, message: Message):
        if "📊 Менее 5%" in await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: small_poll:'):
            return True
        else:
            return False


class NotNaziFilter(BaseFilter):
    async def __call__(self, message: Message):
        nazi_answers = await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:')
        if "🙅 Ничего из вышеперечисленного..." in nazi_answers and len(nazi_answers) == 1:
            return True
        else:
            return False


class SubscriberFilter(BaseFilter):
    async def __call__(self, message: Message):
        bot = bata.all_data().get_bot()
        user_channel_status = await bot.get_chat_member(chat_id=bata.all_data().masterchannel,
                                                        user_id=message.from_user.id)
        await bot.session.close()
        if user_channel_status.status not in {'left', 'banned', 'restricted'}:
            return False
        else:
            return True





class ManualFilters:
    def __init__(self, message: Message, state: FSMContext):
        self.message = message
        self.state = state

    async def truereasons(self):
        war_answers = poll_get(f"Usrs: {self.message.from_user.id}: Start_answers: Invasion:")
        if welc_message_one[8] in war_answers:
            await true_resons_hand.reasons_big_bad_nato(self.message, self.state)
        elif welc_message_one[0] in war_answers:
            await true_resons_hand.donbass_big_tragedy(self.message, self.state)
        elif welc_message_one[1] in war_answers:
            await true_resons_hand.prevent_strike_start(self.message, self.state)
        elif welc_message_one[2] in war_answers:
            await true_resons_hand.reasons_denazi(self.message, self.state)
        elif welc_message_one[3] in war_answers:
            await true_resons_hand.reasons_demilitarism(self.message, self.state)
        elif welc_message_one[5] in war_answers:
            await true_resons_hand.reasons_biopigeons(self.message, self.state)


