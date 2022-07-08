from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_select, data_getter
from states.main_menu_states import MainMenuStates
from utilts import simple_media

router = Router()
router.message.filter(state=MainMenuStates)
router.message(flags={"throttling_key": "True"})

fancy_numbers = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '1️⃣0️⃣', '1️⃣1️⃣', '1️⃣2️⃣', '1️⃣3️⃣',
                 '1️⃣4️⃣', '1️⃣5️⃣')
web_list = ("Министерство обороны РФ", "РИА Новости", "Russia Today", "Телеграм-канал: Война с фейками",
            "ТАСС / Комсомольская правда / Коммерсантъ / Lenta.ru / Известия")


@router.message(F.text.contains('главное меню'))
async def mainmenu_really_menu(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_really_menu'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="База Лжи 👀"))
    nmarkup.row(types.KeyboardButton(text="Мини-игры 🎲"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Вернуться в Базу Лжи 👈") | (F.text == "База Лжи 👀"))
async def mainmenu_baseoflie(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_baseoflie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Трупы в Буче шевелятся 🧎‍♂️"))
    nmarkup.add(types.KeyboardButton(text="Распятый мальчик ☦️"))
    nmarkup.row(types.KeyboardButton(text="Ложь по ТВ 📺"))
    nmarkup.add(types.KeyboardButton(text="Ложь прочих СМИ 👀"))
    nmarkup.row(types.KeyboardButton(text="Ложь политиков и пропагандистов 🗣"))
    nmarkup.add(types.KeyboardButton(text="Обещания Путина 🗣"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Распятый мальчик ☦️'), state=MainMenuStates.baseoflie)
async def mainmenu_crossed_boy_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, 'mainmenu_crossed_boy_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'), state=MainMenuStates.crossed_boy)
async def mainmenu_crossed_boy_2(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_crossed_boy_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай ⏳'), state=MainMenuStates.crossed_boy)
async def mainmenu_crossed_boy_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_crossed_boy_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Трупы в Буче шевелятся 🧎‍♂️'), state=MainMenuStates.baseoflie)
async def mainmenu_bucha_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.about_bucha)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В чём подвох? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Я заметил(а)! 😯"))
    await simple_media(message, 'mainmenu_bucha_1', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'В чём подвох? 🤔') | (F.text == 'Я заметил(а)! 😯')), state=MainMenuStates.about_bucha)
async def mainmenu_bucha_2(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_bucha_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=MainMenuStates.about_bucha)
async def mainmenu_bucha_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_bucha_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Ложь по ТВ 📺") | (F.text.contains('🔄'))),
                state=(MainMenuStates.baseoflie, MainMenuStates.tv))
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.tv)
    tv_list = ('1 канал 📺', 'Россия 1 / 24 📺', 'НТВ 📺', 'Звезда 📺')
    nmarkup = ReplyKeyboardBuilder()
    for tv in tv_list:
        nmarkup.row(types.KeyboardButton(text=tv))
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    nmarkup.adjust(2, 2, 2)
    await message.answer('Выберите любой телеканал.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_({'1 канал 📺', 'Россия 1 / 24 📺', 'НТВ 📺', 'Звезда 📺'})) |
                 (F.text == '👈 Выбрать сюжет')), state=MainMenuStates.tv)
async def mainmenu_tv_lie_select(message: Message, state: FSMContext):
    similarity, channel = str(), str()
    if message.text == '👈 Выбрать сюжет':
        similarity = (await state.get_data())['chan']
    else:
        if message.text == '1 канал 📺':
            similarity = 'tv_first'
        elif message.text == 'Россия 1 / 24 📺':
            similarity = 'tv_24'
        elif message.text == 'НТВ 📺':
            similarity = 'tv_HTB'
        elif message.text == 'Звезда 📺':
            similarity = 'tv_star'
        await state.update_data(chan=similarity)
    how_many = len(await data_getter(f"SELECT name FROM assets WHERE name LIKE '{similarity}_lie_%'"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Выбрать другое СМИ 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await message.answer('Какой сюжет вам показать? Выберите номер.',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующий сюжет 📺')), state=MainMenuStates.tv)
async def mainmenu_tv_one_lie(message: Message, state: FSMContext):
    if message.text == 'Следующий сюжет 📺':
        number = (await state.get_data())['tv_number'] + 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(tv_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Сюжет посмотрел(а). Что с ним не так? 🤔'))
    await simple_media(message, f'{(await state.get_data())["chan"]}_lie_{number}',
                       nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Сюжет посмотрел(а). Что с ним не так? 🤔'), state=MainMenuStates.tv)
async def mainmenu_tv_one_reb(message: Message, state: FSMContext):
    data = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать сюжет'))
    if await sql_safe_select('t_id', 'assets', {'name': f"{data['chan']}_reb_{data['tv_number'] + 1}"}) is not False:
        nmarkup.add(types.KeyboardButton(text='Следующий сюжет 📺'))
    nmarkup.row(types.KeyboardButton(text='Выбрать другой телеканал 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await simple_media(message, f"{data['chan']}_reb_{data['tv_number']}", nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Ложь прочих СМИ 👀") | (F.text.contains('🔄'))),
                state=(MainMenuStates.baseoflie, MainMenuStates.web))
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.web)
    nmarkup = ReplyKeyboardBuilder()
    for web in web_list:
        nmarkup.row(types.KeyboardButton(text=web))
    nmarkup.adjust(2, 2, 2)
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer('Выберите СМИ.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(web_list))) | (F.text == '👈 Выбрать новость')), state=MainMenuStates.web)
async def mainmenu_tv_lie_select(message: Message, state: FSMContext):
    similarity, smi = str(), str()
    if message.text == '👈 Выбрать новость':
        similarity = (await state.get_data())['smi']
    else:
        if message.text == web_list[0]:
            similarity = 'MINISTRY'
        elif message.text == web_list[1]:
            similarity = 'RIANEWS'
        elif message.text == web_list[2]:
            similarity = 'RUSSIATODAY'
        elif message.text == web_list[3]:
            similarity = 'TCHANEL_WAR'
        elif message.text == web_list[4]:
            similarity = 'TACC'
        await state.update_data(smi=similarity)
    how_many = len(await data_getter(f"SELECT name FROM assets WHERE name LIKE '{similarity}_media_%'"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Выбрать другое СМИ 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await message.answer('Какой сюжет вам показать? Выберите номер.',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующая новость 👀')), state=MainMenuStates.web)
async def mainmenu_tv_one_lie(message: Message, state: FSMContext):
    if message.text == 'Следующая новость 👀':
        number = (await state.get_data())['web_number'] + 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(web_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Сюжет посмотрел(а). Что с ним не так? 🤔'))
    await simple_media(message, f'{(await state.get_data())["smi"]}_media_{number}',
                       nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Сюжет посмотрел(а). Что с ним не так? 🤔'), state=MainMenuStates.web)
async def mainmenu_tv_one_reb(message: Message, state: FSMContext):
    data = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать новость'))
    if await sql_safe_select('t_id', 'assets', {'name': f"{data['smi']}_media_{data['web_number'] + 1}"}) \
            is not False:
        nmarkup.add(types.KeyboardButton(text='Следующая новость 👀'))
    nmarkup.row(types.KeyboardButton(text='Выбрать другое СМИ 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await simple_media(message, f"{data['smi']}_exposure_{data['web_number']}", nmarkup.as_markup(resize_keyboard=True))
