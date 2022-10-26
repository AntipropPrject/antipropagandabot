import asyncio
from typing import List

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove, User
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import poll_get, redis_just_one_read, sql_select_row_like, mongo_game_answer, mongo_count_docs, \
    redis_just_one_write
from data_base.DBuse import sql_safe_select, data_getter
from filters.MapFilters import WebPropagandaFilter, PplPropagandaFilter, \
    NotYandexPropagandaFilter
from keyboards.map_keys import antip_killme_kb, polls_continue_kb
from resources.all_polls import antip_q1_options, antip_q2_options, antip_q3_options
from resources.variables import release_date
from states.antiprop_states import propaganda_victim
from states.true_goals_states import TrueGoalsState
from utilts import simple_media, dynamic_media_answer, simple_media_bot, simple_video_album, CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()

router.message.filter(state=propaganda_victim)


async def antip_wolves(user: User, bot: Bot, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай ⏳"))
    await state.set_state(propaganda_victim.next_0)
    await simple_media_bot(bot, user.id, 'antip_wolves', reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), flags=flags, state=propaganda_victim.next_0)
async def antip_black_and_white(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_black_and_white'})
    nmarkap = ReplyKeyboardBuilder()
    await state.set_state(propaganda_victim.fake_tv)
    nmarkap.add(types.KeyboardButton(text="Это интересно 👌"))
    nmarkap.row(types.KeyboardButton(text="Не хочу смотреть ложь по ТВ 🙅‍♀️"))
    nmarkap.adjust(2)
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Не хочу смотреть ложь по ТВ 🙅‍♀️'), state=propaganda_victim.fake_tv, flags=flags)
async def antip_just_a_little(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_just_a_little'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text="Хорошо, убедил 👌"))
    nmarkap.row(types.KeyboardButton(text="Ладно, посмотрю 🤷️"))
    tv_answers = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: tv:')
    polit_status = await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:')
    if 'Нет, не верю ни слову ⛔' in tv_answers \
            or "Не знаю, потому что не смотрю ни новости по ТВ, ни их интернет-версию 🤷‍♂" in tv_answers:
        if 'Противник войны 🕊' == polit_status:
            nmarkap.row(types.KeyboardButton(text="Всё равно не хочу смотреть ложь по ТВ 🙅‍♂️"))

    nmarkap.adjust(2, 1)

    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(((F.text.contains('Всё равно не хочу смотреть ложь')) | (F.text.contains('удивлен(а)')) | (
        F.text.contains('что по ТВ врут')) | (F.text.contains('Честно говоря, я в шоке'))), flags=flags)
async def antip_TV_makes_them_bad(message: Message):
    if 'Всё равно не хочу смотреть ложь' in message.text:
        await message.answer('Хорошо 👌')

    trust = await mongo_count_docs('database', 'statistics_new', {'tv_love_gen': 'Да, полностью доверяю ✅'})
    dont_trust = await mongo_count_docs('database', 'statistics_new', {'tv_love_gen': 'Нет, не верю ни слову ⛔'})
    maybe_trust = await mongo_count_docs('database', 'statistics_new', {'tv_love_gen': 'Скорее да 👍'})
    maybe_dont_trust = await mongo_count_docs('database', 'statistics_new', {'tv_love_gen': 'Скорее нет 👎'})

    var_true_and_trust = await mongo_count_docs(
        'database', 'statistics_new', {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️',
                                       'tv_love_gen': 'Да, полностью доверяю ✅'})
    var_true_and_dont_trust = await mongo_count_docs(
        'database', 'statistics_new', {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️',
                                       'tv_love_gen': 'Нет, не верю ни слову ⛔'})
    var_true_and_maybe_trust = await mongo_count_docs(
        'database', 'statistics_new', {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️',
                                       'tv_love_gen': 'Скорее да 👍'})
    var_true_and_maybe_dont_trust = await mongo_count_docs(
        'database', 'statistics_new', {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️',
                                       'tv_love_gen': 'Скорее нет 👎'})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_TV_makes_them_bad'}), trust)
    txt.replace('AA', var_true_and_trust)
    txt.replace('BB', var_true_and_maybe_trust, temp_base=maybe_trust)
    txt.replace('CC', var_true_and_maybe_dont_trust, temp_base=maybe_dont_trust)
    txt.replace('DD', var_true_and_dont_trust, temp_base=dont_trust)

    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkap.row(types.KeyboardButton(text="Это и так понятно 👌"))
    nmarkap.adjust(2)
    await message.answer(txt(), disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Это интересно 👌') | F.text.contains('Хорошо, убедил') |
                 F.text.contains('Ладно, посмотрю')), state=propaganda_victim.fake_tv, flags=flags)
async def antip_time_wasted(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="В чём подвох? 🤔"))
    nmarkap.row(types.KeyboardButton(text="Я заметил(а)! 😯"))
    nmarkap.adjust(2)
    await simple_media(message, 'antip_time_wasted', nmarkap.as_markup(resize_keyboard=True))


@router.message(((F.text == 'В чём подвох? 🤔') | (F.text == 'Я заметил(а)! 😯')), flags=flags)
async def antip_water_lie(message: Message, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай ⏳"))
    await state.set_state(propaganda_victim.next_2)
    await simple_media(message, 'antip_water_lie', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.next_2, flags=flags)
async def antip_cant_unsee(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_cant_unsee'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Это намеренная ложь 🗣"))
    nmarkap.add(types.KeyboardButton(text="Это случайность 🤷‍♀️️"))
    nmarkap.row(types.KeyboardButton(text='Это намеренная ложь, но и на Украине так же делают ☝️'))
    nmarkap.add(types.KeyboardButton(text="Не знаю 🤷‍♂️"))
    nmarkap.adjust(2, 1, 1)
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Это намеренная ложь, но и на') | F.text.contains('Не знаю 🤷‍♂️')
                 | F.text.contains('Это намеренная ложь') | F.text.contains('Это случайность')),
                state=propaganda_victim.next_2, flags=flags)
