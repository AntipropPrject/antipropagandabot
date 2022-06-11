from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from DBuse import poll_get, poll_write
from bata import all_data
from states import welcome_states
from DBuse import sql_safe_select
router = Router()


@router.message(commands=['message', 'help'], state="*")
async def commands_start(message: types.Message, state: FSMContext):  # Первое сообщение
    await state.clear()
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

    await message.answer(text, reply_markup=markup.as_markup())
    # if на ты

    await state.set_state(welcome_states.start_dialog.dialogue_4)


@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('(СВО)'), content_types=types.ContentType.TEXT, text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('Вторжение', 'Украину'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_3(message: types.Message, state: FSMContext):  # Начало опроса
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Задавай"))
    markup.add(types.KeyboardButton(text="А долго будешь допрашивать?"))
    text = await sql_safe_select("text", "texts", {"name": "start_lets_start"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    # if на ты
    await state.set_state(welcome_states.start_dialog.dialogue_5)


@router.message(welcome_states.start_dialog.dialogue_4, text_contains=('выражать', 'незаконно'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def message_4(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Специальная военная операция (СВО)"))
    markup.add(types.KeyboardButton(text="Война / Вторжение в Украину"))
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


@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Хорошо', 'свои', 'вопросы'), content_types=types.ContentType.TEXT, text_ignore_case=True)
@router.message(welcome_states.start_dialog.dialogue_5, text_contains=('Задавай'), content_types=types.ContentType.TEXT, text_ignore_case=True)  # Задаю первый вопрос и ставлю состояние
async def message_6(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начал(а) интересоваться после 24 февраля"))
    markup.row(types.KeyboardButton(text="Скорее да"), types.KeyboardButton(text="Скорее нет"))
    text = await sql_safe_select("text", "texts", {"name": "start_do_you_love_politics"})
    await message.answer(text, reply_markup=markup.as_markup())
    await state.set_state(welcome_states.start_dialog.dialogue_6)


@router.message(welcome_states.start_dialog.dialogue_6)  # Сохраняю 1 вопрос и задаю второй
async def message_7(message: types.Message, state: FSMContext):
    # Сохранить 1 вопрос в базу
    print(1)
    options = ["Защитить русских в Донбассе",  # Вопросы опроса
               "Предотвратить вторжение на территорию"
               " России или ЛНР/ДНР", "Денацификация / Уничтожить нацистов", "Демилитаризация / Снижение военной мощи",
               "Сменить власть в Украине", "Уничтожить биолаборатории / Предотвратить создание ядерного оружия",
               "Повысить рейтинг доверия Владимира Путина", "Захватить территории Донбасса и юга Украины",
               "Предотвратить размещение военных баз НАТО в Украине", "Я не знаю..."
               ]
    text = await sql_safe_select("text", "texts", {"name": "start_russia_goal"})
    await message.answer_poll(text, options, is_anonymous=False, allows_multiple_answers=True)  # Отправка первого опроса
    await state.set_state(welcome_states.start_dialog.dialogue_7)


@router.poll_answer(state=welcome_states.start_dialog.dialogue_7)  # Ловлю ответы первого опроса
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    print(poll_answer.option_ids)  # тут нужно записать ответы опроса в базу
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Да, полностью доверяю"))
    markup.add(types.KeyboardButton(text="Скорее да"), types.KeyboardButton(text="Скорее нет"))
    markup.add(types.KeyboardButton(text="Нет, не верю ни слову"))
    text = await sql_safe_select("text", "texts", {"name": "start_belive_TV"})
    await Bot(all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup())
    await state.set_state(welcome_states.start_dialog.dialogue_8)


@router.message(state=welcome_states.start_dialog.dialogue_8)  # Сохранение 3 вопроса и отправка 4
async def message_8(message: types.Message, state: FSMContext):
    #сохранение 3 вопроса
    options = ["РИА Новости", "Russia Today",
               "Meduza / BBC / Радио Свобода / Медиазона / Настоящее время / Популярная Политика",
               "Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews",
               "Телеграм-канал: Война с фейками", "РБК",
               "ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс",
               "Яндекс.Новости", "Википедия", "Никому из них...",
               ]
    text = await sql_safe_select("text", "texts", {"name": "start_internet_belive"})
    await message.answer_poll(text, options, is_anonymous=False, allows_multiple_answers=True)
    await state.set_state(welcome_states.start_dialog.dialogue_9)


@router.poll_answer(state = welcome_states.start_dialog.dialogue_9)  # Ловлю ответы второго опроса и отправляю третий
async def poll_answer_handler_tho(poll_answer: types.PollAnswer, state=FSMContext):
    print(poll_answer.option_ids)  # тут нужно записать ответы опроса в базу
    options = ["Владимир Путин", "Дмитрий Песков", "Рамзан Кадыров",
               "Сергей Лавров", "Юрий Подоляка", "Владимир Соловьев",
               "Ольга Скабеева", "Никому из них..."
               ]
    text = await sql_safe_select("text", "texts", {"name": "start_people_belive"})
    await Bot(all_data().bot_token).send_poll(poll_answer.user.id, text, options, is_anonymous=False, allows_multiple_answers=True)
    await state.set_state(welcome_states.start_dialog.dialogue_10)


@router.poll_answer(state = welcome_states.start_dialog.dialogue_10)  # Ловлю ответы третьего опроса и перехожу к антипропаганде
async def poll_answer_handler_three(poll_answer: types.PollAnswer, state=FSMContext):
    text = await sql_safe_select("text", "texts", {"name": "start_thank_you"})
    # Сохранить все значения и присвоить статус собеседнику для дальнейшего сценария
    await Bot(all_data().bot_token).send_message(poll_answer.user.id, text)