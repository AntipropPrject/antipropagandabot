import asyncio
import datetime
from datetime import time

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.filters.command import CommandStart, CommandObject
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from data_base.DBuse import poll_write, sql_safe_select, mongo_add, mongo_select, redis_just_one_write, \
    mongo_user_info, redis_just_one_read, advertising_value
from day_func import day_count
from resources.all_polls import web_prop, welc_message_one, people_prop
from states import welcome_states
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_stat, mongo_update_stat, mongo_stat_new, mongo_update_stat_new

flags = {"throttling_key": "True"}
router = Router()


@router.message(CommandStart(command_magic=F.args), flags=flags)
async def adv_company(message: types.Message, state: FSMContext, command: CommandObject):
    await advertising_value(command.args)
    await commands_start(message, state)


@router.message(commands=['start', 'help', 'restart'], state='*', flags=flags)
async def commands_start(message: types.Message, state: FSMContext):  # Первое сообщение
    asyncio.create_task(start_base(message))
    await state.clear()
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Начнем 🇷🇺🇺🇦"))
    markup.row(types.KeyboardButton(text="А с чего мне тебе верить? 🤔"))
    text = await sql_safe_select("text", "texts", {"name": "start_hello"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_1)
    # else:
    #    await message.answer("Извините, этого бота можно проходить только один раз")

async def start_base(message):
    user_id = message.from_user.id  # if old is None:
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}:*"):
        redis.delete(key)
    await mongo_stat(user_id)
    await mongo_stat_new(user_id)
    await mongo_user_info(user_id, message.from_user.username)