async def antip_eye_log(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_eye_log', value=message.text)
    if 'Это намеренная ложь, но и на Украине так же делают ☝️' == message.text:
        text_fake = await sql_safe_select('text', 'texts', {'name': 'antip_eye_log'})
        await message.answer(text_fake)
    await state.update_data(antip_eye_log_answ=message.text)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='corpses', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_how_could_they'})
    fake_1 = await mongo_count_docs('database', 'statistics_new',
                                    {'antip_eye_log': 'Это намеренная ложь 🗣'})
    fake_2 = await mongo_count_docs('database', 'statistics_new',
                                    {'antip_eye_log': 'Это намеренная ложь, но и на Украине так же делают ☝️'})
    random = await mongo_count_docs('database', 'statistics_new',
                                    {'antip_eye_log': 'Это случайность 🤷‍♀️️'})

    dont_know = await mongo_count_docs('database', 'statistics_new',
                                       {'antip_eye_log': 'Не знаю 🤷‍♂️'})
    fake = fake_1 + fake_2
    all_count = fake + random + dont_know
    try:
        fake_result = str(round(fake / all_count * 100))
        random_result = int(round(random / all_count * 100))
        dont_know_result = int(round(dont_know / all_count * 100))
        text = text.replace('XX', fake_result)
        text = text.replace('YY', str(random_result))
        text = text.replace('ZZ', str(dont_know_result))
        text = text.replace('AA', str(random_result + dont_know_result))
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')
        text = text.replace('ZZ', 'N/A')
        text = text.replace('AA', 'N/A')

    nmarkap = ReplyKeyboardBuilder()
    await state.set_state(propaganda_victim.next_1)
    nmarkap.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Продолжай') | F.text.contains('Хорошо 🤝')),
                state=propaganda_victim.next_1, flags=flags)
async def antip_stop_emotions(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'намеренная ложь' not in data['antip_eye_log_answ'] and 'Хорошо' not in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'antip_listen_to_facts'})
        nmarkap = ReplyKeyboardBuilder()
        nmarkap.row(types.KeyboardButton(text="Хорошо 🤝"))
        await state.set_state(propaganda_victim.next_1)
        await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))
    else:
        await state.set_state(propaganda_victim.start)
        text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_statistics'})
        nmarkap = ReplyKeyboardBuilder()
        await state.set_state(propaganda_victim.start)
        nmarkap.row(types.KeyboardButton(text="Открой мне глаза 👀"))
        nmarkap.row(types.KeyboardButton(text="Ну, удиви меня 🧐"))
        nmarkap.adjust(2)
        await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Открой мне глаза 👀', "Ну, удиви меня 🧐"})), flags=flags)
async def antip_censorship_lie(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.choose_TV)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_censorship_lie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    nmarkup.row(types.KeyboardButton(text="Больше похоже на теорию заговора 👽"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('теорию заговора')), state=propaganda_victim.choose_TV, flags=flags)
async def antip_conspirasy(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_conspiracy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.choose_TV, flags=flags)
async def antip_pile_of_lies(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='false_on_tv', value='Да')
    text = await sql_safe_select('text', 'texts', {'name': 'antip_pile_of_lies'})
    utv_list = ['1 канал 📺', 'Россия 1 / 24 📺', 'НТВ 📺', 'Звезда 📺']
    await state.update_data(first_tv_count=0, rus24_tv_count=0, HTB_tv_count=0, Star_tv_count=0)
    nmarkup = ReplyKeyboardBuilder()
    for channel in utv_list:
        nmarkup.row(types.KeyboardButton(text=channel))
    nmarkup.adjust(2, 2)
    nmarkup.row(types.KeyboardButton(text='Украинское ТВ 📺'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Украинское ТВ 📺") |
                 (F.text == "Подожди. А украинскую пропаганду ты показать не хочешь? 🤔")),
                state=(propaganda_victim.choose_TV, propaganda_victim.after_quizez),
                flags=flags)
async def antip_ukrainian_lie_1(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Сюжет посмотрел(а). Что с ним не так? 🤔'))
    await simple_media(message, 'antip_ukrainian_lie_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Сюжет посмотрел(а). Что с ним не так? 🤔"),
                state=(propaganda_victim.choose_TV, propaganda_victim.after_quizez), flags=flags)
async def antip_ukrainian_lie_2(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👉'))
    await simple_media(message, 'antip_ukrainian_lie_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжим 👉"), state=(propaganda_victim.choose_TV, propaganda_victim.after_quizez),
                flags=flags)
async def antip_already_not_involved(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_already_not_involved'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, продолжим 👌'))
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Ukr_tv:', 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('1 канал')) & ~(F.text.contains('🇷🇺')), flags=flags)
async def antiprop_tv_first(message: Message, state: FSMContext):
    try:
        await state.set_state(propaganda_victim.tv_first)
        count = (await state.get_data())['first_tv_count'] + 1
        await state.update_data(first_tv_count=count)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Сюжет посмотрел(а). Что с ним не так? 🤔"))
        await dynamic_media_answer(message, 'tv_first_lie_', count, nmarkup.as_markup(resize_keyboard=True))
    except TelegramBadRequest:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
        await message.answer('Похоже, что у меня больше нет сюжетов с этого канала.\nМожет быть, другой?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('1 / 24 📺')), flags=flags)
async def antiprop_tv_24(message: Message, state: FSMContext):
    try:
        await state.set_state(propaganda_victim.tv_russia24)
        count = (await state.get_data())['rus24_tv_count'] + 1
        await state.update_data(rus24_tv_count=count)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Сюжет посмотрел(а).Что с ним не так? 🤔"))
        await dynamic_media_answer(message, 'tv_24_lie_', count, nmarkup.as_markup(resize_keyboard=True))
    except TelegramBadRequest:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
        await message.answer('Похоже, что у меня больше нет сюжетов с этого канала.\nМожет быть, другой?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('НТВ 📺')), flags=flags)
async def antiprop_tv_HTB(message: Message, state: FSMContext):
    try:
        await state.set_state(propaganda_victim.tv_HTB)
        count = (await state.get_data())['HTB_tv_count'] + 1
        await state.update_data(HTB_tv_count=count)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Сюжет посмотрел(а). Что с ним не так? 🤔"))
        await dynamic_media_answer(message, 'tv_HTB_lie_', count, nmarkup.as_markup(resize_keyboard=True))
    except TelegramBadRequest:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
        await message.answer('Похоже, что у меня больше нет сюжетов с этого канала.\nМожет быть, другой?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Звезд')), flags=flags)
async def antiprop_tv_star(message: Message, state: FSMContext):
    try:
        await state.set_state(propaganda_victim.tv_star)
        count = (await state.get_data())['Star_tv_count'] + 1
        await state.update_data(Star_tv_count=count)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Сюжет посмотрел(а). Что с ним не так? 🤔"))
        await dynamic_media_answer(message, 'tv_star_lie_', count, nmarkup.as_markup(resize_keyboard=True))

    except TelegramBadRequest:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
        await message.answer('Похоже, что у меня больше нет сюжетов с этого канала.\nМожет быть, другой?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Что')) & F.text.contains('не так'), state=propaganda_victim.tv_first, flags=flags)
async def russia_tv_first_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['first_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_first_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с 1 канала 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, закончим смотреть ложь по ТВ ✋"))
    await dynamic_media_answer(message, 'tv_first_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Что')) & F.text.contains('не так'), state=propaganda_victim.tv_russia24, flags=flags)
async def tv_russia24_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['rus24_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_24_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет c России 1 / 24 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, закончим смотреть ложь по ТВ ✋"))
    await dynamic_media_answer(message, 'tv_24_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Что')) & F.text.contains('не так'), state=propaganda_victim.tv_HTB, flags=flags)
