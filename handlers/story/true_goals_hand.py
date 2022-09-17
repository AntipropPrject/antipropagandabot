from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_select, poll_get, poll_write, del_key
from filters.MapFilters import OperationWar, FakeGoals
from resources.all_polls import welc_message_one, true_and_idk_goals
from states.true_goals_states import TrueGoalsState

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=TrueGoalsState)
router.poll_answer.filter(state=TrueGoalsState)


@router.message((F.text.contains('нтересно')) | (F.text.contains('скучно')), flags=flags)
async def goals_war_point_now(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_war_point_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(OperationWar(answer='(СВО)'), (F.text == "Продолжай ⏳"),
                state=TrueGoalsState.before_shop, flags=flags)
async def goals_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop_operation)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Продолжай ⏳", state=TrueGoalsState.before_shop_operation, flags=flags)
async def goals_not_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_not_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 🤝"))
    nmarkup.add(types.KeyboardButton(text="*презрительно хмыкнуть* 🤨"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FakeGoals(no_fakes_do_not_know=False),
                (F.text.contains('охоже')) | (F.text == 'Объясни-ка 🤔') | (F.text == 'Просто продолжим 👉'),
                state=TrueGoalsState.more_goals, flags=flags)
async def goals_you_cool(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_you_cool'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, давай обсудим некоторые из этих тем 🎯"))
    nmarkup.row(types.KeyboardButton(text="Не стоит, просто продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FakeGoals(no_fakes_do_not_know=True),
                (F.text.contains('охоже')) | (F.text == 'Объясни-ка 🤔') | (F.text == 'Просто продолжим 👉'),
                state=TrueGoalsState.more_goals, flags=flags)
async def goals_why_its_a_fraud(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_why_its_a_fraud'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи варианты 🎯"))
    nmarkup.row(types.KeyboardButton(text="Мне это не интересно 🤷‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Мне это не интересно 🤷‍♂️', state=TrueGoalsState.more_goals, flags=flags)
async def goals_are_you_sure_conflict(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_are_you_sure_conflict'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, давай обсудим некоторые из этих тем 🎯"))
    nmarkup.row(types.KeyboardButton(text="Не стоит, давай продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FakeGoals(more_than_one=True),
                (F.text.contains('охоже')) | (F.text == 'Объясни-ка 🤔') | (F.text == 'Просто продолжим 👉'),
                state=TrueGoalsState.more_goals, flags=flags)
async def goals_little_bet(message: Message, fake_goals_data: dict):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_little_bet'})
    if fake_goals_data['fake_goals_number'] > 1:
        text.replace('[agreed]', 'такими причинами')
        text.replace('[claim]', 'эти причины')
        text.replace('[is]', 'являются')
    else:
        text.replace('[agreed]', 'такой причиной')
        text.replace('[claim]', 'эта причина')
        text.replace('[is]', 'является')
    listtext = "\n".join(fake_goals_data['fake_goals'])
    text.replace('[REASONS_LIST]', listtext)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, начнём 🤝"))
    if fake_goals_data['fake_goals_number'] != 6:
        nmarkup.row(types.KeyboardButton(text="Да, но давай добавим ещё цели к обсуждению 🎯"))
    nmarkup.row(types.KeyboardButton(text="Нет, пропустим обсуждение этих тем 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FakeGoals(not_all_fakes=True), F.text == 'Да, начнём 🤝', state=TrueGoalsState.more_goals, flags=flags)
async def goals_lets_add_goals(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_lets_add_goals'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, давай обсудим некоторые из этих тем 🎯"))
    nmarkup.row(types.KeyboardButton(text="Просто продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Нет, пропустим обсуждение этих тем 👉', state=TrueGoalsState.more_goals, flags=flags)
async def goals_wait_a_minute(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_wait_a_minute'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, давай обсудим 👌"))
    nmarkup.row(types.KeyboardButton(text="Точно пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Хорошо, давай обсудим 👌', state=TrueGoalsState.more_goals, flags=flags)
async def goals_good_decision(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_good_decision'})
    await message.answer(text, disable_web_page_preview=True)
    await goals_lets_add_goals(message)


@router.message(F.text.contains('🎯'), state=TrueGoalsState.more_goals, flags=flags)
async def goals_add_goals_poll(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.more_goals_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_add_goals_poll'})
    answers = list((set(welc_message_one) ^ set(true_and_idk_goals)) ^
                   set(await poll_get(f"Usrs: {message.from_user.id}: Start_answers: Invasion:")))
    for answer in answers:
        print(answer)
        await poll_write(f'Usrs: {message.from_user.id}: TrueGoals: FakeInvasion:', answer)
    await message.answer_poll(text, answers, allows_multiple_answers=True, is_anonymous=False)


@router.poll_answer(state=TrueGoalsState.more_goals_poll, flags=flags)
async def goals_answer(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(TrueGoalsState.main)
    lst_answers = poll_answer.option_ids
    user_new_fake_list = await poll_get(f"Usrs: {poll_answer.user.id}: TrueGoals: FakeInvasion:")
    await del_key(f"Usrs: {poll_answer.user.id}: TrueGoals: FakeInvasion:")
    for index in lst_answers:
        print(index, user_new_fake_list[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:', user_new_fake_list[index])
    a = "\n".join((await poll_get(f"Usrs: {poll_answer.user.id}: Start_answers: Invasion:")))
    await bot.send_message(poll_answer.user.id, f'Ответ на опрос, пока конец. Нынешний список причин войны:{a}')
