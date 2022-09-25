from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import poll_get, poll_write, del_key, data_getter, mongo_game_answer
from data_base.DBuse import sql_safe_select, mongo_count_docs
from filters.MapFilters import FakeGoals
from filters.MapFilters import OperationWar
from resources.all_polls import welc_message_one, true_and_idk_goals
from states.true_goals_states import TrueGoalsState
from utilts import simple_media, CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=TrueGoalsState)
router.poll_answer.filter(state=TrueGoalsState)


@router.message((F.text.contains('нтересно')) | (F.text.contains('скучно')), state=TrueGoalsState.main, flags=flags)
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


@router.message((F.text.contains('Понятно 👌')) | (F.text.contains('Да, выйти ⬇')), flags=flags)
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
    all_count = pwr_ukr + nato + putins_reting + russians_donbass + prevent_the_invasion + denazification + \
                demilitarization + unite_russian + secret_dev
    var_aims['✅ ♻️ Сменить власть на Украине / Сделать её лояльной России'] = round(pwr_ukr / all_count * 100)
    var_aims['❌ 💂 Предотвратить размещение военных баз НАТО на Украине'] = round(nato / all_count * 100)
    var_aims['❓ 📈 Повысить рейтинг доверия Владимира Путина'] = round(putins_reting / all_count * 100)
    var_aims['❌ 👪 Защитить русских в Донбассе'] = round(russians_donbass / all_count * 100)
    var_aims['❌ 🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР'] = round(
        prevent_the_invasion / all_count * 100)
    var_aims['❌ 🤬 Денацификация / Уничтожить нацистов'] = round(denazification / all_count * 100)
    var_aims['❌ 💣 Демилитаризация / Снижение военной мощи'] = round(demilitarization / all_count * 100)
    var_aims['❓ 🗺 Вернуть России исторические земли / Объединить русский народ'] = round(
        unite_russian / all_count * 100)
    var_aims['❌ 🤯 Предотвратить секретные разработки: биологическое оружие / ядерное оружие'] = round(
        secret_dev / all_count * 100)

    sorted_dict = dict(sorted(var_aims.items(), key=lambda x: x[1]))
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
async def goals_no_truth_for_us(message: Message, state: FSMContext):
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
async def goals_no_truth_for_us(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_cards_opened'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай! 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains("Давай! 👌"), state=TrueGoalsState.more_goals_no_truth, flags=flags)
async def goals_no_truth_for_us(message: Message, state: FSMContext):
    data = await state.get_data()
    sorted_dict = data['sorted_dict']
    result_text = await sql_safe_select('text', 'texts', {'name': 'goals_sort_reveal'})
    result_text = result_text + '\n '
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
async def goals_lets_add_goals(message: Message):
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
async def goals_good_decision(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_good_decision'})
    await message.answer(text, disable_web_page_preview=True)
    await goals_lets_add_goals(message)


@router.message(F.text.contains('🎯'), state=TrueGoalsState.more_goals, flags=flags)
async def goals_add_goals_poll(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.more_goals_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_add_goals_poll'})
    answers = await poll_get(f'Usrs: {message.from_user.id}: TrueGoals: NotChosenFakeGoals:')
    answers.append('Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.')
    await message.answer_poll(text, answers, allows_multiple_answers=True, is_anonymous=False)


@router.poll_answer(state=TrueGoalsState.more_goals_poll, flags=flags)
async def goals_answer(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(TrueGoalsState.really_goals)
    lst_answers = poll_answer.option_ids
    user_new_fake_list = await poll_get(f"Usrs: {poll_answer.user.id}: TrueGoals: NotChosenFakeGoals:")
    user_new_fake_list.append('Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.')
    await del_key(f"Usrs: {poll_answer.user.id}: TrueGoals: NotChosenFakeGoals:")
    for index in lst_answers:
        if user_new_fake_list[index] != 'Я передумал(а). Не хочу обсуждать ничего из вышеперечисленного.':
            await poll_write(f'Usrs: {poll_answer.user.id}: TrueGoals: UserFakeGoals:', user_new_fake_list[index])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Кнопка"))
    await bot.send_message(poll_answer.user.id, f'НЕ настоящие цели войны ЗАГЛУШКА')


@router.message(F.text == "Кнопка", state=TrueGoalsState.really_goals, flags=flags)
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
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
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
    if 'Пропустим игру' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Пропустили')
    await state.set_state(TrueGoalsState.absurd)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Добавить абсурдности 🪄"))
    await simple_media(message, 'reasons_real_reasons', nmarkup.as_markup(resize_keyboard=True))


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
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


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
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Взглянем на факты 👀"))
    nmarkup.row(types.KeyboardButton(text="Пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('на факты 👀')), state=TrueGoalsState.power_change, flags=flags)
async def goals_will_add_sorry(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_change_of_power'})
    await message.answer(text)
    await goals_why_power_change(message)


@router.message(F.text == "Пропустим 👉", state=TrueGoalsState.power_change, flags=flags)
async def goals_sure_power_change(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_sure_power_change'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Всё-таки взглянем на факты 👀"))
    nmarkup.row(types.KeyboardButton(text="Да, двигаемся дальше 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Да, двигаемся дальше 👉", state=TrueGoalsState.power_change, flags=flags)
async def goals_why_power_change(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_why_power_change'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай посмотрим 👀"))
    nmarkup.row(types.KeyboardButton(text="Это мне не интересно, пропустим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Да, двигаемся дальше 👉", state=TrueGoalsState.power_change, flags=flags)
async def goals_paper_theses(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_paper_theses'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkup.add(types.KeyboardButton(text="Стало скучно, ближе к делу 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Интересно 🤔", state=TrueGoalsState.power_change, flags=flags)
async def goals_russian_world_nazi(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_russian_world_nazi'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Посмотрел(а) 📺", "Продолжим 👉"})) | (F.text == "Это мне не интересно, пропустим 👉") |
                (F.text == "Стало скучно, ближе к делу 👉"), state=TrueGoalsState.absurd, flags=flags)
async def goals_why_he_is_continued(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.putin)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_why_he_is_continued'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    nmarkup.row(types.KeyboardButton(text="Подожди! А почему Путин решил напасть именно сейчас? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
