import asyncio
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bata import all_data
from data_base.DBuse import poll_write, sql_safe_select, mongo_add, mongo_select, redis_just_one_write, mongo_user_info
from middleware import CounterMiddleware
from resources.all_polls import web_prop, welc_message_one
from states import welcome_states
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_stat, mongo_update_stat

router = Router()
router.message.middleware(CounterMiddleware())


@router.message(commands=['start', 'help'], state="*")
async def commands_start(message: types.Message, state: FSMContext):  # Первое сообщение
    user_id = message.from_user.id
    await mongo_stat(user_id)
    await mongo_user_info(user_id, message.from_user.username)
    await state.clear()
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}:*"):
        redis.delete(key)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начнем 🇷🇺🇺🇦"))
    markup.add(types.KeyboardButton(text="А с чего мне тебе верить? 🤔"))
    text = await sql_safe_select("text", "texts", {"name": "start_hello"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_1)


@router.message(welcome_states.start_dialog.dialogue_1, text_contains='верить', content_types=types.ContentType.TEXT,
                text_ignore_case=True)  # А с чего мне тебе верить?
async def message_1(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Хорошо"))
    text = await sql_safe_select("text", "texts", {"name": "start_why_belive"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_2)


@router.message(welcome_states.start_dialog.dialogue_2, text_contains='Хорошо', content_types=types.ContentType.TEXT,
                text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_1, text_contains='Начнем 🇷🇺🇺🇦',
                content_types=types.ContentType.TEXT,
                text_ignore_case=True)
# @router.message(welcome_states.start_dialog.dialogue_3) запомнить на ты или на вы в базу
async def message_2(message: types.Message, state: FSMContext):
    # запись значения в базу
    markup = ReplyKeyboardBuilder()

    markup.row(types.KeyboardButton(text="1️⃣ Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="2️⃣ Война / Вторжение в Украину"))
    markup.row(types.KeyboardButton(text="Сейчас даже такое мнение "
                                         "выражать незаконно. Вдруг вы из ФСБ? 🤐"))
    text = await sql_safe_select("text", "texts", {"name": "start_what_about_you"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_4)


@router.message(welcome_states.start_dialog.dialogue_4,
                ((F.text == '1️⃣ Специальная военная операция (СВО)') | (F.text == '2️⃣ Война / Вторжение в Украину')))
async def message_3(message: types.Message, state: FSMContext):  # Начало опроса
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:', message.text)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай 👌"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать? ⏱"))
    await state.update_data(answer_1=message.text)
    text = await sql_safe_select("text", "texts", {"name": "start_lets_start"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('выражать', 'незаконно'),
                content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_4(message: types.Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="1️⃣ Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="2️⃣ Война / Вторжение в Украину"))
    text = await sql_safe_select("text", "texts", {"name": "start_afraid"})
    # if на ты
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('долго', 'допрашивать'),
                content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_5(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, задавай свои вопросы 👌"))
    text = await sql_safe_select("text", "texts", {"name": "start_only_five"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Хорошо', 'свои', 'вопросы'),
                content_types=types.ContentType.TEXT, text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_5, text_contains='Задавай', content_types=types.ContentType.TEXT,
                text_ignore_case=True)  # Задаю первый вопрос и ставлю состояние
async def message_6(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Скорее да 🙂"), types.KeyboardButton(text="Скорее нет 🙅‍♂"))
    markup.row(types.KeyboardButton(text="Начал(а) интересоваться после 24 февраля"))
    text = await sql_safe_select("text", "texts", {"name": "start_do_you_love_politics"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(welcome_states.start_dialog.dialogue_6)


@router.message(welcome_states.start_dialog.dialogue_6)
async def message_6to7(message: types.Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи варианты ✍"))
    text = await sql_safe_select("text", "texts", {"name": "start_russia_goal"})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    if text == 'Начал(а) интересоваться после 24 февраля' or text == "Скорее да 🙂" or text == "Скорее нет 🙅‍♂":
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: interest_in_politics:',
                         message.text[:-2].strip())
    await state.set_state(welcome_states.start_dialog.dialogue_extrafix)


@router.message(text_contains='Покажи варианты', state = welcome_states.start_dialog.dialogue_extrafix)  # Сохраняю 1 вопрос
async def message_7(message: types.Message, state: FSMContext):
    # Сохранить 1 вопрос в базу
    text = message.text
    options = welc_message_one
    # Сохранение 1 вопроса в дату   
    await state.update_data(option_1=options)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Продолжай"))
    await message.answer_poll(
        question="Выберите все цели, с которыми согласны или частично согласны. Затем нажмите «Проголосовать»",
        options=options, is_anonymous=False, allows_multiple_answers=True,
        reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_7)


@router.message(welcome_states.start_dialog.dialogue_7, (F.text == 'Продолжай'))
async def poll_filler(message: types.Message, bot: Bot):
    msg = await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"',
                               reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
    await asyncio.sleep(10)
    await bot.delete_message(message.from_user.id, msg.message_id)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_7)  # Сохраняю 2 вопрос
async def poll_answer_handler(poll_answer: types.PollAnswer, state: FSMContext):
    # сохранение 2 вопроса
    options = await state.get_data()
    lst_options = options["option_1"]
    lst_answers = poll_answer.option_ids
    for index in lst_answers:
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:', lst_options[index])
    await state.update_data(answer_2=lst_answers)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, полностью доверяю ✅"),
               types.KeyboardButton(text="Нет, не верю ни слову ⛔"))
    markup.row(types.KeyboardButton(text="Скорее да 👍"), types.KeyboardButton(text="Скорее нет 👎"))

    text = await sql_safe_select("text", "texts", {"name": "start_belive_TV"})
    await Bot(all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text,
                                                 reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_8)


@router.message(state=welcome_states.start_dialog.dialogue_8)  # Сохраняю 3 вопрос
async def message_8(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Да, полностью доверяю ✅" or text == "Скорее да 👍" or \
            text == "Скорее нет 👎" or text == "Нет, не верю ни слову ⛔":
        # сохранение 3 вопроса
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: tv:', message.text)
        await state.update_data(option_3=web_prop)
        await state.update_data(answer_3=message.text)
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Покажи варианты ✍️"))
        mess = await sql_safe_select("text", "texts", {"name": "start_internet_belive"})
        await message.answer(text=mess, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
        await state.set_state(welcome_states.start_dialog.button_next)
    else:
        await message.answer("Неправильный ответ, вы можете выбрать вариант ответа на клавиатуре", disable_web_page_preview=True)


@router.message((F.text.contains("Покажи варианты ✍️")), state=welcome_states.start_dialog.button_next)
async def button(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай"))
    text = await sql_safe_select("text", "texts", {"name": "start_internet_belive"})
    await message.answer_poll(text, web_prop, is_anonymous=False, allows_multiple_answers=True,
                              reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_9)


@router.message(welcome_states.start_dialog.dialogue_9, (F.text == 'Продолжай'))
async def poll_filler(message: types.Message, bot: Bot):
    msg = await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"',
                               reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
    await asyncio.sleep(10)
    await bot.delete_message(message.from_user.id, msg.message_id)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_9)  # Сохраняю 4 вопрос
async def poll_answer_handler_tho(poll_answer: types.PollAnswer, state=FSMContext):
    options = ["Владимир Путин", "Дмитрий Песков", "Сергей Лавров", "Владимир Соловьев","Никита Михалков", "Юрий Подоляка",
               "Никому из них..."]
    # сохранение 4 вопроса
    option = await state.get_data()
    lst_options = option["option_3"]
    lst_answers = poll_answer.option_ids
    lst = []
    for index in lst_answers:
        lst.append(lst_options[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: ethernet_id:', int(index))
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: ethernet:', lst_options[index])
    await state.update_data(answer_4=poll_answer.option_ids)
    await state.update_data(option_4=options)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай"))
    text = await sql_safe_select("text", "texts", {"name": "start_people_belive"})
    await Bot(all_data().bot_token).send_poll(poll_answer.user.id, text, options, is_anonymous=False,
                                              allows_multiple_answers=True,
                                              reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_10)


@router.message(welcome_states.start_dialog.dialogue_10, (F.text == 'Продолжай'))
async def poll_filler(message: types.Message, bot: Bot):
    msg = await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"',
                               reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
    await asyncio.sleep(10)
    await bot.delete_message(message.from_user.id, msg.message_id)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_10)  # Сохраняю 5 вопрос
async def poll_answer_handler_three(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Поехали!"))
    options = await state.get_data()
    lst_options = options["option_4"]
    lst_answers = poll_answer.option_ids
    lst = []
    for index in lst_answers:
        lst.append(lst_options[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust:', lst_options[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:', lst_options[index])
    await state.update_data(answer_5=poll_answer.option_ids)
    text = await sql_safe_select("text", "texts", {"name": "start_thank_you"})
    await bot.send_message(poll_answer.user.id, text)
    data = await state.get_data()
    await mongo_update_stat(poll_answer.user.id, 'start')
    if await mongo_select(poll_answer.user.id):  # можно поставить счетчик повторных обращений
        print("Пользователь уже есть в базе")
    else:
        await mongo_add(poll_answer.user.id,
                        [data['answer_1'], data['answer_2'], data['answer_3'], data['answer_4'], data['answer_5']])
    if data["answer_3"] != "Нет, не верю ни слову ⛔" or ({0, 1, 3, 4, 5}.isdisjoint(
            set(data["answer_4"])) is False and {1, 2, 3, 4, 5}.isdisjoint(
        set(data["answer_5"])) is False):  # Жертва пропаганды?
        # Вот это все бы не в списки совать, потом займусь
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', 'Жертва пропаганды')
        print('Жертва пропаганды')
    elif {2}.isdisjoint(set(data["answer_4"])) is False:  # Король информации?
        if len(data["answer_2"]) <= 2 and {0, 1, 2, 3, 5, 7, 8} not in set(data["answer_2"]):
            await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', 'Король информации')
            print('Король информации')
        else:
            await redis_just_one_write(f'Usrs: {poll_answer.user.id}: INFOState:', "Фома неверующий")
            print('Фома неерующий')

    await state.clear()
    await state.set_state(propaganda_victim.start)

    # Вот это все бы не в списки совать
    if {0, 1, 2, 3, 5, 7, 8}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Сторонник войны')
    elif {4, 6}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Оппозиционер')
    elif {9}.isdisjoint(set(data["answer_2"])) is False:
        await redis_just_one_write(f'Usrs: {poll_answer.user.id}: Politics:', 'Аполитичный')

    await state.set_state(propaganda_victim.start)
    if data["answer_3"] == "Нет, не верю ни слову ⛔":
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Пропустим этот шаг 👉"))
        markup.row(types.KeyboardButton(text="Покажи ложь на ТВ -- мне интересно посмотреть! 📺"))
        text = await sql_safe_select("text", "texts", {"name": "antip_all_no_TV"})
        await bot.send_message(poll_answer.user.id, text, reply_markup=markup.as_markup(resize_keyboard=True),
                               disable_web_page_preview=True)
    elif data["answer_3"] == "Да, полностью доверяю ✅":
        text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Продолжай 📺"))
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
                               disable_web_page_preview=True)
