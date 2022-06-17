from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from data_base.DBuse import poll_get, poll_write, sql_safe_select, mongo_add, mongo_select, mongo_update
from bata import all_data
from states import welcome_states
from states.antiprop_states import propaganda_victim
from resources.all_polls import web_prop
from stats.stat import mongo_stat, mongo_update


router = Router()


@router.message(commands=['start', 'help'], state="*")
async def commands_start(message: types.Message, state: FSMContext):  # Первое сообщение
    await mongo_stat(message.from_user.id)
    await state.clear()
    all_data().get_data_red().flushdb()
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начнем!"))
    markup.add(types.KeyboardButton(text="А с чего мне тебе верить?"))
    text = await sql_safe_select("text", "texts", {"name": "start_hello"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_1)


@router.message(welcome_states.start_dialog.dialogue_1, text_contains=('верить'), content_types=types.ContentType.TEXT, text_ignore_case=True)  # А с чего мне тебе верить?
async def message_1(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Хорошо"))
    text = await sql_safe_select("text", "texts", {"name": "start_why_belive"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_2)


#@router.message(welcome_states.start_dialog.dialogue_2, text_contains=('Хорошо'), content_types=types.ContentType.TEXT, text_ignore_case=True)
#@router.message(welcome_states.start_dialog.dialogue_1, text_contains=('Начнем'), content_types=types.ContentType.TEXT, text_ignore_case=True)  # Общаемся на ты или на вы?
#async def message_1(message: types.Message, state: FSMContext):
#    markup = ReplyKeyboardBuilder()
#    markup.add(types.KeyboardButton(text="На ты 👋"))
#    markup.add(types.KeyboardButton(text="На вы 🤝"))
#    await message.answer("Как нам будет комфортнее общаться: на Ты или на Вы?", reply_markup=markup.as_markup(resize_keyboard=True))
#    await state.set_state(welcome_states.start_dialog.dialogue_3)


@router.message(welcome_states.start_dialog.dialogue_2, text_contains=('Хорошо'), content_types=types.ContentType.TEXT, text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_1, text_contains=('Начнем'), content_types=types.ContentType.TEXT, text_ignore_case=True)
#@router.message(welcome_states.start_dialog.dialogue_3)  # запомнить на ты или на вы в базу
async def message_2(message: types.Message, state: FSMContext):
    # запись значения в базу
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Сейчас даже такое мнение "
                                 "выражать незаконно. Вдруг вы из ФСБ?"))
    markup.row(types.KeyboardButton(text="Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="Война / Вторжение в Украину"))
    text = await sql_safe_select("text", "texts", {"name": "start_what_about_you"})

    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    # if на ты

    await state.set_state(welcome_states.start_dialog.dialogue_4)


@router.message(welcome_states.start_dialog.dialogue_4, ((F.text == 'Специальная военная операция (СВО)') | (F.text == 'Война / Вторжение в Украину')))
async def message_3(message: types.Message, state: FSMContext):  # Начало опроса
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Is_it_war:', message.text)
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать?"))
    await state.update_data(answer_1=message.text)
    text = await sql_safe_select("text", "texts", {"name": "start_lets_start"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('выражать', 'незаконно'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_4(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Специальная военная операция (СВО)"))
    markup.row(types.KeyboardButton(text="Война / Вторжение в Украину"))
    text = await sql_safe_select("text", "texts", {"name": "start_afraid"})
    # if на ты
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('долго', 'допрашивать'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_5(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, задавай свои вопросы"))
    text = await sql_safe_select("text", "texts", {"name": "start_only_five"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_5)

#((F.text @ ('Открой мне глаза 👀', "Ну удиви меня 🤔"))
#@router.message(((F.text == 'Договорились') | (F.text == 'Хорошо')))
@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Хорошо', 'свои', 'вопросы'), content_types=types.ContentType.TEXT, text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Задавай'), content_types=types.ContentType.TEXT, text_ignore_case=True)  # Задаю первый вопрос и ставлю состояние
async def message_6(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начал(а) интересоваться после 24 февраля"))
    markup.row(types.KeyboardButton(text="Скорее да"), types.KeyboardButton(text="Скорее нет"))
    text = await sql_safe_select("text", "texts", {"name": "start_do_you_love_politics"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_6)


@router.message(welcome_states.start_dialog.dialogue_6)  # Сохраняю 1 вопрос
async def message_7(message: types.Message, state: FSMContext):
    # Сохранить 1 вопрос в базу
    text = message.text
    if text == 'Начал(а) интересоваться после 24 февраля' or text == "Скорее да" or text == "Скорее нет":
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: interest_in_politics:', message.text)
        options = ["Защитить русских в Донбассе",  # Вопросы опроса
                   "Предотвратить вторжение на территорию"
                   " России или ЛНР/ДНР", "Денацификация / Уничтожить нацистов", "Демилитаризация / Снижение военной мощи",
                   "Сменить власть в Украине", "Уничтожить биолаборатории / Предотвратить создание ядерного оружия",
                   "Повысить рейтинг доверия Владимира Путина", "Захватить территории Донбасса и юга Украины",
                   "Предотвратить размещение военных баз НАТО в Украине", "Я не знаю..."
                   ]
        # Сохранение 1 вопроса в дату
        await state.update_data(option_1=options)
        text = await sql_safe_select("text", "texts", {"name": "start_russia_goal"})
        await message.answer_poll(text, options, is_anonymous=False, allows_multiple_answers=True, reply_markup=ReplyKeyboardRemove())
        await state.set_state(welcome_states.start_dialog.dialogue_7)
    else:
        await message.answer("Неправильный ответ, вы можете выбрать вариант ответа на клавиатуре")


@router.poll_answer(state=welcome_states.start_dialog.dialogue_7)  # Сохраняю 2 вопрос
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    #сохранение 2 вопроса
    options = await state.get_data()
    lst_options = options["option_1"]
    lst_answers = poll_answer.option_ids
    lst = []
    for index in lst_answers:
        lst.append(lst_options[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:', lst_options[index])
    await state.update_data(answer_2=lst_answers)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, полностью доверяю"))
    markup.row(types.KeyboardButton(text="Скорее да"), types.KeyboardButton(text="Скорее нет"))
    markup.row(types.KeyboardButton(text="Нет, не верю ни слову"))
    text = await sql_safe_select("text", "texts", {"name": "start_belive_TV"})
    await Bot(all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup(resize_keyboard=True))
    await state.set_state(welcome_states.start_dialog.dialogue_8)


@router.message(state=welcome_states.start_dialog.dialogue_8)  # Сохраняю 3 вопрос
async def message_8(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Да, полностью доверяю" or text == "Скорее да" or text =="Скорее нет" or text == "Нет, не верю ни слову":

        # сохранение 3 вопроса

        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: tv:', message.text)
        await state.update_data(option_3=web_prop)
        await state.update_data(answer_3=message.text)
        text=await sql_safe_select("text", "texts", {"name": "start_internet_belive"})
        await message.answer_poll(text, web_prop, is_anonymous=False, allows_multiple_answers=True, reply_markup=ReplyKeyboardRemove())
        await state.set_state(welcome_states.start_dialog.dialogue_9)
    else:
        await message.answer("Неправильный ответ, вы можете выбрать вариант ответа на клавиатуре")


@router.poll_answer(state = welcome_states.start_dialog.dialogue_9)  # Сохраняю 4 вопрос
async def poll_answer_handler_tho(poll_answer: types.PollAnswer, state=FSMContext):
    options = ["Владимир Путин", "Дмитрий Песков", "Рамзан Кадыров",
               "Сергей Лавров", "Юрий Подоляка", "Владимир Соловьев",
               "Ольга Скабеева", "Никому из них..."
               ]
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
    answer_id_str = await poll_get(f'Usrs: {poll_answer.user.id}: Start_answers: ethernet_id:')
    text = await sql_safe_select("text", "texts", {"name": "start_people_belive"})
    await Bot(all_data().bot_token).send_poll(poll_answer.user.id, text, options, is_anonymous=False, allows_multiple_answers=True)
    await state.set_state(welcome_states.start_dialog.dialogue_10)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_10)  # Сохраняю 5 вопрос
async def poll_answer_handler_three(poll_answer: types.PollAnswer, state=FSMContext):
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
    await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=markup.as_markup(resize_keyboard=True))
    data = await state.get_data()
    await mongo_update(poll_answer.user.id, 'start')
    if await mongo_select(poll_answer.user.id):  # можно поставить счетчик повторных обращений
        print("Пользователь уже есть в базе")
    else:
        await mongo_add(poll_answer.user.id, [data['answer_1'], data['answer_2'], data['answer_3'], data['answer_4'], data['answer_5']])
    if data["answer_3"] != "Нет, не верю ни слову"\
            or {0, 1, 3, 4, 5, 6, 7}.isdisjoint(set(data["answer_4"]))==False\
            or {1, 2, 3, 4, 5, 6}.isdisjoint(set(data["answer_5"])) == False:  # Жертва пропаганды?
        print("Жертва пропаганды")
        print(await mongo_select(poll_answer.user.id))
        await state.set_state(propaganda_victim.start)
    elif {2, 8}.isdisjoint(set(data["answer_4"]))==False or {7}.isdisjoint(set(data["answer_5"]))==False:  # Король информации?
        if len(data["answer_2"]) <= 2 and {0, 1, 2, 3, 5, 7, 8} not in set(data["answer_2"]):
            print("Король информации")
        else:
            print("Фома неверующий")