@router.message(welcome_states.start_dialog.dialogue_1, text_contains='верить', content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)  # А с чего мне тебе верить?
async def message_1(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='first_button', value='А с чего мне тебе верить?')
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Хорошо 👌"))
    text = await sql_safe_select("text", "texts", {"name": "start_why_belive"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_2)


@router.message(welcome_states.start_dialog.dialogue_2, text_contains='Хорошо', content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
@router.message(welcome_states.start_dialog.dialogue_1, text_contains='Начнем 🇷🇺🇺🇦',
                content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
# @router.message(welcome_states.start_dialog.dialogue_3) запомнить на ты или на вы в базу
async def message_2(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='first_button', value='Начнем')
    # запись значения в базу
    markup = ReplyKeyboardBuilder()

    markup.row(types.KeyboardButton(text="1️⃣ Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="2️⃣ Война"))
    markup.row(types.KeyboardButton(text="Сейчас даже такое мнение "
                                         "выражать незаконно. Вдруг вы из ФСБ? 🤐"))
    text = await sql_safe_select("text", "texts", {"name": "start_what_about_you"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_4)


@router.message(welcome_states.start_dialog.dialogue_4, (F.text == '1️⃣ Специальная военная операция (СВО)'),
                flags=flags)
async def message_3(message: types.Message, state: FSMContext):  # Начало опроса
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:', message.text)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='war_or_not', value=message.text)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай 👌"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать? ⏱"))
    markup.row(types.KeyboardButton(text="Стоп! Правильно «в Украине»! ☝️"))
    await state.update_data(answer_1=message.text)
    text = await sql_safe_select("text", "texts", {"name": "start_lets_start"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_4, (F.text == "2️⃣ Война"), flags=flags)
async def start_lets_start_2(message: types.Message, state: FSMContext):  # Начало опроса
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:', message.text)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='war_or_not', value=message.text)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай 👌"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать? ⏱"))
    markup.row(types.KeyboardButton(text="Стоп! Правильно «в Украине»! ☝️"))
    await state.update_data(answer_1=message.text)
    text = await sql_safe_select("text", "texts", {"name": "start_lets_start_2"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_5, (F.text == "Стоп! Правильно «в Украине»! ☝️"), flags=flags)
async def start_lets_start_2(message: types.Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='on_ucraine_or_not', value='Да')
    text = await sql_safe_select("text", "texts", {"name": "start_is_it_correct"})
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай 👌"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать? ⏱"))
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('выражать', 'незаконно'),
                content_types=types.ContentType.TEXT, text_ignore_case=True, flags=flags)
async def message_4(message: types.Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="1️⃣ Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="2️⃣ Война"))
    text = await sql_safe_select("text", "texts", {"name": "start_afraid"})
    # if на ты
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('долго', 'допрашивать'),
                content_types=types.ContentType.TEXT, text_ignore_case=True, flags=flags)
async def message_5(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, задавай свои вопросы 👌"))
    text = await sql_safe_select("text", "texts", {"name": "start_only_five"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message((F.text == 'Продолжить'), state=(welcome_states.start_dialog.dialogue_10,
                                                 welcome_states.start_dialog.dialogue_9,
                                                 welcome_states.start_dialog.dialogue_7), flags=flags)
async def poll_filler(message: types.Message):
    await message.answer('Чтобы продолжить — отметьте варианты выше и нажмите «ГОЛОСОВАТЬ» или «VOTE»',
                         reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Хорошо', 'свои', 'вопросы'),
                content_types=types.ContentType.TEXT, text_ignore_case=True, flags=flags)
@router.message(welcome_states.start_dialog.dialogue_5, text_contains='Задавай', content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)  # Задаю первый вопрос и ставлю состояние
async def message_6(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='on_ucraine_or_not', value='Нет')
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Скорее да  🙂"), types.KeyboardButton(text="Скорее нет  🙅‍♂"))
    markup.row(types.KeyboardButton(text="Начал(а) интересоваться после 24 февраля 🇷🇺🇺🇦"))
    text = await sql_safe_select("text", "texts", {"name": "start_do_you_love_politics"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_6)



@router.message(welcome_states.start_dialog.dialogue_6, flags=flags)
async def message_6to7(message: types.Message, state: FSMContext):
    if message.text == "Начал(а) интересоваться после 24 февраля 🇷🇺🇺🇦" or message.text == "Скорее да  🙂":
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Покажи варианты ✍"))
        text = await sql_safe_select("text", "texts", {"name": "start_russia_goal"})
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: interest_in_politics:',
                         message.text[:-3].strip())
    elif message.text == 'Скорее нет  🙅‍♂':
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, продолжим 👌"))
        text = await sql_safe_select("text", "texts", {"name": "not_in_vain"})
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_extrafix)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='interest_politics', value=message.text)


@router.message((F.text.contains('Хорошо, продолжим')) | (F.text.contains('Покажи варианты')), state=welcome_states.start_dialog.dialogue_extrafix, flags=flags)  # Сохраняю 1 вопрос
async def message_7(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Продолжить"))
    await message.answer_poll(
        question="Выберите все цели, с которыми согласны или частично согласны. Затем нажмите «Проголосовать»",
        options=welc_message_one, is_anonymous=False, allows_multiple_answers=True,
        reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_7)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_7, flags=flags)  # Сохраняю 2 вопрос
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    lst_answers = poll_answer.option_ids
    lst_str = []
    for index in lst_answers:
        lst_str.append(welc_message_one[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:', welc_message_one[index])
    await state.update_data(ans_lst_2=lst_str)
    await state.update_data(answer_2=lst_answers)

    if 'Я не знаю' == lst_str[0]:  # idnt know
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='war_aims_gen', value='Только "Я не знаю"')
    elif {0, 1, 2, 3, 5, 8}.isdisjoint(set(lst_answers)) is False:  # red
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='war_aims_gen', value='Хотя бы один красный')
    elif {4, 6}.isdisjoint(set(lst_answers)) is False:  # green
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='war_aims_gen', value='Есть зелёные и нет красных')

    await mongo_update_stat_new(tg_id=poll_answer.user.id,column='war_aims_ex', value=lst_str)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, полностью доверяю ✅"),
               types.KeyboardButton(text="Нет, не верю ни слову ⛔"))
    markup.row(types.KeyboardButton(text="Скорее да 👍"), types.KeyboardButton(text="Скорее нет 👎"))
    markup.row(types.KeyboardButton(text="Не знаю, потому что не смотрю ни новости по ТВ, ни их интернет-версию 🤷‍♂"))
    text = await sql_safe_select("text", "texts", {"name": "start_belive_TV"})
    await state.set_state(welcome_states.start_dialog.dialogue_8)
    await bot.send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(state=welcome_states.start_dialog.dialogue_8, flags=flags)  # Сохраняю 3 вопрос
async def message_8(message: types.Message, state: FSMContext):
    m_text = message.text
    if m_text == "Да, полностью доверяю ✅" or m_text == "Скорее да 👍" or \
            m_text == "Скорее нет 👎" or m_text == "Нет, не верю ни слову ⛔" or \
            m_text == "Не знаю, потому что не смотрю ни новости по ТВ, ни их интернет-версию 🤷‍♂":
        await mongo_update_stat_new(tg_id=message.from_user.id, column='tv_love_gen', value=m_text)
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: tv:', m_text)
        await state.update_data(answer_3=m_text)
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Покажи варианты ✍️"))
        text = await sql_safe_select("text", "texts", {"name": "start_internet_belive"})
        await message.answer(text=text, reply_markup=markup.as_markup(resize_keyboard=True),
                             disable_web_page_preview=True)
        await state.set_state(welcome_states.start_dialog.button_next)
    else:
        await message.answer("Неправильный ответ, вы можете выбрать вариант ответа на клавиатуре",
                             disable_web_page_preview=True)


@router.message((F.text.contains("Покажи варианты ✍️")), state=welcome_states.start_dialog.button_next, flags=flags)
async def button(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжить"))
    text = await sql_safe_select("text", "texts", {"name": "start_internet_poll"})
    await message.answer_poll(text, web_prop, is_anonymous=False, allows_multiple_answers=True,
                              reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_9)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_9, flags=flags)  # Сохраняю 4 вопрос
async def poll_answer_handler_tho(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    lst_answers = poll_answer.option_ids
    lst_str = []
    for index in lst_answers:
        lst_str.append(web_prop[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: ethernet:', web_prop[index])

    if 'Никому из них...' in lst_str[0]:  # idnt know
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='web_prop_gen', value='Только "Я не знаю"')
    elif {2, 3, 4, 5, 7}.isdisjoint(set(lst_answers)) is False:  # red
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='web_prop_gen', value='Хотя бы один красный')
    elif {1, 6}.isdisjoint(set(lst_answers)) is False:  # green
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='web_prop_gen', value='Есть зелёные и нет красных')
    if 'Википедия' not in lst_str:
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='why_not_wiki', value=lst_str)

    await state.update_data(answer_4=poll_answer.option_ids)
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='web_prop_ex', value=lst_str)
    await state.update_data(ans_lst_4=lst_str)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжить"))
    text = await sql_safe_select("text", "texts", {"name": "start_people_belive"})
    await state.set_state(welcome_states.start_dialog.dialogue_10)
    await bot.send_message(poll_answer.user.id, text)
    await bot.send_poll(poll_answer.user.id, 'Отметьте всех людей,'
                                             ' которым доверяете или частично доверяете.'
                                             ' Затем нажмите «Проголосовать»',
                        people_prop, is_anonymous=False,
                        allows_multiple_answers=True,
                        reply_markup=markup.as_markup(resize_keyboard=True))


@router.poll_answer(state=welcome_states.start_dialog.dialogue_10)  # Сохраняю 5 вопрос
async def poll_answer_handler_three(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    data = await state.get_data()
    lst_answers = poll_answer.option_ids
    lst_str = []
    for index in lst_answers:
        lst_str.append(people_prop[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust:', people_prop[index])
        if people_prop[index] != "Владимир Путин" and people_prop[index] != "Никому из них...":
            await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:',
                             people_prop[index])
            await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons_newpoll:',
                             people_prop[index])
        elif people_prop[index] == "Владимир Путин":
            await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Start_answers: LovePutin', 'True')

    if {1, 2, 3, 4, 5}.isdisjoint(set(lst_answers)) is False:  # red
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='prop_gen', value='Хотя бы один красный')
    elif {0}.isdisjoint(set(lst_answers)) is False:
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='prop_gen', value='Красных нет, но есть Путин')
    else:
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='prop_gen', value='Нет ни красных, ни Путина')

    await mongo_update_stat_new(tg_id=poll_answer.user.id,column='prop_ex', value=lst_str)
    text = await sql_safe_select("text", "texts", {"name": "start_thank_you"})
    await bot.send_message(poll_answer.user.id, text)
    await mongo_update_stat(poll_answer.user.id, 'start')
    if await mongo_select(poll_answer.user.id):  # можно поставить счетчик повторных обращений
        print("Пользователь уже есть в базе")
    else:
        await mongo_add(poll_answer.user.id,
                        [data['answer_1'], data['ans_lst_2'], data['answer_3'], data['ans_lst_4'], lst_str])
    answer_3, answer_4, answer_5 = set(data["answer_3"]), set(data["answer_4"]), set(poll_answer.option_ids)
    if (data["answer_3"] != "Нет, не верю ни слову ⛔"
        and data["answer_3"] != "Не знаю, потому что не смотрю ни новости по ТВ, ни их интернет-версию 🤷‍♂") \
            or ({0, 2, 3, 4, 5, 7}.isdisjoint(answer_4) is False
                or {1, 2, 3, 4, 5}.isdisjoint(answer_5) is False
                or 'Да, полностью доверяю ✅' in answer_3) \
                or 'Скорее да 👍' in answer_3 \
                or 'Скорее нет 👎' in answer_3:

        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', 'Жертва пропаганды')
        await mongo_update_stat(poll_answer.user.id, column='faith', value='victim', options='$set')

        if {0}.isdisjoint(answer_4) is False:
            await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Start_answers: Yandex', 1)
        if {1}.isdisjoint(answer_4):
            await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Start_answers: NotWiki', 1)
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='faith', value='Жертва пропаганды')
        print('Жертва пропаганды')

    elif {1, 6}.isdisjoint(answer_4) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', 'Король информации')
        await mongo_update_stat(poll_answer.user.id, column='faith', value='kinginfo', options='$set')
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='faith', value='Король информации')
        print('Король информации')

    elif {1, 6}.isdisjoint(answer_4) is True:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', "Фома неверующий")
        await mongo_update_stat(poll_answer.user.id, column='faith', value='foma', options='$set')
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='faith', value='Фома неверующий')
        print('Фома неерующий')

    await state.clear()
    await state.set_state(propaganda_victim.start)

    if {0, 1, 2, 3, 5, 7, 8}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Сторонник войны')
        await mongo_update_stat(poll_answer.user.id, column='political_view', value='warsupp', options='$set')
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='polit_status', value='Сторонник войны')
    elif {4, 6}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Оппозиционер')
        await mongo_update_stat(poll_answer.user.id, column='political_view', value='oppos', options='$set')
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='polit_status', value='Оппозиционер')
    elif {9}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Аполитичный')
        await mongo_update_stat(poll_answer.user.id, column='political_view', value='apolitical', options='$set')
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='polit_status', value='Аполитичный')
    if await redis_just_one_read(f'Usrs: {poll_answer.user.id}: INFOState:') == 'Жертва пропаганды':
        text = await sql_safe_select("text", "texts", {"name": "antip_only_facts"})
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', 'Жертва пропаганды')

        nmarkap = ReplyKeyboardBuilder()
        nmarkap.row(types.KeyboardButton(text="Мне интересно 👌"))
        nmarkap.add(types.KeyboardButton(text="Ну давай... 🤨"))
        nmarkap.row(types.KeyboardButton(text="Что такое пропаганда? 🤔"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkap.as_markup(resize_keyboard=True))
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Пропустим этот шаг 👉"))
        markup.row(types.KeyboardButton(text="Покажи ложь на ТВ — мне интересно посмотреть! 📺"))
        text = await sql_safe_select("text", "texts", {"name": "antip_all_no_TV"})
        await bot.send_message(poll_answer.user.id, text, reply_markup=markup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)


"""    if data["answer_3"] == "Нет, не верю ни слову ⛔":
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Пропустим этот шаг 👉"))
        markup.row(types.KeyboardButton(text="Покажи ложь на ТВ — мне интересно посмотреть! 📺"))
        text = await sql_safe_select("text", "texts", {"name": "antip_all_no_TV"})
        await bot.send_message(poll_answer.user.id, text, reply_markup=markup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)
    elif data["answer_3"] == "Да, полностью доверяю ✅":
        text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)
    elif data["answer_3"] == "Скорее нет 👎":
        text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_no_TV'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
        nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)
    elif data["answer_3"] == "Скорее да 👍":
        text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_yes_TV'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
        nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)"""