async def tv_HTB_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['HTB_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_HTB_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет НТВ 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, закончим смотреть ложь по ТВ ✋"))
    await dynamic_media_answer(message, 'tv_HTB_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Что')) & F.text.contains('не так'), state=propaganda_victim.tv_star, flags=flags)
async def tv_star_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['Star_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_star_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с телеканала Звезда 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, закончим смотреть ложь по ТВ ✋"))
    await dynamic_media_answer(message, 'tv_star_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Достаточно') & (F.text.contains('по ТВ ✋'))), flags=flags)
async def antip_TV_how_about_more(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_TV_how_about_more'})
    nmarkup = ReplyKeyboardBuilder()
    data = await state.get_data()
    if (await sql_select_row_like('assets', data['Star_tv_count'] + 1, {'name': 'tv_star_lie_'})) is not False or \
            (await sql_select_row_like('assets', data['HTB_tv_count'] + 1, {'name': 'tv_HTB_lie_'})) is not False or \
            (await sql_select_row_like('assets', data['rus24_tv_count'] + 1, {'name': 'tv_24_lie_'})) is not False or \
            (await sql_select_row_like('assets', data['first_tv_count'] + 1, {'name': 'tv_first_lie_'})) is not False:
        nmarkup.row(types.KeyboardButton(text='Нет, посмотрим ещё ложь по ТВ 📺'))
    nmarkup.row(types.KeyboardButton(text='Да, закончим с ТВ 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Да, закончим с ТВ 👌'), flags=flags)
async def antip_crossed_boy_1(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.choose_TV)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а) 📺'))
    await simple_media(message, 'antip_crossed_boy_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'), state=propaganda_victim.choose_TV, flags=flags)
async def antip_crossed_boy_2(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай... ⏳"))
    await simple_media(message, 'antip_crossed_boy_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай... ⏳'), flags=flags)
