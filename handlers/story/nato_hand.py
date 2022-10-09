import asyncio
from typing import List

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import poll_get, redis_just_one_read, sql_select_row_like, mongo_game_answer, mongo_count_docs, \
    redis_just_one_write, mongo_select, mongo_ez_find_one
from data_base.DBuse import sql_safe_select, data_getter
from filters.MapFilters import WebPropagandaFilter, PplPropagandaFilter, \
    NotYandexPropagandaFilter
from filters.isAdmin import IsAdmin
from handlers.story import true_resons_hand
from keyboards.map_keys import antip_killme_kb
from resources.all_polls import antip_q1_options, antip_q2_options, antip_q3_options
from resources.variables import release_date
from states.antiprop_states import propaganda_victim
from states.true_goals_states import TrueGoalsState, WarGoalsState
from utilts import simple_media, dynamic_media_answer, simple_media_bot, simple_video_album, CoolPercReplacer

from states.nato_states import Nato_states

flags = {"throttling_key": "True"}
router = Router()


# router.message.filter(state=Nato_states)


@router.message(commands='nato')
@router.message((F.text.contains('Хорошо, обсудим 💂')) , flags=flags,
                state=WarGoalsState.donbas_enter)
async def nato_start(message: Message, bot: Bot, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'nato_start'})
    await state.set_state(Nato_states.nato_start)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text="Интересно 🙂"))
    nmarkap.row(types.KeyboardButton(text="Ну, попробуй 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Интересно')) | (F.text.contains('Ну, попробуй')), flags=flags,
                state=Nato_states.nato_start)
async def nato_first_poll(message: Message, bot: Bot, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'first_poll'})
    await state.set_state(Nato_states.first_poll)
    nmarkap = ReplyKeyboardBuilder()
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))
    poll_options = ['0 раз', '1 раз', '2 разa', '3 разa', ]
    await message.answer_poll("Сколько раз?",
                              explanation_parse_mode="HTML",
                              options=poll_options, correct_option_id=0, is_anonymous=False, type='quiz',
                              reply_markup=ReplyKeyboardRemove())


@router.poll_answer(state=Nato_states.first_poll, flags=flags)
async def poll_answer(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='nato_poll_answer',
                                value=poll_answer.option_ids[0])
    right_answers = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 0})
    answer_1 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 1})
    answer_2 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 2})
    answer_3 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 3})
    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': {'$exists': True}})
    await state.set_state(Nato_states.poll_answer)
    await state.update_data(nato_poll_answer=poll_answer.option_ids[0])

    result = (right_answers * 100) / all_answers  # TODO test this percentage
    result_1 = (answer_1 * 100) / all_answers
    result_2 = (answer_2 * 100) / all_answers
    result_3 = (answer_3 * 100) / all_answers

    print(f'all {all_answers}')
    print(f'right {right_answers}')

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, согласен(а) 👍"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет, не согласен(а) 👎"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀"))
    nmarkup.adjust(2, 1)
    text = await sql_safe_select('text', 'texts', {'name': 'nato_poll_answer'})
    text = text.replace("AA", f"{str(result)[:-2]}")
    text = text.replace("BB", f"{str(result_1)[:-2]}")
    text = text.replace("CC", f"{str(result_2)[:-2]}")
    text = text.replace("DD", f"{str(result_3)[:-2]}")
    print(all_answers)
    print(right_answers)
    await bot.send_message(text=text, chat_id=poll_answer.user.id, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(
    ((F.text.contains('Скорее да, согласен(а)')) | (F.text.contains('Скорее нет, не согласен(а)')) | (
            F.text == "Затрудняюсь ответить 🤷‍♀")),
    state=Nato_states.poll_answer, flags=flags)
async def nato_other_questions(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_other_questions)
    print("asdasd")
    try:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='nato_other_questions',
                                    value=message.text)
    except Exception:
        print("asdasd")

    answer_1 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Скорее да, согласен(а) 👍'})
    answer_2 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Скорее нет, не согласен(а) 👎'})
    answer_3 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Затрудняюсь ответить 🤷‍♀'})
    print("asdasd")

    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_other_questions': {'$exists': True}})
    if all_answers == 0:
        all_answers = 1
    print(all_answers)
    print(answer_1)
    print(answer_2)
    print(answer_3)
    result_1 = (answer_1 * 100) / all_answers
    result_2 = (answer_2 * 100) / all_answers
    result_3 = (answer_3 * 100) / all_answers
    text = await sql_safe_select('text', 'texts', {'name': 'nato_other_questions'})
    print(text)
    text = text.replace("AA", f"{str(result_1)[:-2]}")
    text = text.replace("BB", f"{str(result_2)[:-2]}")
    text = text.replace("CC", f"{str(result_3)[:-2]}")
    print(text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Страны НАТО что ли? 😏"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(
    ((F.text.contains('Какие? 🤔')) | (F.text.contains('Страны НАТО что ли? 😏'))),
    state=Nato_states.nato_other_questions, flags=flags)
