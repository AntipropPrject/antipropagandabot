import asyncio

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new, mongo_update_stat
from data_base.DBuse import poll_get, poll_write, del_key, data_getter, mongo_game_answer, redis_delete_from_list
from data_base.DBuse import sql_safe_select, mongo_count_docs
from filters.MapFilters import FakeGoals, WarGoals
from filters.MapFilters import OperationWar
from handlers.story.donbass_hand import donbass_big_tragedy
from handlers.story.nato_hand import nato_start
from handlers.story.nazi_hand import NaziState, nazi_first_poll
from handlers.story.power_change_hand import goals_fact_1
from handlers.story.preventive_strike import prevent_strike_any_brutality
from keyboards.map_keys import polls_continue_kb
from resources.all_polls import welc_message_one
from resources.variables import mobilisation_date
from states.stopwar_states import StopWarState
from states.true_goals_states import TrueGoalsState, WarGoalsState
from utils.fakes import fake_message
from utilts import simple_media, CoolPercReplacer, get_time_from_war_started

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=(TrueGoalsState, WarGoalsState))
router.poll_answer.filter(state=TrueGoalsState)


@router.message((F.text.in_({"Очень интересно 👍", "Интересно, но слегка затянуто 🤏",
                             "Где-то интересно, где-то скучно 🙂", "Довольно скучно 🥱"})),
                state=TrueGoalsState.main, flags=flags)
async def goals_war_point_now(message: Message, state: FSMContext):
    await mongo_update_stat_new(message.from_user.id, "antip_final_reaction", value=message.text)
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


@router.message((F.text.contains('Понятно...')) | (F.text.contains('Да, выйти ⬇')), flags=flags)
async def goals_big_war(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.more_goals)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_big_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="И какие цели настоящие? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains("И какие цели настоящие? 🤔")), flags=flags)
async def goals_big_war(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_no_clear'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи результаты 📊"))
    await state.set_state(TrueGoalsState.more_goals_sort)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains("Покажи результаты 📊")), state=TrueGoalsState.more_goals_sort, flags=flags)
async def goals_sort_reveal(message: Message, state: FSMContext):
    var_aims = dict()
    pwr_ukr = await mongo_count_docs('database', 'statistics_new',
                                     {'war_aims_ex': {'$regex': "Сменить власть на Украине"}})
    nato = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "НАТО на Украине"}})
    putins_reting = await mongo_count_docs('database', 'statistics_new',
                                           {'war_aims_ex': {'$regex': "рейтинг доверия Владимира Путина"}})
    russians_donbass = await mongo_count_docs('database', 'statistics_new',
                                              {'war_aims_ex': {'$regex': "Защитить русских в Донбассе"}})
    prevent_the_invasion = await mongo_count_docs('database', 'statistics_new',
                                                  {'war_aims_ex': {'$regex': "Предотвратить вторжение"}})
    denazification = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Денацификация"}})
    demilitarization = await mongo_count_docs('database', 'statistics_new',
                                              {'war_aims_ex': {'$regex': "Демилитаризация"}})
    unite_russian = await mongo_count_docs('database', 'statistics_new',
                                           {'war_aims_ex': {'$regex': "Объединить русский народ"}})
    secret_dev = await mongo_count_docs('database', 'statistics_new',
                                        {'war_aims_ex': {'$regex': "Предотвратить секретные разработки"}})

    all_count = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    var_aims['✅ ' + welc_message_one[4]] = round(pwr_ukr / all_count * 100)
    var_aims['❌ ' + welc_message_one[5]] = round(nato / all_count * 100)
    var_aims['❓ ' + welc_message_one[6]] = round(putins_reting / all_count * 100)
    var_aims['❌ ' + welc_message_one[0]] = round(russians_donbass / all_count * 100)
    var_aims['❌ ' + welc_message_one[1]] = round(prevent_the_invasion / all_count * 100)
    var_aims['❌ ' + welc_message_one[2]] = round(denazification / all_count * 100)
    var_aims['❌ ' + welc_message_one[3]] = round(demilitarization / all_count * 100)
    var_aims['❓ ' + welc_message_one[7]] = round(unite_russian / all_count * 100)
    var_aims['❌ ' + welc_message_one[8]] = round(secret_dev / all_count * 100)

    sorted_dict = dict(sorted(var_aims.items(), key=lambda x: x[1], reverse=True))

    result_text = await sql_safe_select('text', 'texts', {'name': 'goals_sort_hided'})
    result_text = result_text + '\n\n'
    for text, value in sorted_dict.items():
        result_text = result_text + (str(value) + '% ' + str(text[1:])) + '\n'  # str(text[:1]) + '  — ' +
    await state.update_data(sorted_dict=sorted_dict)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkup.row(types.KeyboardButton(text="Продолжай 👉"))
    nmarkup.adjust(2)
    await state.set_state(TrueGoalsState.more_goals_no_truth)
    await message.answer(result_text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Интересно 🤔')) | (F.text.contains('Продолжай 👉')),
                state=TrueGoalsState.more_goals_no_truth,
                flags=flags)