async def antip_crossed_boy_3(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой ужас 😱"))
    nmarkup.row(types.KeyboardButton(text="Давай продолжим 😕"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Какой ужас 😱") | (F.text == "Давай продолжим 😕"), flags=flags)
async def antip_be_honest(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='crucified_man', value=message.text)
    text2 = await sql_safe_select('text', 'texts', {'name': 'antip_be_honest'})
    await message.answer(text2, reply_markup=antip_killme_kb(), disable_web_page_preview=True)


@router.message(((F.text.contains('другой телеканал')) | (F.text.contains('ещё ложь по ТВ')) |
                 (F.text.contains('Хорошо, продолжим 👌'))),
                state=(propaganda_victim.choose_TV, propaganda_victim.tv_HTB, propaganda_victim.tv_star,
                       propaganda_victim.tv_russia24, propaganda_victim.tv_first), flags=flags)
async def antip_lies_for_you(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.choose_TV)
    bigdata = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', bigdata["first_tv_count"] + 1, {'name': "tv_first_lie_"}):
        nmarkup.row(types.KeyboardButton(text='1 канал 📺'))
    if await sql_select_row_like('assets', bigdata["rus24_tv_count"] + 1, {'name': "tv_24_lie_"}):
        nmarkup.add(types.KeyboardButton(text='Россия 1 / 24 📺'))
    if await sql_select_row_like('assets', bigdata["Star_tv_count"] + 1, {'name': "tv_star_lie_"}):
        nmarkup.row(types.KeyboardButton(text='Звезда 📺'))
    if await sql_select_row_like('assets', bigdata["HTB_tv_count"] + 1, {'name': "tv_HTB_lie_"}):
        nmarkup.add(types.KeyboardButton(text='НТВ 📺'))
    if not await redis_just_one_read(f'Usrs: {message.from_user.id}: Ukr_tv:'):
        nmarkup.add(types.KeyboardButton(text='Украинское ТВ 📺'))
    nmarkup.adjust(2)
    nmarkup.row(types.KeyboardButton(text="Достаточно, закончим смотреть ложь по ТВ ✋"))
    text = await sql_safe_select('text', 'texts', {'name': 'antip_lies_for_you'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WebPropagandaFilter(), (
        (F.text.contains('Интересно 🤔')) | (F.text.contains('Это и так понятно 👌'))), flags=flags)
@router.message(WebPropagandaFilter(), commands=["test"])
async def antip_not_only_TV(message: Message, web_lies_list: List[str], state: FSMContext):
    await state.set_state(propaganda_victim.web)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='grade_tv', value=message.text)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Покажи новость 👀"))
    all_answers_user = web_lies_list.copy()
    try:
        all_answers_user.remove('Meduza / Дождь / Би-би-си')
    except Exception as err:
        print(err)
    try:
        all_answers_user.remove("Википедия")
    except Exception as err:
        print(err)
    try:
        all_answers_user.remove("Яндекс")
    except Exception as err:
        print(err)
    try:
        all_answers_user.remove("Никому из них...")
    except Exception as err:
        print(err)

    await state.update_data(RIANEWS_c=0)
    await state.update_data(RUSSIATODAY_c=0)
    await state.update_data(TCHANEL_WAR_c=0)
    await state.update_data(TACC_c=0)
    await state.update_data(MINISTRY_c=0)
    await state.update_data(count_news=0)
    await state.update_data(all_answers_user=all_answers_user)  # Список ответов пользователя
    channel = all_answers_user[0]
    text = await sql_safe_select('text', 'texts', {'name': 'antip_not_only_TV'})
    text = text.replace('[[первый красный источник]]', channel)
    text = text.replace('[[ещё раз название источника]]', channel)
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


async def keyboard_for_next_chanel(text):
    markup = ReplyKeyboardBuilder()
    if text:
        markup.row(types.KeyboardButton(text=text + ' 👀'))
    markup.row(types.KeyboardButton(text="Достаточно, мне все понятно 🤚"))
    return markup.as_markup(resize_keyboard=True)


async def keyboard_for_all_chanel(lst_kb):
    markup = ReplyKeyboardBuilder()

    for button in lst_kb:
        markup.row(types.KeyboardButton(text=button + ' 👀'))
        markup.adjust(2)
    markup.row(types.KeyboardButton(text='Хватит, пропустим остальные источники 🙅‍♂️'))
    return markup.as_markup(resize_keyboard=True)


async def get_tag(viewed_channel) -> str:
    if 'РИА Новости' in viewed_channel:
        return 'RIANEWS'
    elif 'Russia Today' in viewed_channel:
        return 'RUSSIATODAY'
    elif 'Телеграм-канал «Война' in viewed_channel:
        return 'TCHANEL_WAR'
    elif 'ТАСС / Комсомольская правда' in viewed_channel:
        return 'TACC'
    elif 'Министерство' in viewed_channel:
        return 'MINISTRY'


async def get_count(tag: str, state) -> int:
    data = await state.get_data()
    if 'RIANEWS' == tag:
        count = data['RIANEWS_c']
        await state.update_data(RIANEWS_c=count + 1)
        return count
    elif 'RUSSIATODAY' == tag:
        count = data['RUSSIATODAY_c']
        await state.update_data(RUSSIATODAY_c=count + 1)
        return count
    elif 'TCHANEL_WAR' == tag:
        count = data['TCHANEL_WAR_c']
        await state.update_data(TCHANEL_WAR_c=count + 1)
        return count
    elif 'TACC' == tag:
        count = data['TACC_c']
        await state.update_data(TACC_c=count + 1)
        return count
    elif 'MINISTRY' == tag:
        count = data['MINISTRY_c']
        await state.update_data(MINISTRY_c=count + 1)
        return count


@router.message(((F.text.contains('Покажи новость 👀')) | (F.text.contains('РИА Новости 👀')) | (
        F.text.contains('Russia Today 👀')) | (
                         F.text.contains('Министерство обороны РФ 👀')) | (
                         F.text.contains('Телеграм-канал «Война с фейками» 👀')) | (F.text.contains('РБК 👀')) | (
                         F.text.contains('ТАСС / Комсомольская правда / Коммерсантъ / Lenta.ru / Известия 👀')) |
                 (F.text.contains('Хорошо, давай вернемся и посмотрим 👀'))) & ~(
        F.text.contains('еще')), flags=flags)  # вход в цикл
async def show_the_news(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_answers_user = data['all_answers_user']
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Новость посмотрел(а). Что с ней не так? 🤔'))
    if message.text == 'Покажи новость 👀':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='false_on_web_prop', value='Да')
        tag = await get_tag(all_answers_user[0])
        news = await data_getter(f"SELECT name FROM assets WHERE name LIKE '{tag}_media_%'")
        count = await get_count(tag, state)
        await state.update_data(viewed_channel=all_answers_user[0])
        await state.update_data(actual_count=count)
        await simple_media(message, news[count][0], reply_markup=markup.as_markup(resize_keyboard=True))
    elif message.text != 'Хорошо, давай вернемся и посмотрим 👀':
        tag = await get_tag(message.text)
        news = await data_getter(f"SELECT name FROM assets WHERE name LIKE '{tag}_media_%'")
        count = await get_count(tag, state)
        await state.update_data(viewed_channel=message.text[:-2])
        await state.update_data(actual_count=count)
        await simple_media(message, news[count][0], reply_markup=markup.as_markup(resize_keyboard=True))
    elif message.text == 'Хорошо, давай вернемся и посмотрим 👀':
        not_viewed_chanel = data['not_viewed_chanel']
        tag = await get_tag(not_viewed_chanel)
        news = await data_getter(f"SELECT name FROM assets WHERE name LIKE '{tag}_media_%'")
        count = await get_count(tag, state)
        await state.update_data(viewed_channel=not_viewed_chanel)
        await state.update_data(actual_count=count)
        await simple_media(message, news[count][0], reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Новость посмотрел(а). Что с ней не так? 🤔')), flags=flags)
async def revealing_the_news(message: types.Message, state: FSMContext):
    data = await state.get_data()
    count = data['actual_count']
    all_answers_user = data['all_answers_user']
    viewed_channel = data['viewed_channel']  # Просматриваемый канал  менять это для следующих каналов
    tag = await get_tag(viewed_channel)
    news_exposure = await data_getter(f"SELECT name FROM assets WHERE name LIKE '{tag}_exposure_%'")
    if len(news_exposure) != count + 1:
        keyboard = await keyboard_for_next_chanel(f'Покажи еще новость с {viewed_channel}')
        await simple_media(message, news_exposure[count][0], reply_markup=keyboard)
    else:
        all_answers_user.remove(viewed_channel)
        await state.update_data(all_answers_user=all_answers_user)
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text='Достаточно, мне все понятно 🤚'))
        await simple_media(message, news_exposure[count][0], reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(text_contains=('Покажи', 'еще', 'новость'), content_types=types.ContentType.TEXT, text_ignore_case=True,
                flags=flags)
async def show_more(message: types.Message, state: FSMContext):
    data = await state.get_data()
    viewed_channel = data['viewed_channel']  # Просматриваемый канал  менять это для следующих каналов
    tag = await get_tag(viewed_channel)
    count = await get_count(tag, state)
    actual_count = data['actual_count']
    await state.update_data(actual_count=actual_count + 1)
    news_media = await data_getter(f"SELECT name FROM assets WHERE name LIKE '{tag}_media_%'")
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Новость посмотрел(а). Что с ней не так? 🤔'))
    await simple_media(message, news_media[count][0], reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Достаточно, мне все понятно 🤚')), flags=flags)
async def revealing_the_news(message: Message, state: FSMContext):
    data = await state.get_data()
    viewed_channel = data['viewed_channel']
    all_answers_user = data['all_answers_user']
    try:  # Удаление кнопки с клавиатуры
        all_answers_user.remove(viewed_channel)  # В случае если
    except:  # Хоть один сюжет
        pass  # из источника
    await state.update_data(all_answers_user=all_answers_user)  # будет просмотрен
    if len(all_answers_user) != 0:
        all_answers_user = data['all_answers_user']
        markup = await keyboard_for_all_chanel(all_answers_user)
        text = await sql_safe_select('text', 'texts', {'name': 'antip_another_web_lie'})
        await message.answer(text, reply_markup=markup)
    else:
        redis = all_data().get_data_red()
        for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:*"):
            if key != "Яндекс" or key != "Википедия":
                redis.delete(key)
        propagandist_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
        if set(propagandist_list).isdisjoint(
                ("Дмитрий Песков", "Сергей Лавров",
                 "Маргарита Симоньян", "Владимир Соловьев", "Никита Михалков")) is False:
            await antip_bad_people_lies(message, propagandist_list, state)
        else:
            await antip_funny_propaganda(message, state)


@router.message((F.text.contains('Хватит, пропустим остальные источники 🙅‍♂️')), flags=flags)
async def skip_web(message: Message, state: FSMContext):
    data = await state.get_data()
    answer_channel = data['all_answers_user']  # Все выбранные источники
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Хорошо, давай вернемся и посмотрим 👀'))
    markup.row(types.KeyboardButton(text='Не надо, я и так знаю, что они врут 😒'))
    markup.row(types.KeyboardButton(text='Не надо, я всё равно буду доверять им 👍'))
    lst_web_answers = str(', '.join(answer_channel))
    next_channel = answer_channel[0]
    if next_channel == 'Министерство обороны РФ':
        next_channel = 'Министерства обороны РФ'
    if next_channel == 'Телеграм-канал «Война с фейками»':
        next_channel = 'Телеграм-каналa «Война с фейками»'

    text = await sql_safe_select('text', 'texts', {'name': 'antip_maybe_just_one'})
    text = text.replace('[[список неотсмотренных красных источников через запятую]]', lst_web_answers)
    text = text.replace('[[название следующего непросмотренного красного источника]]', next_channel)
    await state.update_data(not_viewed_chanel=answer_channel[0])
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('Не надо')) & ~(F.text.contains('интересно'))), state=(propaganda_victim.web,
                                                                                         propaganda_victim.options),
                flags=flags)
async def antip_web_exit_1(message: Message, state: FSMContext):
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:"):
        if key != "Яндекс" or key != "Википедия":
            redis.delete(key)
    if await state.get_state() == "propaganda_victim:options":
        await antip_funny_propaganda(message, state)
        redis.delete(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
        return
    propagandist_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    if set(propagandist_list).isdisjoint(("Дмитрий Песков", "Сергей Лавров",
                                          "Маргарита Симоньян", "Владимир Соловьев", "Никита Михалков")) is False:
        await antip_bad_people_lies(message, propagandist_list, state)
    else:
        await antip_funny_propaganda(message, state)


@router.message(PplPropagandaFilter(),
                (F.text.contains('Это и так понятно 👌')) | (F.text.contains('Интересно 🤔')), flags=flags)
async def antip_bad_people_lies(message: Message, ppl_lies_list: List[str], state: FSMContext):
    await state.set_state(propaganda_victim.ppl_propaganda)
    persons = ppl_lies_list
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    text = text.replace('[[первая красная личность]]', persons[0] if len(persons) > 0 else 'N/A')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнём 🙂"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Интересно 🤔')) | (F.text.contains('и так')) | (F.text.contains('я всё равно')),
                state=(propaganda_victim.choose_TV, propaganda_victim.web, propaganda_victim.ppl_propaganda,
                       propaganda_victim.fake_tv),
                flags=flags)
async def antip_funny_propaganda(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.quiz_1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи варианты ✍️"))
    await simple_media(message, 'antip_funny_propaganda', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Покажи варианты ✍️"), state=propaganda_victim.quiz_1, flags=flags)
async def antip_quiz_1(message: Message, bot: Bot):
    await bot.send_poll(message.from_user.id, 'Сколько?', antip_q1_options,
                        is_anonymous=False, correct_option_id=3, type='quiz',
                        reply_markup=polls_continue_kb())


@router.poll_answer(state=propaganda_victim.quiz_1, flags=flags)
async def antip_quiz_1_answer(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    answer = poll_answer.option_ids[0]
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='antiprop_quiz_1',
                                value=antip_q1_options[answer])
    p_all = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_1': {'$exists': True}})
    p3000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_1': 'Около 3000 человек'})
    p11000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_1': 'Около 11000 человек'})
    p25000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_1': 'Около 25000 человек'})
    p40000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_1': 'Около 40000 человек'})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_quiz_1_answer'}), p_all)
    txt.replace('AA', p3000)
    txt.replace('BB', p11000)
    txt.replace('CC', p25000)
    txt.replace('DD', p40000)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 🤔"))
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await simple_media_bot(bot, poll_answer.user.id, 'antip_quiz_1_answer', nmarkup.as_markup(resize_keyboard=True),
                           custom_caption=txt())


