from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import  mongo_count_docs
from data_base.DBuse import sql_safe_select
from keyboards.map_keys import polls_continue_kb
from resources.all_polls import welc_message_one

from states.true_goals_states import  WarGoalsState
from utilts import simple_media, CoolPercReplacer

from states.nato_states import Nato_states

flags = {"throttling_key": "True"}
router = Router()


# router.message.filter(state=Nato_states)


@router.message(commands='test_nato')
async def nato_start(message: Message, state: FSMContext):
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
                              reply_markup=polls_continue_kb())


@router.poll_answer(state=Nato_states.first_poll, flags=flags)
async def nato_poll_answer(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='nato_poll_answer',
                                value=poll_answer.option_ids[0])
    right_answers = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 0})
    answer_1 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 1})
    answer_2 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 2})
    answer_3 = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': 3})
    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_poll_answer': {'$exists': True}})
    await state.set_state(Nato_states.poll_answer)
    await state.update_data(nato_poll_answer=poll_answer.option_ids[0])

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'nato_poll_answer'}), all_answers)
    txt.replace("AA", right_answers)
    txt.replace("BB", answer_1)
    txt.replace("CC", answer_2)
    txt.replace("DD", answer_3)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, согласен(а) 👍"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет, не согласен(а) 👎"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀"))
    nmarkup.adjust(2, 1)
    await bot.send_message(text=txt(), chat_id=poll_answer.user.id, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Скорее да, согласен(а) 👍', 'Скорее нет, не согласен(а) 👎',
                             "Затрудняюсь ответить 🤷‍♀"})), state=Nato_states.poll_answer, flags=flags)
async def nato_other_questions(message: Message, state: FSMContext):
    await state.set_state(Nato_states.nato_other_questions)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='nato_other_questions',
                                value=message.text)
    answer_1 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Скорее да, согласен(а) 👍'})
    answer_2 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Скорее нет, не согласен(а) 👎'})
    answer_3 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_other_questions': 'Затрудняюсь ответить 🤷‍♀'})
    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_other_questions': {'$exists': True}})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'nato_other_questions'}), all_answers)
    txt.replace("AA", answer_1)
    txt.replace("BB", answer_2)
    txt.replace("CC", answer_3)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Страны НАТО что ли? 😏"))
    await message.answer(txt(), disable_web_page_preview=True, reply_markup=nmarkup.as_markup(resize_keyboard=True))


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


@router.message(F.text.contains('Надули? 🤨'), state=Nato_states.nato_countries, flags=flags)
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
    await simple_media(message, 'nato_extention', reply_markup=nmarkup.as_markup(resize_keyboard=True))


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
    await simple_media(message, 'nato_propagandons', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Продолжим 👉'),
                state=Nato_states.nato_countries, flags=flags)
async def nato_not_enemy(message: Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'nato_not_enemy', reply_markup=nmarkup.as_markup(resize_keyboard=True))


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
    await simple_media(message, 'nato_ucraine_in', reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message(F.text.contains('Взглянуть на карту 🗺'), state=Nato_states.nato_ucraine_in, flags=flags)
async def nato_map(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_map)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Так если бы Украина вступила в НАТО, они вместе вторглись бы в Крым!  ✈️"))
    nmarkup.row(types.KeyboardButton(text="А Путин объяснил, почему Украина и Финляндия— это разное? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Закончим диалог о НАТО 👉"))
    await simple_media(message, 'nato_map', reply_markup=nmarkup.as_markup(resize_keyboard=True))



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
        nmarkup.row(
            types.KeyboardButton(text="Так если бы Украина вступила в НАТО, они вместе вторглись бы в Крым!  ✈️"))
    nmarkup.row(types.KeyboardButton(text="Закончим диалог о НАТО 👉"))
    await simple_media(message, 'nato_diff_with_fin', reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message(F.text.contains('Закончим диалог о НАТО 👉'),
                state=Nato_states.nato_map, flags=flags)
async def nato_pre_end(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Nato_states.nato_pre_end)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, это лишь предлог 👌"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет, это настоящая причина 🙅‍♂"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀"))
    nmarkup.adjust(2, 1)
    text = await sql_safe_select('text', 'texts', {'name': 'nato_pre_end'})
    await message.answer(text=text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(Nato_states.nato_pre_end,
                (F.text.in_({'Скорее да, это лишь предлог 👌', "Скорее нет, это настоящая причина 🙅‍♂",
                             "Затрудняюсь ответить 🤷‍♀"})), flags=flags)
async def nato_end(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.main)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='nato_end',
                                value=message.text)
    answer_1 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Скорее да, это лишь предлог 👌',
                                       'war_aims_ex': welc_message_one[5]})
    answer_2 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Скорее нет, это настоящая причина 🙅‍♂',
                                       'war_aims_ex': welc_message_one[5]})
    answer_3 = await mongo_count_docs('database', 'statistics_new',
                                      {'nato_end': 'Затрудняюсь ответить 🤷‍♀',
                                       'war_aims_ex': welc_message_one[5]})
    all_answers = await mongo_count_docs('database', 'statistics_new', {'nato_end': {'$exists': True},
                                                                        'war_aims_ex': welc_message_one[5]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'nato_end'}), all_answers)
    txt.replace("AA", answer_1)
    txt.replace("BB", answer_2)
    txt.replace("CC", answer_3)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text=txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True),
                         disable_web_page_preview=True)