async def goals_no_truth_for_us(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_no_truth_for_us'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, слышал(а) 👌"))
    nmarkup.row(types.KeyboardButton(text="Нет, не слышал(а) 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Да, и сам(а) так считаю 👍"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains("Да, слышал(а) 👌") | F.text.contains("Нет, не слышал(а) 🤷‍♀️") |
                 F.text.contains("Да, и сам(а) так считаю 👍")),
                state=TrueGoalsState.more_goals_no_truth, flags=flags)
async def goals_no_truth_for_us(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_cards_opened'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай! 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains("Давай! 👌"), state=TrueGoalsState.more_goals_no_truth, flags=flags)
async def goals_no_truth_for_us(message: Message, state: FSMContext):
    data = await state.get_data()
    sorted_dict = data['sorted_dict']
    result_text = await sql_safe_select('text', 'texts', {'name': 'goals_sort_reveal'})
    result_text = result_text + '\n'
    for text, value in sorted_dict.items():
        result_text = result_text + (str(text[:1]) + '  — ' + str(value) + '% ' + str(text[1:])) + '\n'
    await state.update_data(sorted_dict=sorted_dict)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Похоже на правду 👍"))
    nmarkup.row(types.KeyboardButton(text="Не похоже на правду 👎"))
    nmarkup.row(types.KeyboardButton(text="Объясни-ка 🤔"))
    nmarkup.row(types.KeyboardButton(text="Просто продолжим 👉"))
    nmarkup.adjust(2, 2)
    await state.set_state(TrueGoalsState.more_goals)
    await message.answer(result_text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


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
        text = text.replace('[agreed]', 'такими причинами')
        text = text.replace('[claim]', 'эти причины')
        text = text.replace('[is]', 'являются')
    else:
        text = text.replace('[agreed]', 'такой причиной')
        text = text.replace('[claim]', 'эта причина')
        text = text.replace('[is]', 'является')
    listtext = "\n".join(fake_goals_data['fake_goals'])
    text = text.replace('[REASONS_LIST]', listtext)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, начнём 🤝"))
    if fake_goals_data['fake_goals_number'] != 6:
        nmarkup.row(types.KeyboardButton(text="Да, но давай добавим ещё цели к обсуждению 🎯"))
    nmarkup.row(types.KeyboardButton(text="Нет, пропустим обсуждение этих тем 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FakeGoals(not_all_fakes=True), F.text == 'Да, начнём 🤝', state=TrueGoalsState.more_goals, flags=flags)
async def goals_lets_add_goals(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.more_goals_next)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_lets_add_goals'})
    not_checked_fakes = await poll_get(f'Usrs: {message.from_user.id}: TrueGoals: NotChosenFakeGoals:')
    listtext = "\n".join(not_checked_fakes)
    text = text.replace('[REASONS_LIST]', listtext)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, давай обсудим некоторые из этих тем 🎯"))
    nmarkup.row(types.KeyboardButton(text="Просто продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Нет, пропустим обсуждение этих тем 👉', state=TrueGoalsState.more_goals, flags=flags)
async def goals_wait_a_minute(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_wait_a_minute'})
    listtext = "\n".join(await poll_get(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:'))
    text = text.replace('[REASONS_LIST]', listtext)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, давай обсудим 👌"))
    nmarkup.row(types.KeyboardButton(text="Точно пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Хорошо, давай обсудим 👌', state=TrueGoalsState.more_goals, flags=flags)
async def goals_good_decision(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_good_decision'})
    await message.answer(text, disable_web_page_preview=True)
    await goals_lets_add_goals(message, state)


@router.message(F.text.contains('🎯'), state=(TrueGoalsState.more_goals, TrueGoalsState.more_goals_next), flags=flags)
async def goals_add_goals_poll(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.more_goals_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_add_goals_poll'})
    answers = await poll_get(f'Usrs: {message.from_user.id}: TrueGoals: NotChosenFakeGoals:')
    answers.append('Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.')
    await message.answer_poll(text, answers, allows_multiple_answers=True, is_anonymous=False,
                              reply_markup=polls_continue_kb())


@router.poll_answer(state=TrueGoalsState.more_goals_poll, flags=flags)
@router.message(F.text == 'Просто продолжим 👉', state=TrueGoalsState.more_goals_next, flags=flags)
@router.message(F.text == 'Да, начнём 🤝', state=TrueGoalsState.more_goals, flags=flags)
async def goals_answer(update: types.PollAnswer | Message, bot: Bot, state: FSMContext):
    await state.set_state(WarGoalsState.main)
    if isinstance(update, types.PollAnswer):
        user = update.user
        lst_answers = update.option_ids
        user_new_fake_list = await poll_get(f"Usrs: {user.id}: TrueGoals: NotChosenFakeGoals:")
        user_new_fake_list.append('Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.')
        for index in lst_answers:
            if user_new_fake_list[index] != 'Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.':
                await poll_write(f'Usrs: {user.id}: TrueGoals: UserFakeGoals:', user_new_fake_list[index])
    else:
        user = update.from_user
    await del_key(f"Usrs: {user.id}: TrueGoals: NotChosenFakeGoals:")
    await bot.send_message(user.id, await sql_safe_select('text', 'texts', {'name': 'goals_answer'}))
    await asyncio.sleep(all_data().THROTTLE_TIME)
    await router.parent_router.feed_update(bot, fake_message(user, "Уверен(а), проп"))


@router.message(WarGoals(goal=welc_message_one[0]), ((F.text.contains("Уверен(а), проп")) | (F.text == "Кнопка")),
                state=WarGoalsState, flags=flags)
async def goals_donbas_start(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.donbas_enter)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[0])
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    donbass = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[0]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_donbas_start'}), g_all)
    txt.replace('XX', donbass)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём 👪'))
    nmarkup.row(types.KeyboardButton(text='Пропустим 👉'))
    nmarkup.adjust(2)
    await simple_media(message, 'goals_donbas_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message((F.text == "Пропустим 👉"), state=WarGoalsState.donbas_enter, flags=flags)
async def goals_pls_use_goal(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_pls_use_goal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, обсудим 👪'))
    nmarkup.row(types.KeyboardButton(text='Уверен(а), пропустим 👉'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains("👪")), state=WarGoalsState.donbas_enter, flags=flags)
async def goals_donbas_enterence(message: Message, state: FSMContext):
    # await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_start', value='Да')
    await donbass_big_tragedy(message, state)


@router.message(WarGoals(goal=welc_message_one[1]), ((F.text.contains("Уверен(а), проп")) | (F.text == "Кнопка") |
                                                     (F.text == "Продолжим 👌")), state=WarGoalsState, flags=flags)
async def goals_preventive_start(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.preventive_enter)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[1])
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    prevent = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[1]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_preventive_start'}), g_all)
    txt.replace('XX', prevent)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём 🛡'))
    nmarkup.row(types.KeyboardButton(text='Пропустим 👉'))
    nmarkup.adjust(2)
    await simple_media(message, 'goals_preventive_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message((F.text == "Пропустим 👉"), state=WarGoalsState.preventive_enter, flags=flags)
async def goals_pls_use_goal_prev(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_pls_use_goal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, обсудим 🛡'))
    nmarkup.row(types.KeyboardButton(text='Уверен(а), пропустим 👉'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains("🛡")), state=WarGoalsState.preventive_enter, flags=flags)
async def goals_preventive_enterence(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_start', value='Да')
    await prevent_strike_any_brutality(message, state)


@router.message(WarGoals(goal=welc_message_one[2]), ((F.text.contains("Уверен(а), проп")) | (F.text == "Кнопка")) |
                (F.text == "Продолжим 👌"), state=WarGoalsState, flags=flags)
async def goals_nazi_start(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[2])
    await state.set_state(WarGoalsState.nazi_enter)
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    nazi = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[2]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_nazi_start'}), g_all)
    txt.replace('XX', nazi)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём 🙋‍♂️'))
    nmarkup.row(types.KeyboardButton(text='Пропустим 👉'))
    await simple_media(message, 'goals_nazi_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message((F.text == "Пропустим 👉"), state=WarGoalsState.nazi_enter, flags=flags)
async def goals_pls_use_goal_nazi(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_pls_use_goal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, обсудим 🙋‍♂️'))
    nmarkup.row(types.KeyboardButton(text='Уверен(а), пропустим 👉'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains("🙋‍♂️")), state=WarGoalsState.nazi_enter, flags=flags)
async def goals_nazi_enterence(message: Message, state: FSMContext):
    await state.set_state(NaziState.first_poll)
    await nazi_first_poll(message)


@router.message(WarGoals(goal=welc_message_one[3]),
                ((F.text.contains("Уверен(а), проп")) | (F.text.in_({"Кнопка"})) | (F.text == "Продолжим 👌")),
                state=WarGoalsState, flags=flags)
async def goals_demilitari_start(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.demilitari)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[3])
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    demil = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[3]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_demilitari_start'}), g_all)
    txt.replace('XX', demil)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Предотвратить размещение военных баз НАТО 🛡'))
    nmarkup.row(types.KeyboardButton(text='Предотвратить создание ядерного оружия на Украине 💥'))
    nmarkup.row(types.KeyboardButton(text='Им наверху виднее 🤔'))
    nmarkup.add(types.KeyboardButton(text='Я не знаю 🤷‍♀️'))
    nmarkup.row(types.KeyboardButton(text='Думаю он хотел, как лучше, а получилось наоборот 🤷‍♂️'))
    await simple_media(message, 'goals_demilitari_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message(((F.text.contains("🤷‍")) | F.text.contains("виднее 🤔")),
                state=WarGoalsState.demilitari, flags=flags)
async def goals_noone_remember(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_noone_remember'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Предотвратить размещение военных баз НАТО 🛡"),
                state=WarGoalsState.demilitari, flags=flags)
async def goals_demilitari_NATO(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[5])
    text = await sql_safe_select('text', 'texts', {'name': 'goals_demilitari_NATO'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Предотвратить создание ядерного оружия на Украине 💥"),
                state=WarGoalsState.demilitari, flags=flags)
async def goals_demilitari_nukes(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[8])
    text = await sql_safe_select('text', 'texts', {'name': 'goals_demilitari_nukes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WarGoals(goal=welc_message_one[5]),
                ((F.text.contains("Уверен(а), проп")) | (F.text.in_({"Кнопка", 'Продолжим 👌'}))),
                state=WarGoalsState, flags=flags)
async def goals_NATO_start(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.nato)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[5])
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    nato = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[5]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_NATO_start'}), g_all)
    txt.replace('XX', nato)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём 💂'))
    nmarkup.row(types.KeyboardButton(text='Пропустим 👉'))
    await simple_media(message, 'goals_NATO_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message((F.text == "Пропустим 👉"), state=WarGoalsState.nato, flags=flags)
async def goals_pls_use_goal_nazi(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_pls_use_goal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, обсудим 💂'))
    nmarkup.row(types.KeyboardButton(text='Уверен(а), пропустим 👉'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains("💂")), state=WarGoalsState.nato, flags=flags)
async def goals_nazi_enterence(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await nato_start(message, state)


@router.message(WarGoals(goal=welc_message_one[8]),
                ((F.text.contains("Уверен(а), проп")) | (F.text.in_({"Кнопка", 'Продолжим 👌'}))),
                state=WarGoalsState, flags=flags)
async def goals_bio_start(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.bio)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: TrueGoals: UserFakeGoals:', welc_message_one[8])
    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    bio = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[8]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'goals_bio_start'}), g_all)
    txt.replace('XX', bio)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём 🤯'))
    nmarkup.row(types.KeyboardButton(text='Пропустим 👉'))
    await simple_media(message, 'goals_bio_start', nmarkup.as_markup(resize_keyboard=True), txt())


@router.message((F.text == "Пропустим 👉"), state=WarGoalsState.bio, flags=flags)
async def goals_pls_use_goal_nazi(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_pls_use_goal'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, обсудим 🤯'))
    nmarkup.row(types.KeyboardButton(text='Уверен(а), пропустим 👉'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains("🤯")), state=WarGoalsState.bio, flags=flags)
async def goals_nazi_enterence(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_will_add_bio_sorry'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains("Уверен(а), проп")) | (F.text.in_({"Кнопка", 'Продолжим 👌'}))),
                state=WarGoalsState, flags=flags)
@router.message((F.text.contains("продолжим")) | (F.text.contains("пропустим")),
                state=TrueGoalsState.more_goals, flags=flags)
async def goals_normal_game_start(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.normal_game)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_normal_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнём! 🚀'))
    nmarkup.row(types.KeyboardButton(text='Пропустим игру 🙅‍♀️'))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Начнём! 🚀") | (F.text == "Продолжаем, давай еще! 👉")), state=TrueGoalsState.normal_game,
                flags=flags)
async def goals_normal_game_question(message: Message, state: FSMContext):
    if 'Начнём! 🚀' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats',
                                    value='Начали и НЕ закончили')
    try:
        count = (await state.get_data())['ngamecount']
    except Exception:
        count = 0
    how_many_rounds = (await data_getter("SELECT COUNT (*) FROM public.normal_game"))[0][0]
    if count < how_many_rounds:
        count += 1
        truth_data = (await data_getter("SELECT * FROM (SELECT t_id, text, belivers, nonbelivers, rebuttal, "
                                        " ROW_NUMBER () OVER (ORDER BY id)"
                                        "FROM normal_game "
                                        "left outer join assets on asset_name = assets.name "
                                        "left outer join texts ON text_name = texts.name)"
                                        f"AS sub WHERE row_number = {count}"))[0]
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это абсурд🤦🏼‍♀️"))
        nmarkup.row(types.KeyboardButton(text="Это нормально👌"))
        nmarkup.adjust(2)
        if truth_data[0] is not None:
            capt = ""
            if truth_data[1] is not None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except TelegramBadRequest:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'{truth_data[1]}', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Начали и закончили')
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Продолжим 🤝"))
        await message.answer(
            "У меня закончились новости. Спасибо за игру 🤝",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Это абсурд🤦🏼‍♀️") | (F.text == "Это нормально👌")), state=TrueGoalsState.normal_game,
                flags=flags)
async def goals_normal_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    END = bool(data['ngamecount'] == (await data_getter('SELECT COUNT(id) FROM public.normal_game'))[0][0])
    nmarkup = ReplyKeyboardBuilder()
    if END is False:
        nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще! 👉"))
        nmarkup.row(types.KeyboardButton(text="Достаточно, давай закончим 🙅"))
    else:
        nmarkup.row(types.KeyboardButton(text="Продолжим 🤝"))
    answer_group = str()
    if message.text == "Это абсурд🤦🏼‍♀️":
        answer_group = 'belivers'
    elif message.text == "Это нормально👌":
        answer_group = 'nonbelivers'
    await mongo_game_answer(message.from_user.id, 'normal_game', data['ngamecount'],
                            answer_group, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    await message.answer(
        f'Результаты других участников:\n🤦‍♂️ Это абсурд: {round(t_percentage * 100)}%'
        f'\n👌 Это нормально: {round(100 - t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
    if END is True:
        await message.answer("У меня закончились новости. Спасибо за игру 🤝",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains("Достаточно,")) | (F.text == "Продолжим 🤝") | (F.text == 'Пропустим игру 🙅‍♀️')),
                state=TrueGoalsState.normal_game, flags=flags)
async def goals_I_love_absurd(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_I_love_absurd'})
    if 'Пропустим игру' in message.text:
        await message.answer('Хорошо')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Пропустили')
    await state.set_state(TrueGoalsState.absurd)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить абсурдности 🪄"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Добавить абсурдности 🪄", state=TrueGoalsState.absurd, flags=flags)
async def goals_read_this_thing(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_read_this_thing'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Забавно 🙂"))
    nmarkup.add(types.KeyboardButton(text="Грустно 😔"))
    nmarkup.row(types.KeyboardButton(text="Однобоко 👎"))
    nmarkup.add(types.KeyboardButton(text="Просто продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({"Забавно 🙂", "Грустно 😔", "Однобоко 👎", "Просто продолжим 👉"}),
                state=TrueGoalsState.absurd, flags=flags)
async def goals_no_conspirasy(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='goals_absurd_summary',
                                value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_no_conspirasy'})

    a_all = await mongo_count_docs('database', 'statistics_new', {'goals_absurd_summary': {'$exists': True}})
    a_funny = await mongo_count_docs('database', 'statistics_new', {'goals_absurd_summary': "Забавно 🙂"})
    a_sad = await mongo_count_docs('database', 'statistics_new', {'goals_absurd_summary': "Грустно 😔"})
    a_bok = await mongo_count_docs('database', 'statistics_new', {'goals_absurd_summary': "Однобоко 👎"})
    a_plain = await mongo_count_docs('database', 'statistics_new', {'goals_absurd_summary': "Просто продолжим 👉"})

    txt = CoolPercReplacer(text, a_all)
    txt.replace("AA", a_funny)
    txt.replace("BB", a_sad)
    txt.replace("CC", a_bok)
    txt.replace("DD", a_plain)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай начнём 👌"))
    nmarkup.add(types.KeyboardButton(text="Так войну или спецоперацию? 🤔"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({"Давай начнём 👌", "Так войну или спецоперацию? 🤔"}),
                state=TrueGoalsState.absurd, flags=flags)
async def goals_such_plan_so(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_such_plan_so'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Продолжай ⏳", state=TrueGoalsState.absurd, flags=flags)
async def goals_change_of_power(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.power_change)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_change_of_power'})

    g_all = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$exists': True}})
    change_power = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': welc_message_one[4]})
    try:
        XX = change_power / g_all * 100
        text = text.replace('XX', round(XX))
    except Exception:
        text = text.replace('XX', 'N/A')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Взглянем на факты 👀"))
    nmarkup.row(types.KeyboardButton(text="Пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('на факты 👀')), state=TrueGoalsState.power_change, flags=flags)
async def goals_will_add_sorry(message: Message, state: FSMContext):
    await goals_fact_1(message, state)


@router.message(F.text == "Пропустим 👉", state=TrueGoalsState.power_change, flags=flags)
async def goals_sure_power_change(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_sure_power_change'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Всё-таки взглянем на факты 👀"))
    nmarkup.row(types.KeyboardButton(text="Да, двигаемся дальше 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Достаточно фактов ✋", state=TrueGoalsState, flags=flags)
@router.message(F.text == "Хорошо, продолжим 👌", state=TrueGoalsState.goals_fact_7, flags=flags)
@router.message(F.text == "Да, двигаемся дальше 👉", state=TrueGoalsState.power_change, flags=flags)
async def goals_why_power_change(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.power_change)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_why_power_change'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай посмотрим 👀"))
    nmarkup.row(types.KeyboardButton(text="Это мне не интересно, пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Давай посмотрим 👀", state=TrueGoalsState.power_change, flags=flags)
async def goals_paper_theses(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_paper_theses'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkup.add(types.KeyboardButton(text="Стало скучно, ближе к делу 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Интересно 🤔", state=TrueGoalsState.power_change, flags=flags)
async def goals_russian_world_nazi(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await simple_media(message, 'goals_russian_world_nazi', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Посмотрел(а) 📺", "Продолжим 👉"})) | (F.text == "Это мне не интересно, пропустим 👉") |
                (F.text == "Стало скучно, ближе к делу 👉"), state=TrueGoalsState.power_change, flags=flags)
async def goals_why_he_is_continued(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_why_he_is_continued'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    nmarkup.row(types.KeyboardButton(text="Подожди! А почему Путин решил напасть именно в феврале 2022? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Подожди! А почему Путин решил напасть именно в феврале 2022? 🤔",
                state=TrueGoalsState.putin, flags=flags)
async def goals_best_moment(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_best_moment'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, продолжим 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Давай 👌") | (F.text == 'Хорошо, продолжим 👌')), state=TrueGoalsState.putin, flags=flags)
async def goals_would_you_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_would_you_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно, продолжай ⏳"))
    nmarkup.add(types.KeyboardButton(text="Стало скучно, пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Интересно, продолжай ⏳", state=TrueGoalsState.putin, flags=flags)
async def goals_dirt_waves(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin_next)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно, продолжай ⏳"))
    nmarkup.add(types.KeyboardButton(text="Стало скучно, пропустим 👉"))
    await simple_media(message, 'goals_dirt_waves', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Интересно, продолжай ⏳"), state=TrueGoalsState.putin_next, flags=flags)
async def goals_putin_plan_continued(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'goals_putin_plan_continued', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Стало скучно, пропустим 👉'),
                state=(TrueGoalsState.putin_next, TrueGoalsState.putin), flags=flags)
@router.message(F.text == "Продолжай ⏳", state=TrueGoalsState.putin_next, flags=flags)
async def goals_putin_face(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin_next)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим..."))
    await simple_media(message, 'goals_putin_face', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Продолжим...", state=TrueGoalsState.putin_next, flags=flags)
async def goals_mobilisation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_mobilisation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой вопрос 🤔"))
    await simple_media(message, 'goals_mobilisation', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Какой вопрос 🤔", state=TrueGoalsState.putin_next, flags=flags)
async def goals_how_many_mobs(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_how_many_mobs'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Около 300 тысяч, как и обещали 👌"))
    nmarkup.row(types.KeyboardButton(text="Меньше 300 тыс. человек 🔻"))
    nmarkup.add(types.KeyboardButton(text="Больше 300 тыс. человек 🔺"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Около 300 тысяч, как и обещали 👌", "Меньше 300 тыс. человек 🔻",
                             "Больше 300 тыс. человек 🔺", "Затрудняюсь ответить 🤷‍♀️"})),
                state=TrueGoalsState.putin_next, flags=flags)
async def goals_how_many_mobs_result(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin_next_next)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='goals_many_mobs', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_how_many_mobs_result'})

    m_all = await mongo_count_docs('database', 'statistics_new', {'goals_many_mobs': {'$exists': True}})
    m_300 = await mongo_count_docs('database', 'statistics_new',
                                   {'goals_many_mobs': "Около 300 тысяч, как и обещали 👌"})
    m_less = await mongo_count_docs('database', 'statistics_new',
                                    {'goals_many_mobs': "Меньше 300 тыс. человек 🔻"})
    m_more = await mongo_count_docs('database', 'statistics_new', {'goals_many_mobs': "Больше 300 тыс. человек 🔺"})
    m_idk = await mongo_count_docs('database', 'statistics_new', {'goals_many_mobs': "Затрудняюсь ответить 🤷‍♀️"})

    txt = CoolPercReplacer(text, m_all)
    txt.replace("AA", m_300)
    txt.replace("BB", m_less)
    txt.replace("CC", m_more)
    txt.replace("DD", m_idk)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Узнать правильный ответ 📊"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Узнать правильный ответ 📊", state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_more_than_300(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await simple_media(message, 'goals_more_than_300', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Давай 👌", state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_agreed_to_die(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_agreed_to_die'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, ощущаю угрозу ⚔️"))
    nmarkup.add(types.KeyboardButton(text="Нет, не ощущаю угрозы 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Да, ощущаю угрозу ⚔️", "Нет, не ощущаю угрозы 🤷‍♂️",
                             "Затрудняюсь ответить 🤔"})), state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_agreed_to_die_result(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='goals_mobilisation_terror', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_agreed_to_die_result'})

    terr_all = await mongo_count_docs('database', 'statistics_new', {'goals_mobilisation_terror': {'$exists': True}})
    terr_yes = await mongo_count_docs('database', 'statistics_new',
                                      {'goals_mobilisation_terror': "Да, ощущаю угрозу ⚔️"})
    terr_no = await mongo_count_docs('database', 'statistics_new',
                                     {'goals_mobilisation_terror': "Нет, не ощущаю угрозы 🤷‍♂️"})
    terr_idk = await mongo_count_docs('database', 'statistics_new',
                                      {'goals_mobilisation_terror': "Затрудняюсь ответить 🤔"})

    txt = CoolPercReplacer(text, terr_all)
    txt.replace("AA", terr_yes)
    txt.replace("BB", terr_no)
    txt.replace("CC", terr_idk)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Это точно 👌"))
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Это точно 👌", "Продолжим 👉"})), state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_politics_is_here(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_politics_is_here'})

    who_love_all = await mongo_count_docs('database', 'statistics_new', {'prop_ex': {"$exists": True}})
    who_love_putin_now = await mongo_count_docs('database', 'statistics_new', {'prop_ex': "Владимир Путин"})
    txt = CoolPercReplacer(text, who_love_all)
    txt.replace("XX", who_love_putin_now)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой факт? 🤔"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Какой факт? 🤔", state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_putin_in_the_past(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_putin_in_the_past'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="И правда, не могу вспомнить 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Это неправда, Путин выполняет обещания ☝️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Это неправда, Путин выполняет обещания ☝️",
                state=TrueGoalsState.putin_next_next, flags=flags)
async def goals_gifted_cat(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_gifted_cat'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Продолжим 👌") | (F.text == "И правда, не могу вспомнить 🤷‍♂️")),
                state=TrueGoalsState.putin_next_next, flags=flags)
async def putin_gaming(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin_gaming)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='started_putin_old_lies', value='Да')
    text = await sql_safe_select('text', 'texts', {'name': 'goals_putin_old_lies_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я готов(а) 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Я готов(а) 👌") | (F.text == "Нет, давай продолжим 👉") | (F.text == "Продолжаем! 👉")),
                state=TrueGoalsState.putin_gaming, flags=flags)
async def putin_game2_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['pgamecount']
    except Exception:
        count = 0
    how_many_rounds = (await data_getter("SELECT COUNT (*) FROM public.putin_old_lies"))[0][0]
    if count < how_many_rounds:
        count += 1
        truth_data = (await data_getter("SELECT * FROM (SELECT t_id, text, belivers, nonbelivers, rebuttal, "
                                        "row_number() over (order by id) FROM public.putin_old_lies "
                                        "left outer join assets on asset_name = assets.name "
                                        f"left outer join texts ON text_name = texts.name) as subb "
                                        f"where row_number = {count}"))[0]
        await state.update_data(pgamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.add(types.KeyboardButton(text="Виноват 👎"))
        nmarkup.add(types.KeyboardButton(text="Не виноват 👍"))
        if truth_data[0] is not None:
            capt = ""
            if truth_data[1] is not None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except TelegramBadRequest:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'Вот что обещал Путин:\n\n{truth_data[1]}',
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, давай дальше"))
        await message.answer(
            "Боюсь, что пока что у меня кончились примеры. Я поищу еще, а пока что продолжим",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Не виноват 👍") | (F.text == "Виноват 👎")), state=TrueGoalsState.putin_gaming,
                flags=flags)
async def putin_game2_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    answer_group = str()
    END = bool(data['pgamecount'] == (await data_getter('SELECT COUNT(id) FROM public.putin_old_lies'))[0][0])
    nmarkup = ReplyKeyboardBuilder()
    if END is False:
        nmarkup.row(types.KeyboardButton(text="Продолжаем! 👉"))
        nmarkup.row(types.KeyboardButton(text="Достаточно ✋"))
    else:
        nmarkup.row(types.KeyboardButton(text="Давай 🤝"))
    if message.text == "Не виноват 👍":
        answer_group = 'belivers'
    elif message.text == "Виноват 👎":
        answer_group = 'nonbelivers'
    await mongo_game_answer(message.from_user.id, 'putin_old_lies', data['pgamecount'],
                            answer_group, {'id': data['pgamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    await message.answer(
        f'А вот что думают другие участники:\n\n'
        f'👎 <b>Виноват</b>: {round((100 - t_percentage * 100))}% \n👍 <b>Не виноват</b>: {round(t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
    if END is True:
        await message.answer('Спасибо за игру 🤝 Давайте подведем итоги.')


@router.message((F.text == "Достаточно ✋"), state=TrueGoalsState.putin_gaming, flags=flags)
async def putin_game2_are_you_sure(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, давай продолжим 👉"))
    nmarkup.row(types.KeyboardButton(text="Да, достаточно 🤷‍♀️"))
    await message.answer('Вы уверены? У меня еще есть примеры', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Да, достаточно 🤷‍♀️") | (F.text == "Хорошо, давай дальше") |
                 (F.text == "Давай 🤝")), state=TrueGoalsState.putin_gaming, flags=flags)
async def goals_putin_why_still_belive(message: Message, state: FSMContext):
    await state.clear()
    await mongo_update_stat(message.from_user.id, 'putin')
    await state.set_state(TrueGoalsState.final)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_putin_why_still_belive'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Расскажи 👌"))
    nmarkup.row(types.KeyboardButton(text="Мне это не интересно, пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Расскажи 👌"), state=TrueGoalsState.final, flags=flags)
async def goals_bad_tzar_bad(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_bad_tzar_bad'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 🪖"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Давай 🪖") | (F.text == "Мне это не интересно, пропустим 👉")), state=TrueGoalsState.final,
                flags=flags)
async def goals_putin_not_a_sport(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_putin_not_a_sport'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой факт? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Какой факт? 🤔"), state=TrueGoalsState.final, flags=flags)
async def goals_no_winners_in_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_no_winners_in_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    nmarkup.row(types.KeyboardButton(text="А что, Путин этого не знал? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Не верю / Докажи 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не верю / Докажи 🤔"), state=TrueGoalsState.final, flags=flags)
async def goals_wars_of_past(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await simple_media(message, 'goals_wars_of_past', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Продолжай ⏳", "А что, Путин этого не знал? 🤔", "Продолжим 👌"})),
                state=TrueGoalsState.final, flags=flags)
async def goals_russia_already_lost(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='goals_final_result', value=message.text)
    await state.set_state(StopWarState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_russia_already_lost'})
    day = await get_time_from_war_started()
    text = text.replace("AA", f"{day}")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Подведём итоги 📊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