@router.message((F.text.in_({'Интересно 🤔', "Продолжим 👉"})), state=propaganda_victim.quiz_1, flags=flags)
async def antip_how_much_they_lie(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.quiz_2)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи варианты ✍️"))
    await simple_media(message, 'antip_how_much_they_lie', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Покажи варианты ✍️"), state=propaganda_victim.quiz_2, flags=flags)
async def antip_quiz_2(message: Message, bot: Bot):
    await bot.send_poll(message.from_user.id, 'Сколько?', antip_q2_options,
                        is_anonymous=False, correct_option_id=3, type='quiz',
                        reply_markup=polls_continue_kb())


@router.poll_answer(state=propaganda_victim.quiz_2, flags=flags)
async def antip_quiz_2_answer(poll_answer: types.PollAnswer, bot: Bot):
    answer = poll_answer.option_ids[0]
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='antiprop_quiz_2',
                                value=antip_q2_options[answer])
    s_all = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_2': {'$exists': True}})
    s1000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_2': 'Около 1000 скоплений'})
    s4000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_2': 'Около 4000 скоплений'})
    s12000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_2': 'Около 12000 скоплений'})
    s39000 = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_2': 'Около 39000 скоплений'})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_quiz_2_answer'}), s_all)
    txt.replace('AA', s1000)
    txt.replace('BB', s4000)
    txt.replace('CC', s12000)
    txt.replace('DD', s39000)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👉"))
    nmarkup.add(types.KeyboardButton(text="Чтооо? 😳"))
    await simple_media_bot(bot, poll_answer.user.id, 'antip_quiz_2_answer', nmarkup.as_markup(resize_keyboard=True),
                           custom_caption=txt())


@router.message((F.text.in_({'Продолжим 👉', "Чтооо? 😳"})), state=propaganda_victim.quiz_2, flags=flags)
async def antip_noone_will_do_this(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await state.set_state(propaganda_victim.quiz_2)
    await simple_media(message, 'antip_noone_will_do_this', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.quiz_2, flags=flags)
async def antip_not_only_numbers(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А на что ещё? 🤔"))
    await simple_media(message, 'antip_not_only_numbers', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "А на что ещё? 🤔"), state=propaganda_victim.quiz_2, flags=flags)
async def antip_what_they_told_us(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.quiz_3)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_they_told_us'})
    await message.answer(text, disable_web_page_preview=True)
    await message.answer_poll('Какие?', antip_q3_options, allows_multiple_answers=True, is_anonymous=False,
                              reply_markup=polls_continue_kb())


@router.poll_answer(state=propaganda_victim.quiz_3, flags=flags)
async def antip_unhumanity(poll_answer: types.PollAnswer, bot: Bot):
    answers = poll_answer.option_ids
    if answers == [0, 1, 2, 3, 4]:
        tomongo = 'Отметил все'
    else:
        tomongo = 'Не отметил все'
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='antiprop_quiz_3',
                                value=tomongo)
    l_all = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_3': {'$exists': True}})
    l_right = await mongo_count_docs('database', 'statistics_new', {'antiprop_quiz_3': 'Отметил все'})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_unhumanity'}), l_all)
    txt.replace('XX', l_right)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что же? 🤔"))
    await simple_media_bot(bot, poll_answer.user.id, 'antip_unhumanity', nmarkup.as_markup(resize_keyboard=True),
                           custom_caption=txt())