async def nato_countries(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_countries)
    text = await sql_safe_select('text', 'texts', {'name': 'nato_countries'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Но НАТО обещали, что не будут расширяться на восток. Надули? 🤨"))
    nmarkup.row(types.KeyboardButton(text="Так а чего им бояться? Россия не собирается ни на кого нападать. 🤔"))
    nmarkup.row(types.KeyboardButton(text="Продолжим 👉"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Надули? 🤨'),
                state=Nato_states.nato_countries, flags=flags)
async def nato_extention(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()

    data = await state.get_data()
    try:
        nato_buttons = int(data['nato_buttons'])
    except Exception:
        nato_buttons = 0
    if nato_buttons == 0:
        nmarkup.row(types.KeyboardButton(text="Так а чего им бояться? Россия не собирается ни на кого нападать. 🤔"))
    nmarkup.row(types.KeyboardButton(text="Продолжим 👉"))
    await state.update_data(nato_buttons=f'{nato_buttons + 1}')
    text = await sql_safe_select('text', 'texts', {'name': 'nato_extention'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "Вопрос_о_нерасширении_НАТО_на_восток"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Так а чего им бояться? Россия не собирается ни на кого нападать. 🤔'),
                state=Nato_states.nato_countries, flags=flags)
async def nato_propagandons(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    try:
        nato_buttons = int(data['nato_buttons'])
    except Exception:
        nato_buttons = 0
    await state.update_data(nato_buttons=f'{nato_buttons + 1}')
    nmarkup = ReplyKeyboardBuilder()
    if nato_buttons == 0:
        nmarkup.row(types.KeyboardButton(text="Но НАТО обещали, что не будут расширяться на восток. Надули? 🤨"))
    nmarkup.row(types.KeyboardButton(text="Продолжим 👉"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_propagandons'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "Пропаганда_о_том,_что_мы_не_остановимся_на_Украине"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Продолжим 👉'),
                state=Nato_states.nato_countries, flags=flags)
async def nato_not_enemy(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_not_enemy'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "Путин:_НАТО_не_враг,_но_зачем_двигаются_к_нам?"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Продолжай ⏳'),
                state=Nato_states.nato_countries, flags=flags)
async def nato_no_args(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_no_args)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Каким образом? 🤔"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_no_args'})
    await message.answer(text=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Каким образом? 🤔'),
                state=Nato_states.nato_no_args, flags=flags)
async def nato_ucraine_in(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    await state.set_state(Nato_states.nato_ucraine_in)
    nmarkup.row(types.KeyboardButton(text="Взглянуть на карту 🗺"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_ucraine_in'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "Путин_об_Украине_в_НАТО_и_Швеции_с_Финляндией_в_НАТО"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Взглянуть на карту 🗺'),
                state=Nato_states.nato_ucraine_in, flags=flags)
async def nato_map(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_map)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Так если бы Украина вступила в НАТО, они вместе вторглись бы в Крым!  ✈️"))
    nmarkup.row(types.KeyboardButton(text="А Путин объяснил, почему Украина и Финляндия— это разное? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Закончим диалог о НАТО 👉"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_map'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "НАТО,_Россия,_Украина,_Швеция_и_Финляндия_на_карте"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Так если бы Украина вступила в НАТО, они вместе вторглись бы в Крым!  ✈️'),
                state=Nato_states.nato_map, flags=flags)
async def nato_krim_naw(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()

    data = await state.get_data()
    try:
        nato_buttons = int(data['nato_buttons_2'])
    except Exception:
        nato_buttons = 0
    await state.update_data(nato_buttons_2=f'{nato_buttons + 1}')
    if nato_buttons == 0:
        nmarkup.row(types.KeyboardButton(text="А Путин объяснил, почему Украина и Финляндия— это разное? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Закончим диалог о НАТО 👉"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_krim_naw'})
    await message.answer(text=text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)



@router.message(F.text.contains('А Путин объяснил, почему Украина и Финляндия— это разное? 🤔'),
                state=Nato_states.nato_map, flags=flags)
async def nato_diff_with_fin(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()

    data = await state.get_data()
    try:
        nato_buttons = int(data['nato_buttons_2'])
    except Exception:
        nato_buttons = 0
    await state.update_data(nato_buttons_2=f'{nato_buttons + 1}')
    if nato_buttons == 0:
        nmarkup.row(types.KeyboardButton(text="Так если бы Украина вступила в НАТО, они вместе вторглись бы в Крым!  ✈️"))
    nmarkup.row(types.KeyboardButton(text="Закончим диалог о НАТО 👉"))
    text = await sql_safe_select('text', 'texts', {'name': 'nato_diff_with_fin'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': "Путин_объясняет_в_чём_разница_между_Украиной_в_НАТО_и_Финляндией"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(F.text.contains('Закончим диалог о НАТО 👉'),
                state=Nato_states.nato_map, flags=flags)
async def nato_pre_end(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_pre_end)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, это лишь предлог 👌"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет, это настоящая причина 🙅‍♂"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀"))
    nmarkup.adjust(2,1)

    text = await sql_safe_select('text', 'texts', {'name': 'nato_pre_end'})
    await message.answer(text=text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)



@router.message(state=Nato_states.nato_pre_end, flags=flags)
async def nato_end(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(WarGoalsState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    try:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='nato_end',
                                    value=message.text)
    except Exception:
        print("asdasd")

    answer_1 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Скорее да, это лишь предлог 👌'})
    answer_2 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Скорее нет, это настоящая причина 🙅‍♂'})
    answer_3 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Затрудняюсь ответить 🤷‍♀'})

    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_end': {'$exists': True}})
    if all_answers == 0:
        all_answers = 1
    print(all_answers)
    print(answer_1)
    print(answer_2)
    print(answer_3)
    result_1 = (answer_1 * 100) / all_answers
    result_2 = (answer_2 * 100) / all_answers
    result_3 = (answer_3 * 100) / all_answers

    text = await sql_safe_select('text', 'texts', {'name': 'nato_end'})
    text = text.replace("AA", f"{str(result_1)[:-2]}")
    text = text.replace("BB", f"{str(result_2)[:-2]}")
    text = text.replace("CC", f"{str(result_3)[:-2]}")
    await message.answer(text=text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)