import asyncio
from typing import List

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from data_base.DBuse import poll_get, redis_just_one_read, sql_select_row_like, mongo_game_answer, \
    redis_check
from data_base.DBuse import sql_safe_select, data_getter
from filters.MapFilters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter, \
        PoliticsFilter, WikiFilter, YandexPropagandaFilter
from handlers import true_resons_hand
from keyboards.map_keys import antip_why_kb, antip_killme_kb
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_update_stat, mongo_update_stat_new
from utilts import simple_media, dynamic_media_answer

flags = {"throttling_key": "True"}
router = Router()

router.message.filter(state=propaganda_victim)


@router.message((F.text.contains('такое пропаганда')), flags=flags)
async def antip_what_is_prop(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_is_prop'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Мне интересно 👌"))
    nmarkap.add(types.KeyboardButton(text="Ну давай... 🤨"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Мне интересно 👌') | (F.text == 'Ну давай... 🤨'), flags=flags)
async def antip_time_wasted(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="В чём подвох? 🤔"))
    nmarkap.add(types.KeyboardButton(text="Я заметил(а)! 😯"))
    await simple_media(message, 'antip_time_wasted', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'В чём подвох? 🤔') | (F.text == 'Я заметил(а)! 😯'), flags=flags)
async def antip_water_lie(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай ⌛️"))
    await simple_media(message, 'antip_water_lie', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⌛️"), state=propaganda_victim.start, flags=flags)
async def antip_cant_unsee(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_cant_unsee'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Это случайность, просто редакторам скинули фейк, а они не проверили 🤷‍♀️"))
    nmarkap.row(types.KeyboardButton(text="Это явная ложь, не случайность 🗣"))
    nmarkap.add(types.KeyboardButton(text="Не знаю, давай продолжим 👉"))
    nmarkap.row(types.KeyboardButton(text="Это специальная ложь, но и на Украине так же делают ☝️"))
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('редакторам скинули фейк')), flags=flags)
async def antip_cant_unsee(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='corpses', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_fake_on_main'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains(' специальная ложь, но')), flags=flags)
async def antip_eye_log(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='corpses', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_eye_log'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(((F.text == "Хорошо 👌") | (F.text.contains('явная ложь')) | (F.text.contains('Не знаю, давай'))))
async def antip_stop_emotions(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_stop_emotions'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 🤝"))
    await message.answer(text, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Скорее да"), (F.text == "Хорошо 🤝"))
async def antiprop_rather_yes_start(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='corpses', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Не знаю, потому что не смотрю ни новости по ТВ, ни их интернет-версию 🤷‍♂"),
                (F.text == "Хорошо 🤝"))
async def antiprop_rather_yes_start_no_tv(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antiprop_rather_yes_start_no_tv'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Пропустим этот шаг 👉"))
    nmarkup.row(types.KeyboardButton(text="Покажи ложь на ТВ — мне интересно посмотреть! 📺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == "Хорошо 🤝"))
async def antip_all_yes_TV(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(TVPropagandaFilter(option="Скорее нет"), (F.text == "Хорошо 🤝"))
async def rather_no_TV(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Нет, не верю ни слову"), (F.text == "Хорошо 🤝"))
async def antip_all_no_TV(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Пропустим этот шаг 👉"))
    nmarkup.row(types.KeyboardButton(text="Покажи ложь на ТВ — мне интересно посмотреть! 📺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == 'Продолжай ⏳'),
                state=propaganda_victim.start, flags=flags)
async def antip_all_yes_TV_2(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    (F.text.in_({'Открой мне глаза 👀', "Ну удиви меня 🤔", "Покажи ложь на ТВ — мне интересно посмотреть! 📺"})),
    flags=flags)
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
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('1 канал')) & ~(F.text.contains('🇷🇺')), flags=flags)
async def antiprop_tv_first(message: Message, state: FSMContext):
    try:
        await state.set_state(propaganda_victim.tv_first)
        count = (await state.get_data())['first_tv_count'] + 1
        await state.update_data(first_tv_count=count)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
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
        nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
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
        nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
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
        nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
        await dynamic_media_answer(message, 'tv_star_lie_', count, nmarkup.as_markup(resize_keyboard=True))

    except TelegramBadRequest:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
        await message.answer('Похоже, что у меня больше нет сюжетов с этого канала.\nМожет быть, другой?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_first, flags=flags)
async def russia_tv_first_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['first_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_first_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с 1 канала 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно ✋"))
    await dynamic_media_answer(message, 'tv_first_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_russia24, flags=flags)
async def tv_russia24_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['rus24_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_24_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет c России 1 / 24 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно ✋"))
    await dynamic_media_answer(message, 'tv_24_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_HTB, flags=flags)
async def tv_HTB_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['HTB_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_HTB_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет НТВ 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно ✋"))
    await dynamic_media_answer(message, 'tv_HTB_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_star, flags=flags)
async def tv_star_reb(message: Message, state: FSMContext):
    count = (await state.get_data())['Star_tv_count']
    nmarkup = ReplyKeyboardBuilder()
    if await sql_select_row_like('assets', count + 1, {'name': 'tv_star_lie_'}) is not False:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с телеканала Звезда 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔄"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно ✋"))
    await dynamic_media_answer(message, 'tv_star_reb_', count, nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Достаточно') & (F.text.contains('понятно ✋'))), flags=flags)
async def antip_crossed_boy_1(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а) 📺'))
    await simple_media(message, 'antip_crossed_boy_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'), flags=flags)
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
async def antip_crossed_boy_3(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='grade_tv', value=message.text)
    text2 = await sql_safe_select('text', 'texts', {'name': 'antip_be_honest'})
    await message.answer(text2, reply_markup=antip_killme_kb(), disable_web_page_preview=True)


@router.message((F.text.contains('другой телеканал')) | (F.text.contains('посмотреть еще')), flags=flags)
async def antip_another_tv(message: Message, state: FSMContext):
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
    nmarkup.adjust(2)
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно ✋"))
    text = await sql_safe_select('text', 'texts', {'name': 'antip_lies_for_you'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WebPropagandaFilter(), (
        (F.text.contains('шаг')) | (F.text.contains('удивлён')) | (F.text.contains('шоке')) |
        (F.text.contains('знал'))), flags=flags)
@router.message(WebPropagandaFilter(), commands=["test"])
async def antip_not_only_TV(message: Message, web_lies_list: List[str], state: FSMContext):
    if 'шаг' not in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='crucified_man', value=message.text)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Покажи новость 👀"))
    all_answers_user = web_lies_list.copy()
    try:
        all_answers_user.remove('Meduza / BBC / Радио Свобода / Медиазона / Настоящее время / Популярная Политика')
    except:
        pass
    try:
        all_answers_user.remove("Википедия")
    except:
        pass
    try:
        all_answers_user.remove("Яндекс")
    except:
        pass
    try:
        all_answers_user.remove("Никому из них...")
    except:
        pass

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
    elif 'Телеграм-канал: Война' in viewed_channel:
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
                         F.text.contains('Телеграм-канал: Война с фейками 👀')) | (F.text.contains('РБК 👀')) | (
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
        print(all_answers_user[0])
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
    print(news_exposure)
    print(count)
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
    if len(data['all_answers_user']) != 0:
        all_answers_user = data['all_answers_user']
        markup = await keyboard_for_all_chanel(all_answers_user)
        text = await sql_safe_select('text', 'texts', {'name': 'antip_another_web_lie'})
        await message.answer(text, reply_markup=markup)
    else:
        redis = all_data().get_data_red()
        for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:*"):
            if key != "Яндекс" or key != "Википедия":
                redis.delete(key)
        if set(await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')).isdisjoint(
                ("Дмитрий Песков", "Сергей Лавров",
                 "Маргарита Симоньян", "Владимир Соловьев", "Никита Михалков")) is False:
            await antip_bad_people_lies(message, state)
        else:
            await antip_truth_game_start(message, state)


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
    text = await sql_safe_select('text', 'texts', {'name': 'antip_maybe_just_one'})
    print(lst_web_answers)
    text = text.replace('[[список неотсмотренных красных источников через запятую]]', lst_web_answers)
    text = text.replace('[[название следующего непросмотренного красного источника]]', next_channel)
    await state.update_data(not_viewed_chanel=answer_channel[0])
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Не надо')), flags=flags)
async def antip_web_exit_1(message: Message, state: FSMContext):
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:"):
        if key != "Яндекс" or key != "Википедия":
            redis.delete(key)
    if await state.get_state() == "propaganda_victim:options":
        await antip_truth_game_start(message, state)
        redis.delete(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')
        return
    if set(await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')).isdisjoint(
            ("Дмитрий Песков", "Сергей Лавров",
             "Маргарита Симоньян", "Владимир Соловьев", "Никита Михалков")) is False:
        await antip_bad_people_lies(message, state)
    else:
        await antip_truth_game_start(message, state)


@router.message(PplPropagandaFilter(),
                (F.text.contains('шаг')) | (F.text.contains('удивлён')) | (F.text.contains('шоке')) | (
                        F.text.contains('знал')) | (F.text == 'Конечно!'), flags=flags)
async def antip_bad_people_lies(message: Message, state: FSMContext):
    redis = all_data().get_data_red()
    await state.set_state(propaganda_victim.ppl_propaganda)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    text = text.replace('[[первая красная личность]]',
                        ((await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:'))[0]))

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнём 🙂"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('шаг')) | (F.text.contains('удивлён')) | (F.text.contains('шоке')) | (
        F.text.contains('знал')) | (F.text == 'Конечно!') | (F.text == 'Ну давай'), flags=flags)
async def antip_truth_game_start(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем! 🚀"))
    nmarkup.row(types.KeyboardButton(text="Пропустим игру 🙅‍♀️"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Начнем! 🚀") | (F.text == "Продолжаем, давай еще! 👉"), flags=flags)
async def antip_truth_game_start_question(message: Message, state: FSMContext):
    if message.text =='Начнем! 🚀':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true', value='Начали и НЕ закончили')
    try:
        count = (await state.get_data())['gamecount']
    except:
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
            except:
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


@router.message(YandexPropagandaFilter(), ((F.text == "Пропустим игру 🙅‍♀️") | (F.text == '🤝 Продолжим')
                                           | (F.text == 'Достаточно, двигаемся дальше  🙅‍♀️')), flags=flags)
async def antip_propaganda_here_too(message: Message, state: FSMContext):
    if message.text == 'Пропустим игру 🙅‍♀️':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='game_false_or_true', value='Пропустили')
    await state.set_state(propaganda_victim.yandex)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_propaganda_here_too'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что за источник? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Что за источник? 🤔"), state=propaganda_victim.yandex, flags=flags)
async def antip_they_lie_to_you(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Думаю, что знаю! ☝️"))
    nmarkup.add(types.KeyboardButton(text="Я не знаю  🤷‍♀️"))
    await simple_media(message, 'antip_they_lie_to_you', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('знаю')), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'antip_yandex', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.yandex, flags=flags)
async def antip_yandex_rupor(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_yandex_rupor'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я удивлен(а) 🤔"))
    nmarkup.add(types.KeyboardButton(text="Я не удивлен(а) 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Я не верю 😕"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WikiFilter(), (F.text.contains('удивлен')) | (F.text.contains('не верю')),
                state=propaganda_victim.yandex, flags=flags)
@router.message(WikiFilter(), ((F.text == "Пропустим игру 🙅‍♀️") | (F.text == '🤝 Продолжим')
                               | (F.text == 'Достаточно, двигаемся дальше  🙅‍♀️')), flags=flags)
async def antip_why_not_wiki(message: Message, state: FSMContext):
    if 'удивлен' in message.text or 'не верю' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_yandex_rupor', value=message.text)
    await state.set_state(propaganda_victim.wiki)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_why_not_wiki'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Там статьи может редактировать любой человек ✍️"))
    nmarkup.row(types.KeyboardButton(text="Википедия — проект Запада 🇺🇸"))
    nmarkup.add(types.KeyboardButton(text="Не пользуюсь / Не слышал(а) 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Случайно, вообще я доверяю Википедии 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('редактировать')) | (F.text.contains('проект'))
                 | (F.text.contains('Не слышал')) | (F.text.contains('я доверяю'))),
                state=propaganda_victim.wiki, flags=flags)
async def antip_clear_and_cool(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_clear_and_cool'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=propaganda_victim.wiki, flags=flags)
async def antip_look_at_it_yourself(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Спасибо, не знал(а) 🙂"))
    nmarkup.add(types.KeyboardButton(text="Ничего нового 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Я не верю 😕"))
    await simple_media(message, 'antip_look_at_it_yourself', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains('Спасибо')) | (F.text.contains('нового')) | (F.text.contains('не верю'))),
                state=propaganda_victim.wiki, flags=flags)
@router.message(((F.text.contains('удивлен')) | (F.text.contains('не верю'))),
                state=propaganda_victim.yandex, flags=flags)
@router.message(
    (F.text == "Пропустим игру 🙅‍♀️") | (F.text == '🤝 Продолжим') | (F.text == 'Достаточно, двигаемся дальше  🙅‍♀️'),
    flags=flags)
async def antip_ok(message: Message, state: FSMContext):
    if 'Спасибо' in message.text or 'нового' in message.text or 'не верю' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='antip_look_at_it_yourself', value=message.text)
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    if await redis_just_one_read(f'Usrs: {message.from_user.id}: INFOState:') == 'Жертва пропаганды':
        await asyncio.sleep(1)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer("У меня есть анекдот", reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        polistate = await redis_just_one_read(f'Usrs: {message.from_user.id}: Politics:')
        await asyncio.sleep(1)
        if polistate == 'Аполитичный':
            await reasons_lets_figure(message, state)
        elif polistate == 'Сторонник войны':
            await war_point_now(message, state)
        elif polistate == 'Оппозиционер':
            await reasons_king_of_info(message, state)


@router.message((F.text == 'Давай'), flags=flags)
async def antip_anecdote(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_anecdote'})
    await state.clear()
    await state.set_state(propaganda_victim.start)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="😁"))
    nmarkup.row(types.KeyboardButton(text="🙂"))
    nmarkup.row(types.KeyboardButton(text="😕"))
    nmarkup.adjust(3)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'😁', "🙂", "😕"})), flags=flags)
async def antip_emoji(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='reaction_on_anecdot', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Конечно! 🙂"))
    nmarkup.add(types.KeyboardButton(text="Ну, давай 🤨"))
    nmarkup.row(
        types.KeyboardButton(text="Подожди! А украинскую пропаганду ты показать не хочешь? Как-то однобоко. 🤔"))
    await message.answer("Можно вопрос?", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Подожди! А украинскую пропаганду ты показать не хочешь? Как-то однобоко. 🤔"), flags=flags)
async def antip_after_anecdote_log(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='can_ask_u_answ', value='Украинская пропаганда')
    text = await sql_safe_select('text', 'texts', {'name': 'antip_after_anecdote_log'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Конечно! 🙂"))
    nmarkup.row(types.KeyboardButton(text="Ну, давай 🤨"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Конечно! 🙂", "Ну, давай 🤨"})), flags=flags)
async def antip_do_you_agree(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='can_ask_u_answ', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_do_you_agree'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, полностью согласен 👌"))
    nmarkup.row(types.KeyboardButton(text="Да, но почему тогда люди ей верят? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Да, существует, как и во всех странах 🇺🇸"))
    nmarkup.row(types.KeyboardButton(text="Возможно / частично 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен(а) 🙅‍♂️"))
    nmarkup.adjust(2, 1, 2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('почему')), flags=flags)
async def antip_why_they_belive(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_1', value=message.text)
    await simple_media(message, 'antip_why_they_belive', antip_why_kb())


@router.message((F.text.contains('Возможно') | (F.text.contains('полностью')) | (F.text.contains('Скорее')) | (
        F.text.contains('Допускаю'))), flags=flags)
async def antip_to_the_main(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_1', value=message.text)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_2', value=message.text)
    await simple_media(message, 'antip_to_the_main', antip_why_kb())


@router.message((F.text.contains('странах')) | (F.text.contains('🇺🇸')), flags=flags)
async def antip_to_the_main(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_1', value=message.text)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_2', value=message.text)
    await simple_media(message, 'antip_prop_difference', antip_why_kb())


@router.message((F.text == "Нет, не согласен(а) 🙅‍♂️"), flags=flags)
async def antip_love_propaganda(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_1', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее согласен(а) 👌"))
    nmarkup.row(types.KeyboardButton(text="Да, как и во многих других странах 🇺🇸"))
    nmarkup.row(types.KeyboardButton(text="Нет, нам хотят донести правду 😌"))
    await simple_media(message, 'antip_love_propaganda', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Нет, нам хотят донести правду 😌')
async def antip_big_love_propaganda(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prop_machine_2', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_big_love_propaganda'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(
        text="Я передумал(а). Допускаю, что ТВ и гос. СМИ не ставят целью донести до людей правду 😔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Откуда ты знаешь')), flags=flags)
async def antip_reputation_matters(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_reputation_matters'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 🇷🇺🇺🇦'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


# По хорошему, это уже начало войны
# Я НЕ ЗНАЮ КАК ЭТО НОРМАЛЬНО ПОВЕСИТЬ
@router.message(PoliticsFilter(title='Сторонник войны'),
                ((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
                        F.text.contains('Продолжим 🇷🇺🇺🇦')), flags=flags)
async def war_point_now(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='map_antiprop', value=message.text)
    await mongo_update_stat(message.from_user.id, 'antiprop')
    await state.set_state(true_resons_hand.TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war_point_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(PoliticsFilter(title='Аполитичный'),
                ((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
                        F.text.contains("Продолжим 🇷🇺🇺🇦")), flags=flags)
async def reasons_lets_figure(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='map_antiprop', value=message.text)
    await state.set_state(true_resons_hand.TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lets_figure'})
    await mongo_update_stat(message.from_user.id, 'antiprop')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай попробуем 👌"))
    nmarkup.row(types.KeyboardButton(text="Я не интересуюсь политикой 😐"))
    nmarkup.row(types.KeyboardButton(text="Незачем, ведь эти цели - бессмысленны 🤬"))
    nmarkup.adjust(2, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
        F.text.contains('Продолжим 🇷🇺🇺🇦')), flags=flags)
async def reasons_king_of_info(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='map_antiprop', value=message.text)
    await state.set_state(true_resons_hand.TruereasonsState.main)
    await mongo_update_stat(message.from_user.id, 'antiprop')
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_king_of_info'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 👌"))
    nmarkup.row(
        types.KeyboardButton(text="Подожди. Я так не говорил(а). С чего ты взял, что это ненастоящие цели? 🤷‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