@router.message((F.text == "Что же? 🤔"), state=propaganda_victim.quiz_3, flags=flags)
async def antip_torture_not_recommended(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_torture_not_recommended'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай 👉"))
    nmarkup.row(types.KeyboardButton(text="Покажи эти видео 😯"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Покажи эти видео 😯"), state=propaganda_victim.quiz_3, flags=flags)
async def antip_torture_really_not_recommended(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_torture_really_not_recommended'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, покажи эти видео 🤯"))
    nmarkup.row(types.KeyboardButton(text="Не стоит, давай продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, покажи эти видео 🤯"), state=propaganda_victim.quiz_3, flags=flags)
async def antip_torture(message: Message, bot: Bot):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_torture_really_not_recommended'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я готов(а) продолжить 👉"))
    await simple_video_album(message, bot, ['antip_torture_v_1', 'antip_torture_v_2', 'antip_torture_v_3'])
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('родолж')) & (F.text.contains('👉'))
                 & ~(F.text.contains('аем'))), state=propaganda_victim.quiz_3, flags=flags)
async def antip_chicken_and_egg(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_chicken_and_egg'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В целом согласен(а) 😌"))
    nmarkup.add(types.KeyboardButton(text="Продолжаем 👉"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    ((F.text.contains('В целом согласен(а)')) | (F.text.contains('Продолжаем 👉')) | (F.text == "Хорошо, продолжим 👌")),
    state=(propaganda_victim.quiz_3, propaganda_victim.after_quizez), flags=flags)
async def antip_german_list(message: Message, state: FSMContext):
    if 'Хорошо, продолжим' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'antip_return_to_german_list'})
        await message.answer(text)
        await asyncio.sleep(1)
    await state.set_state(propaganda_victim.after_quizez)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Интересно 👍"))
    nmarkup.add(types.KeyboardButton(text="Скучновато 👎"))
    if not await redis_just_one_read(f'Usrs: {message.from_user.id}: Ukr_tv:'):
        nmarkup.row(types.KeyboardButton(text="Подожди. А украинскую пропаганду ты показать не хочешь? 🤔"))
    await simple_media(message, 'antip_german_list', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Интересно 👍") | (F.text == "Скучновато 👎")),
                state=propaganda_victim.after_quizez, flags=flags)
async def antip_truth_game_start(message: Message):
    if message.text == "Интересно 👍":
        text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start'})
    else:
        text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем! 🚀"))
    nmarkup.row(types.KeyboardButton(text="Пропустим игру 🙅‍♀️"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Начнем! 🚀") | (F.text == "Продолжаем, давай еще! 👉") |
                (F.text == "Нет, поиграем ещё! 👈"), flags=flags)
async def antip_truth_game_start_question(message: Message, state: FSMContext):
    if message.text == 'Начнем! 🚀':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true',
                                    value='Начали и НЕ закончили')
    try:
        count = (await state.get_data())['gamecount']
    except KeyError:
        count = 0
    how_many_rounds = (await data_getter("SELECT COUNT (*) FROM public.truthgame"))[0][0]
    if count < how_many_rounds:
        count += 1
        truth_data = (await data_getter(f"""SELECT * FROM (Select truth, a.t_id as plot_media, t.text as plot_text,
                                         belivers, nonbelivers,
                                         t2.text as rebb_text, a2.t_id as rebb_media,
                                         ROW_NUMBER () OVER (ORDER BY id), id FROM public.truthgame
                                         left outer join assets a on a.name = truthgame.asset_name
                                         left outer join assets a2 on a2.name = truthgame.reb_asset_name
                                         left outer join texts t on truthgame.text_name = t.name
                                         left outer join texts t2 on truthgame.rebuttal = t2.name)
                                         AS sub WHERE row_number = {count}"""))[0]
        await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                not_belive=truth_data[4], reb_media=truth_data[6], game_id=truth_data[8])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это правда ✅"))
        nmarkup.add(types.KeyboardButton(text="Это ложь ❌"))
        if truth_data[1] is not None:
            capt = ""
            if truth_data[2] is not None:
                capt = truth_data[2]
            try:
                await message.answer_video(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except TelegramBadRequest:
                await message.answer_photo(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="🤝 Продолжим"))
        await message.answer(
            "У меня закончились сюжеты. Спасибо за игру🤝",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Это правда ✅") | (F.text == "Это ложь ❌"), flags=flags)
async def antip_truth_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    END = bool(data['gamecount'] == (await data_getter('SELECT COUNT(id) FROM public.truthgame'))[0][0])
    nmarkup = ReplyKeyboardBuilder()
    if END is False:
        nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще! 👉"))
        nmarkup.row(types.KeyboardButton(text="Достаточно, двигаемся дальше  🙅‍♀️"))
    else:
        nmarkup.row(types.KeyboardButton(text="🤝 Продолжим"))
    answer_group, reality = str(), str()
    if message.text == "Это правда ✅":
        if data['truth'] is True:
            reality = "Правильно! Это правда!"
        elif data['truth'] is False:
            reality = "Неверно! Это ложь!"
        answer_group = 'belivers'
    elif message.text == "Это ложь ❌":
        if data['truth'] is True:
            reality = "Неверно! Это правда!"
        elif data['truth'] is False:
            reality = "Правильно! Это ложь!"
        answer_group = 'nonbelivers'
    await mongo_game_answer(message.from_user.id, 'truthgame', data['game_id'], answer_group, {'id': data['game_id']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    text = reality + f'\n\nРезультаты других участников:\n✅ <b>Правда:</b> {round(t_percentage * 100)}%\n' \
                     f'❌ <b>Ложь</b>: {round((100 - t_percentage * 100))}%' + '\n\nПодтверждение - ниже.'
    reb = data['rebuttal']
    media = data['reb_media']
    if media is None:
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
        await message.answer(reb, disable_web_page_preview=True)
    else:
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
        try:
            await message.answer_video(media, caption=reb)
        except TelegramBadRequest:
            await message.answer_photo(media, caption=reb)
    if END is True:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true', value='Начали и закончили')
        await message.answer('У меня закончились сюжеты. Спасибо за игру🤝')


@router.message(F.text == 'Достаточно, двигаемся дальше  🙅‍♀️', flags=flags)
async def sure_you_are(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, поиграем ещё! 👈"))
    nmarkup.row(types.KeyboardButton(text="Да, продолжим общаться 👌"))
    await message.answer('Уверены?', reply_markup=nmarkup.as_markup(resize_keyboard=True),
                         disable_web_page_preview=True)


@router.message(NotYandexPropagandaFilter(), ((F.text == "Пропустим игру 🙅‍♀️") | (F.text == '🤝 Продолжим')
                                              | (F.text == 'Да, продолжим общаться 👌')), flags=flags)
async def antip_yandex_do_you_like_it(message: Message, state: FSMContext):
    if message.text == 'Пропустим игру 🙅‍♀️':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true', value='Пропустили')
        await message.answer('Хорошо')
    await state.set_state(propaganda_victim.yandex)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_yandex_do_you_like_it'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Часто 👍"))
    nmarkup.add(types.KeyboardButton(text="Редко 🤏"))
    nmarkup.add(types.KeyboardButton(text="Никогда 👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Часто 👍", "Редко 🤏"})), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex_but_I_want(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_yandex_but_I_want'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Никогда 👎"), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex_do_you_want_to_know(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_yandex_do_you_want_to_know'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Расскажи, интересно! 👌"))
    nmarkup.row(types.KeyboardButton(text="Не надо, не интересно 🙅‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Пропустим игру 🙅‍♀️") | (F.text == '🤝 Продолжим')
                 | (F.text == 'Да, продолжим общаться 👌')), flags=flags)
@router.message((F.text == "Давай 👌"), state=propaganda_victim.yandex, flags=flags)
async def antip_propaganda_here_too(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.yandex)
    if message.text == 'Пропустим игру 🙅‍♀️':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true', value='Пропустили')
        await message.answer('Хорошо')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай 🤔"))
    await simple_media(message, 'antip_propaganda_here_too', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Продолжай 🤔") | (F.text == "Расскажи, интересно! 👌")),
                state=propaganda_victim.yandex, flags=flags)
async def antip_they_lie_to_you(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, 'antip_they_lie_to_you', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Посмотрел(а) 📺"), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'antip_yandex', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex_rupor(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_yandex_rupor'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я удивлён(а) 🤔"))
    nmarkup.add(types.KeyboardButton(text="Я не удивлён(а) 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Я не верю 😕"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Я не верю 😕"), state=propaganda_victim.yandex, flags=flags)
async def antip_well_you_will(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_well_you_will'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('удивлён')) | (F.text == 'Продолжим 👌'), state=propaganda_victim.yandex, flags=flags)
@router.message(F.text == "Не надо, не интересно 🙅‍♂️", flags=flags)
async def antip_family_conflicts(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.final)
    if 'удивлён' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_yandex_rupor', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_family_conflicts'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, были ссоры 🗣"))
    nmarkup.add(types.KeyboardButton(text="Нет, ссор не было 🙏"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Нет, ссор не было 🙏") | (F.text == "Да, были ссоры 🗣"),
                state=propaganda_victim.final, flags=flags)
async def antip_people_conflicts(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='family_conflicts', value=message.text)
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Antip: family:', message.text)
    f_all = await mongo_count_docs('database', 'statistics_new', {'family_conflicts': {'$exists': True}})
    f_no = await mongo_count_docs('database', 'statistics_new', {'family_conflicts': "Нет, ссор не было 🙏"})
    f_yes = await mongo_count_docs('database', 'statistics_new', {'family_conflicts': "Да, были ссоры 🗣"})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_people_conflicts'}), f_all)
    txt.replace('XX', f_yes)
    txt.replace('YY', f_no)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, такие есть 🤐"))
    nmarkup.add(types.KeyboardButton(text="Нет, таких нет 🙏"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, такие есть 🤐") | (F.text == "Нет, таких нет 🙏"),
                state=propaganda_victim.final, flags=flags)
async def antip_zombie_everywere(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='breaking_conflicts', value=message.text)
    b_all = await mongo_count_docs('database', 'statistics_new', {'breaking_conflicts': {'$exists': True}})
    b_no = await mongo_count_docs('database', 'statistics_new', {'breaking_conflicts': "Нет, таких нет 🙏"})
    b_yes = await mongo_count_docs('database', 'statistics_new', {'breaking_conflicts': "Да, такие есть 🤐"})
    if 'Нет' in await redis_just_one_read(f'Usrs: {message.from_user.id}: Antip: family:') \
            and 'Нет' in message.text:
        text_tag = 'antip_zombie_everywere_not_you'
    else:
        text_tag = 'antip_zombie_everywere_you'
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': text_tag}), b_all)
    txt.replace('XX', b_yes)
    txt.replace('YY', b_no)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.final, flags=flags)
async def antip_honesty_in_2022(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_honesty_in_2022'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, существуют 👍"))
    nmarkup.add(types.KeyboardButton(text="Скорее нет, все СМИ врут 👎"))
    nmarkup.row(types.KeyboardButton(text="Может да, может нет 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Скорее да, существуют 👍") | (F.text == "Скорее нет, все СМИ врут 👎")
                 | (F.text == "Может да, может нет 🤷‍♀️")), state=propaganda_victim.final, flags=flags)
async def antip_normal_sources(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_honest_sources', value=message.text)
    h_all = await mongo_count_docs('database', 'statistics_new', {'antip_honest_sources': {'$exists': True}})
    h_no = await mongo_count_docs('database', 'statistics_new', {'antip_honest_sources': "Скорее нет, все СМИ врут 👎"})
    h_yes = await mongo_count_docs('database', 'statistics_new', {'antip_honest_sources': "Скорее да, существуют 👍"})
    h_mb = await mongo_count_docs('database', 'statistics_new', {'antip_honest_sources': "Может да, может нет 🤷‍♀️"})
    if message.text == 'Скорее да, существуют 👍':
        text_tag = 'antip_normal_sources_normal'
    else:
        text_tag = 'antip_normal_sources_zombie'
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': text_tag}), h_all)
    txt.replace('AA', h_yes)
    txt.replace('BB', h_no)
    txt.replace('CC', h_mb)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Расскажи 🙂"))
    nmarkup.row(types.KeyboardButton(text="Подожди! Если честные СМИ существуют,"
                                          " то люди смотрели бы их, а не пропаганду 🤔"))
    nmarkup.row(types.KeyboardButton(text="Это мне неинтересно ️🙅‍♂️"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('смотрели бы их')), state=propaganda_victim.final, flags=flags)
async def antip_orwell(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_orwell'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Расскажи 🙂"))
    nmarkup.row(types.KeyboardButton(text="Это мне неинтересно ️🙅‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Расскажи 🙂"), state=propaganda_victim.final, flags=flags)
async def antip_three_categories(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_three_categories'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Назови эти СМИ 👀"))
    nmarkup.row(types.KeyboardButton(text=
                                     "Подожди! А не лучше быть подписанным и на российские, и на украинские СМИ? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.contains('лучше быть подписанным '), state=propaganda_victim.final, flags=flags)
async def antip_good_idea(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_good_idea'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Назови эти СМИ 👀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Продолжай ⏳')), flags=flags, state=propaganda_victim.next_3)
async def antip_look_at_it_yourself(message: Message, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text='Спасибо, не знaл(а) 🙂'))
    nmarkap.add(types.KeyboardButton(text='Ничего нового 🤷‍♀️'))
    nmarkap.add(types.KeyboardButton(text='Я не верю 😕'))
    nmarkap.adjust(2)
    await simple_media(message, 'antip_look_at_it_yourself', reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Я не верю')), flags=flags, state=propaganda_victim.next_3)
async def antip_learn_yourself(message: Message, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text='Продолжим 👌'))
    text = await sql_safe_select('text', 'texts', {'name': 'antip_learn_yourself'})
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('не знaл(а)')) | (F.text.contains('Ничего нового')) | (F.text == 'Продолжим 👌')),
                state=(propaganda_victim.wiki, propaganda_victim.next_3), flags=flags)
@router.message((F.text.contains('двигаемся дальше')), flags=flags)
async def antip_ok(message: Message, state: FSMContext):
    if 'Спасибо' in message.text or 'нового' in message.text or 'не верю' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_look_at_it_yourself', value=message.text)
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай 🤔'))
    await state.set_state(propaganda_victim.final)
    await message.answer("У меня есть анекдот", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай 🤔'), state=propaganda_victim.final, flags=flags)
async def antip_anecdote(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_anecdote'})
    await state.clear()
    await state.set_state(propaganda_victim.final_end)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="😁"))
    nmarkup.row(types.KeyboardButton(text="🙂"))
    nmarkup.row(types.KeyboardButton(text="😕"))
    nmarkup.adjust(3)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'😁', "🙂", "😕"})), state=propaganda_victim.final_end, flags=flags)
async def antip_hole_in_deck(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='reaction_on_anecdot', value=message.text)
    a_all = await mongo_count_docs('database', 'statistics_new', {'reaction_on_anecdot': {'$exists': True}})
    a_hoho = await mongo_count_docs('database', 'statistics_new', {'reaction_on_anecdot': "😁"})
    a_haha = await mongo_count_docs('database', 'statistics_new', {'reaction_on_anecdot': "🙂"})
    a_meh = await mongo_count_docs('database', 'statistics_new', {'reaction_on_anecdot': "😕"})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_anecdote_reaction'}), a_all)
    txt.replace('XX', a_hoho)
    txt.replace('YY', a_haha)
    txt.replace('ZZ', a_meh)
    await message.answer(txt())
    await asyncio.sleep(1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    nmarkup.add(types.KeyboardButton(text="Забавная картинка 🙂"))
    await simple_media(message, 'antip_hole_in_deck', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Назови эти СМИ 👀') | (F.text.contains('Это мне неинтересно ️🙅‍♂️'))), flags=flags)
async def antip_best_of_the_best(message: Message):
    if 'неинтересно' in message.text:
        fake_text = await sql_safe_select('text', 'texts', {'name': 'antip_to_the_point'})
        await message.answer(fake_text)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text='О чём? 🤔'))
    nmarkap.row(types.KeyboardButton(text="Готовь деньги 😉️"))
    nmarkap.adjust(2)
    await simple_media(message, 'antip_best_of_the_best', reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('О чём? 🤔') | (F.text.contains('Готовь деньги'))), flags=flags)
