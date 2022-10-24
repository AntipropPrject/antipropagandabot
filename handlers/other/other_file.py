import asyncio

from aiogram import Router, F
from aiogram import types

from handlers.story.nazi_hand import NaziState
from states import welcome_states
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from states.mob_states import MobState
from states.nato_states import Nato_states
from states.true_goals_states import TrueGoalsState
from utilts import simple_media

flags = {"throttling_key": "True"}
router = Router()


@router.message(F.text == 'Продолжить', state=(welcome_states.start_dialog.dialogue_10,
                                               welcome_states.start_dialog.dialogue_9,
                                               welcome_states.start_dialog.dialogue_7,
                                               propaganda_victim.quiz_1,
                                               propaganda_victim.quiz_2,
                                               MobState.mob_wot_mvps,
                                               MobState.nazi_poll,
                                               MobState.mob_is_he_insane,
                                               MobState.city_poll,
                                               MobState.mob_laws_lol,
                                               MobState.mob_street_fighter,
                                               MobState.mob_why_he_did_it,
                                               MobState.jail,
                                               TrueGoalsState.more_goals_poll, Nato_states.first_poll,
                                               NaziState.first_poll, NaziState.rushate, donbass_state.poll
                                               ), flags=flags)
async def all_polls_continue(message: types.Message):
    await message.answer('Чтобы продолжить — отметьте варианты выше и нажмите «ГОЛОСОВАТЬ» или «VOTE»')


@router.message(flags=flags)
async def empty(message: types.Message):
    if str(message.content_type) == 'pinned_message':
        await asyncio.sleep(0.8)
        await message.delete()
    else:
        await simple_media(message, 'other_text')
