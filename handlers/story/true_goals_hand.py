from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import poll_get, poll_write, del_key
from data_base.DBuse import sql_safe_select, mongo_count_docs
from filters.MapFilters import FakeGoals
from filters.MapFilters import OperationWar
from resources.all_polls import welc_message_one, true_and_idk_goals
from states.true_goals_states import TrueGoalsState

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


@router.message((F.text.contains('Понятно 👌')) | (F.text.contains('Да, выйти ⬇️')), flags=flags)
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
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains("Покажи результаты 📊")), state=TrueGoalsState.more_goals, flags=flags)
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
    result_text = await sql_safe_select('text', 'texts', {'name': 'goals_sort_reveal'})
    result_text = result_text + '\n '
    for text, value in sorted_dict.items():
        result_text = result_text + (str(value) + '% ' + str(text[1:])) + '\n'  # str(text[:1]) + '  — ' +
    await state.update_data(sorted_dict=sorted_dict)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkup.row(types.KeyboardButton(text="Продолжай 👉"))
    nmarkup.adjust(2)
    await state.set_state(TrueGoalsState.more_goals_2)
    await message.answer(result_text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Интересно 🤔')) | (F.text.contains('Продолжай 👉')), state=TrueGoalsState.more_goals_2,
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
                state=TrueGoalsState.more_goals_2, flags=flags)
async def goals_no_truth_for_us(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_cards_opened'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай! 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains("Давай! 👌"), state=TrueGoalsState.more_goals_2, flags=flags)
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