async def antip_many_links_normal(message: Message):
    if await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: BBC'):
        nmarkap = ReplyKeyboardBuilder()
        nmarkap.add(types.KeyboardButton(text="Готов(а) продолжить 👌"))
        text = await sql_safe_select('text', 'texts', {'name': 'antip_many_links_normal'})
        await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    else:
        nmarkap = ReplyKeyboardBuilder()
        nmarkap.add(types.KeyboardButton(text="Всё, я подписан(а)! ✅ Продолжим! 👌"))
        nmarkap.row(types.KeyboardButton(text="Я не буду подписываться. ❌ Но я готов(а) продолжить. 👌"))
        text = await sql_safe_select('text', 'texts', {'name': 'antip_many_links_zombie'})
        await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Готов(а) продолжить') | (F.text.contains('я подписан(а)')) |
                 (F.text.contains('Я не буду подписываться.'))), flags=flags)
async def antip_forbidden_truth(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_forbidden_truth'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text="Какой ресурс? 🤔"))
    nmarkap.add(types.KeyboardButton(text="Википедия что ли? 🙂"))
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Какой ресурс? 🤔') | (F.text.contains('Википедия что ли? 🙂'))), flags=flags)
async def antip_bite_me(message: Message):
    if 'Википедия что ли' in message.text:
        fake_text = await sql_safe_select('text', 'texts', {'name': 'antip_bite_me'})
        await message.answer(fake_text)
    if await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: NotWiki'):
        nmarkap = ReplyKeyboardBuilder()
        nmarkap.add(types.KeyboardButton(text="Там статьи может редактировать любой человек ✍️"))
        nmarkap.add(types.KeyboardButton(text="Википедия — проект Запада 🇺🇸"))
        nmarkap.add(types.KeyboardButton(text="Не пользуюсь / Не слышал(а) 🤷‍♀️"))
        nmarkap.add(types.KeyboardButton(text="Случайно, вообще я доверяю Википедии 👌"))
        nmarkap.adjust(1, 2, 1)
        text = await sql_safe_select('text', 'texts', {'name': 'antip_why_not_wiki'})
        await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    else:
        nmarkap = ReplyKeyboardBuilder()
        nmarkap.add(types.KeyboardButton(text="Расскажи 🙂️"))
        nmarkap.add(types.KeyboardButton(text="Не надо, двигаемся дальше 👉"))
        p_all = await mongo_count_docs('database', 'statistics_new', {'web_prop_ex': {'$exists': True}})
        p_wiki = await mongo_count_docs('database', 'statistics_new', {'web_prop_ex': "Википедия"})
        txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'antip_two_words'}), p_all)
        txt.replace('XX', p_wiki)
        await message.answer(txt(), reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    (F.text.contains('Там статьи может редактировать любой человек') | (F.text.contains('Википедия — проект Запада')) |
     (F.text.contains('Не пользуюсь / Не слышал(а)')) | (F.text.contains('Случайно, вообще я доверяю Википедии')) |
     (F.text.contains('Расскажи 🙂'))), flags=flags)
async def antip_clear_and_cool(message: Message, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.add(types.KeyboardButton(text='Продолжай ⏳'))
    text = await sql_safe_select('text', 'texts', {'name': 'antip_clear_and_cool'})
    await state.set_state(propaganda_victim.next_3)
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Продолжай ⏳', "Забавная картинка 🙂"})), state=propaganda_victim.final_end, flags=flags)
async def antip_how_they_made_it(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой ужас 😯"))
    nmarkup.add(types.KeyboardButton(text="Смешно 🙂"))
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await simple_media(message, 'antip_how_they_made_it', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Какой ужас 😯", "Смешно 🙂", "Продолжим 👉"})),
                state=propaganda_victim.final_end, flags=flags)
async def antip_only_tip_of_the_berg(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Очень интересно 👍"))
    nmarkup.add(types.KeyboardButton(text="Интересно, но слегка затянуто 🤏"))
    nmarkup.row(types.KeyboardButton(text="Где-то интересно, где-то скучно 🙂"))
    nmarkup.row(types.KeyboardButton(text="Довольно скучно 🥱"))
    await simple_media(message, 'antip_only_tip_of_the_berg', reply_markup=nmarkup.as_markup(resize_keyboard=True))
