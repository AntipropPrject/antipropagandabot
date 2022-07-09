from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_select, data_getter, sql_games_row_selecter
from states.main_menu_states import MainMenuStates
from utilts import simple_media, game_answer

router = Router()
router.message.filter(state=MainMenuStates)
flags = {"throttling_key": "True"}

fancy_numbers = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '1️⃣0️⃣', '1️⃣1️⃣', '1️⃣2️⃣', '1️⃣3️⃣',
                 '1️⃣4️⃣', '1️⃣5️⃣')
web_list = ("Министерство обороны РФ", "РИА Новости", "Russia Today", "Телеграм-канал: Война с фейками",
            "ТАСС / Комсомольская правда / Коммерсантъ / Lenta.ru / Известия")
tv_list = ('1 канал 📺', 'Россия 1 / 24 📺', 'НТВ 📺', 'Звезда 📺')
ppl_options = ("Владимир Путин 🗣", "Дмитрий Песков 🗣", "Сергей Лавров 🗣",
               "Владимир Соловьев 🗣", "Никита Михалков 🗣", "Маргарита Симоньян 🗣")


@router.message(F.text.contains('главное меню'), flags=flags)
async def mainmenu_really_menu(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_really_menu'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="База Лжи 👀"))
    nmarkup.row(types.KeyboardButton(text="Мини-игры 🎲"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Вернуться в Базу Лжи 👈") | (F.text == "База Лжи 👀")), flags=flags)
async def mainmenu_baseoflie(message: Message, state: FSMContext):
    await state.clear()
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


@router.message((F.text == 'Распятый мальчик ☦️'), state=MainMenuStates.baseoflie, flags=flags)
async def mainmenu_crossed_boy_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, 'mainmenu_crossed_boy_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'), state=MainMenuStates.crossed_boy, flags=flags)
async def mainmenu_crossed_boy_2(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.crossed_boy)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_crossed_boy_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай ⏳'), state=MainMenuStates.crossed_boy, flags=flags)
async def mainmenu_crossed_boy_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_crossed_boy_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Трупы в Буче шевелятся 🧎‍♂️'), state=MainMenuStates.baseoflie, flags=flags)
async def mainmenu_bucha_1(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.about_bucha)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В чём подвох? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Я заметил(а)! 😯"))
    await simple_media(message, 'mainmenu_bucha_1', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'В чём подвох? 🤔') | (F.text == 'Я заметил(а)! 😯')), state=MainMenuStates.about_bucha,
                flags=flags)
async def mainmenu_bucha_2(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'mainmenu_bucha_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳"), state=MainMenuStates.about_bucha, flags=flags)
async def mainmenu_bucha_3(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.baseoflie)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_bucha_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Ложь по ТВ 📺") | (F.text.contains('🔄'))),
                state=(MainMenuStates.baseoflie, MainMenuStates.tv), flags=flags)
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.tv)
    nmarkup = ReplyKeyboardBuilder()
    for tv in tv_list:
        nmarkup.row(types.KeyboardButton(text=tv))
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    nmarkup.adjust(2, 2, 2)
    await message.answer('Выберите любой телеканал.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_({'1 канал 📺', 'Россия 1 / 24 📺', 'НТВ 📺', 'Звезда 📺'})) |
                 (F.text == '👈 Выбрать сюжет')), state=MainMenuStates.tv, flags=flags)
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


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующий сюжет 📺')),
                state=MainMenuStates.tv, flags=flags)
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


@router.message((F.text == 'Сюжет посмотрел(а). Что с ним не так? 🤔'), state=MainMenuStates.tv, flags=flags)
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
                state=(MainMenuStates.baseoflie, MainMenuStates.web), flags=flags)
async def mainmenu_web_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.web)
    nmarkup = ReplyKeyboardBuilder()
    for web in web_list:
        nmarkup.row(types.KeyboardButton(text=web))
    nmarkup.adjust(2, 2, 2)
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer('Выберите СМИ.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(web_list))) | (F.text == '👈 Выбрать новость')),
                state=MainMenuStates.web, flags=flags)
async def mainmenu_web_lie_select(message: Message, state: FSMContext):
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


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующая новость 👀')),
                state=MainMenuStates.web, flags=flags)
async def mainmenu_web_one_lie(message: Message, state: FSMContext):
    if message.text == 'Следующая новость 👀':
        number = (await state.get_data())['web_number'] + 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(web_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Сюжет посмотрел(а). Что с ним не так? 🤔'))
    await simple_media(message, f'{(await state.get_data())["smi"]}_media_{number}',
                       nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Сюжет посмотрел(а). Что с ним не так? 🤔'),
                state=MainMenuStates.web, flags=flags)
async def mainmenu_web_one_reb(message: Message, state: FSMContext):
    data = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать новость'))
    if await sql_safe_select('t_id', 'assets', {'name': f"{data['smi']}_media_{data['web_number'] + 1}"}) \
            is not False:
        nmarkup.add(types.KeyboardButton(text='Следующая новость 👀'))
    nmarkup.row(types.KeyboardButton(text='Выбрать другое СМИ 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await simple_media(message, f"{data['smi']}_exposure_{data['web_number']}", nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Ложь политиков и пропагандистов 🗣") | (F.text.contains('🔄'))),
                state=(MainMenuStates.baseoflie, MainMenuStates.ppl), flags=flags)
async def mainmenu_ppl_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.ppl)
    nmarkup = ReplyKeyboardBuilder()
    for lying_shit in ppl_options:
        nmarkup.row(types.KeyboardButton(text=lying_shit))
    nmarkup.adjust(2, 2, 2, 2)
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer('Выберите человека.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(ppl_options))) | (F.text == '👈 Выбрать ложь')),
                state=MainMenuStates.ppl, flags=flags)
async def mainmenu_ppl_lie_select(message: Message, state: FSMContext):
    similarity, ppl = str(), str()
    if message.text == '👈 Выбрать ложь':
        similarity = (await state.get_data())['ppl']
    else:
        person = message.text
        print(person)
        if person == ppl_options[0]:
            similarity = 'putin_lie_game_'
        elif person == ppl_options[1]:
            similarity = 'statement_Песков_'
        elif person == ppl_options[2]:
            similarity = 'statement_Лавров_'
        elif person == ppl_options[3]:
            similarity = 'statement_Соловьев_'
        elif person == ppl_options[4]:
            similarity = 'statement_Михалков_'
        elif person == ppl_options[5]:
            similarity = 'statement_Симоньян_'
        await state.update_data(ppl=similarity)
    how_many = len(await data_getter(f"SELECT name FROM assets WHERE name LIKE '{similarity}%'"))
    print(how_many)
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Выбрать другого человека 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await message.answer('Какую ложь вам показать? Выберите номер.',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующая ложь 🗣')),
                state=MainMenuStates.ppl, flags=flags)
async def mainmenu_ppl_one_lie(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Следующая ложь 🗣':
        number = (await state.get_data())['ppl_number'] + 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(ppl_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Целенаправленная ложь 👎'))
    nmarkup.row(types.KeyboardButton(text='Случайная ошибка / Не ложь 👍'))
    print(data['ppl'])
    if data['ppl'] == 'putin_lie_game_':
        tag = f'putin_lie_game_{number}'
        print(tag)
        await simple_media(message, tag,
                           nmarkup.as_markup(resize_keyboard=True))
        truth_data = (await data_getter(f"SELECT belivers, nonbelivers FROM "
                                        f"public.putin_lies WHERE asset_name = '{tag}'"))[0]
        print('DAAATA', truth_data)
        await state.update_data({'belive': truth_data[0], 'unbelive': truth_data[1]})
    else:
        tag = f'{data["ppl"]}{number}'
        await simple_media(message, tag,
                           nmarkup.as_markup(resize_keyboard=True))
        truth_data = (await data_getter(f"SELECT belivers, nonbelivers FROM "
                                        f"public.mistakeorlie WHERE asset_name = '{tag}'"))[0]
        print('DAAATA', truth_data[0])
        await state.update_data({'belive': truth_data[0], 'unbelive': truth_data[1]})


@router.message(((F.text == 'Целенаправленная ложь 👎') | (F.text == 'Случайная ошибка / Не ложь 👍')),
                state=MainMenuStates.ppl, flags=flags)
async def mainmenu_ppl_one_reb(message: Message, state: FSMContext):
    data = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать ложь'))
    if data['ppl'] == ppl_options[0]:
        if await sql_safe_select('t_id', 'assets', {'name': f'putin_lie_game_{data["ppl_number"] + 1}'}) is not False:
            nmarkup.add(types.KeyboardButton(text='Следующая ложь 🗣'))
    else:
        if await sql_safe_select('t_id', 'assets', {'name': f"{data['ppl']}{data['ppl_number'] + 1}"}) \
                is not False:
            nmarkup.add(types.KeyboardButton(text='Следующая ложь 🗣'))
    nmarkup.row(types.KeyboardButton(text='Выбрать другого человека 🔄'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    t_percentage = (data['belive'] / (data['belive'] + data['unbelive'])) * 100
    await message.answer(
        f'А вот, что думают другие мои собеседники:\n\n👍 Случайная ошибка / Не ложь:'
        f' {round(t_percentage)}%\n👎 Целенаправленная ложь: {round(100 - t_percentage)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Обещания Путина 🗣") | (F.text.contains('👈'))),
                state=(MainMenuStates.baseoflie, MainMenuStates.ptn), flags=flags)
async def mainmenu_ptn_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.ptn)
    how_many = len(await data_getter(f"SELECT id FROM putin_old_lies"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text="Вернуться в Базу Лжи 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    await message.answer('Какое обещание вам показать? Выберите номер.',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующее обещание 🗣')),
                state=MainMenuStates.ptn, flags=flags)
async def mainmenu_ptn_one_lie(message: Message, state: FSMContext):
    if message.text == 'Следующее обещание 🗣':
        number = (await state.get_data())['ptn_number'] + 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(ptn_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Целенаправленная ложь 👎'))
    nmarkup.row(types.KeyboardButton(text='Случайная ошибка / Не ложь 👍'))
    tag = f'putin_oldlie_game_{number}'
    await simple_media(message, tag, nmarkup.as_markup(resize_keyboard=True))
    truth_data = (await data_getter(f"SELECT belivers, nonbelivers FROM "
                                    f"public.putin_old_lies WHERE asset_name = '{tag}'"))[0]
    print('DAAATA', truth_data)
    await state.update_data({'belive': truth_data[0], 'unbelive': truth_data[1]})


@router.message(((F.text == 'Целенаправленная ложь 👎') | (F.text == 'Случайная ошибка / Не ложь 👍')),
                state=MainMenuStates.ptn, flags=flags)
async def mainmenu_ptn_one_reb(message: Message, state: FSMContext):
    data = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать обещание'))
    if await sql_safe_select('id', 'putin_old_lies', {'asset_name': f"putin_oldlie_game_{data['ptn_number'] + 1}"}) \
            is not False:
        nmarkup.add(types.KeyboardButton(text='Следующее обещание 🗣'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    t_percentage = (data['belive'] / (data['belive'] + data['unbelive'])) * 100
    await message.answer(
        f'А вот, что думают другие мои собеседники:\n\n👍 Случайная ошибка / Не ложь: {round(t_percentage)}'
        f'%\n👎 Целенаправленная ложь: {round(100 - t_percentage)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Мини-игры 🎲') | (F.text == 'Вернуться к мини-играм 👈')), flags=flags)
async def mainmenu_games_start(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.games)
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_games_here'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Правда или Ложь ✅'))
    nmarkup.add(types.KeyboardButton(text='Абсурд или Нормальность 🤦‍♀️'))
    nmarkup.row(types.KeyboardButton(text='Нацизм в России или Украине 🙋‍♂️'))
    nmarkup.add(types.KeyboardButton(text='А я сейчас вам покажу... ☝️'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Правда или Ложь ✅"),
                state=(MainMenuStates.games, MainMenuStates.truthgame), flags=flags)
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenuStates.truthgame)
    await state.update_data(similarity="truthgame_")
    how_many = len(await data_getter(f"SELECT id FROM truthgame"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Вернуться к мини-играм 👈'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_truthgame_start'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующий сюжет 👉')),
                state=MainMenuStates.truthgame, flags=flags)
async def mainmenu_tv_one_lie(message: Message, state: FSMContext):
    if message.text in fancy_numbers:
        number = fancy_numbers.index(message.text) + 1
    else:
        number = (await state.get_data())['game_number'] + 1
    current_row = await sql_games_row_selecter('truthgame', number)
    await state.update_data(game_number=number, game_data=current_row)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Это правда ✅'))
    nmarkup.add(types.KeyboardButton(text='Это ложь ❌'))
    await game_answer(message, current_row['plot_media'], current_row['plot_text'],
                      reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Это правда ✅') | (F.text == 'Это ложь ❌')), state=MainMenuStates.truthgame, flags=flags)
async def mainmenu_tv_one_reb(message: Message, state: FSMContext):
    data = (await state.get_data())['game_data']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать сюжет'))
    if await sql_games_row_selecter('truthgame', data['ROW_NUMBER'] + 1) is not False:
        nmarkup.add(types.KeyboardButton(text='Следующий сюжет 👉'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    reality = ''
    if message.text == "Это правда ✅":
        if data['truth'] is True:
            reality = "Правильно! Это правда!"
        elif data['truth'] is False:
            reality = "Неверно! Это ложь!"
    elif message.text == "Это ложь ❌":
        if data['truth'] is True:
            reality = "Неверно! Это правда!"
        elif data['truth'] is False:
            reality = "Правильно! Это ложь!"
    t_percentage = data['belivers'] / (data['belivers'] + data['nonbelivers'])
    text = reality + f'\n\nРезультаты других участников:\n✅ <b>Правда:</b> {round(t_percentage * 100)}%\n' \
                     f'❌ <b>Ложь</b>: {round((100 - t_percentage * 100))}%' + '\n\nПодтверждение - ниже.'
    await message.answer(text)
    await game_answer(message, data['rebb_media'], data['rebb_text'],
                      reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Абсурд или Нормальность 🤦‍♀️') | (F.text == '👈 Выбрать новость')),
                state=(MainMenuStates.games, MainMenuStates.normalgame), flags=flags)
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenuStates.normalgame)
    how_many = len(await data_getter(f"SELECT id FROM normal_game"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Вернуться к мини-играм 👈'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_normalgame_start'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующая новость 👀')),
                state=MainMenuStates.normalgame, flags=flags)
async def mainmenu_tv_one_lie(message: Message, state: FSMContext):
    if message.text in fancy_numbers:
        number = fancy_numbers.index(message.text) + 1
    else:
        number = (await state.get_data())['game_number'] + 1
    print(number)
    current_row = await sql_games_row_selecter('normal_game', number)
    print(current_row)
    await state.update_data(game_number=number, game_data=current_row)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Это абсурд 🤦‍♀️'))
    nmarkup.add(types.KeyboardButton(text='Это нормально 👌'))
    await game_answer(message, current_row['plot_media'], current_row['plot_text'],
                      reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Это абсурд 🤦‍♀️') | (F.text == 'Это нормально 👌')),
                state=MainMenuStates.normalgame, flags=flags)
async def mainmenu_tv_one_reb(message: Message, state: FSMContext):
    data = (await state.get_data())['game_data']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать новость'))
    if await sql_games_row_selecter('normal_game', data['ROW_NUMBER'] + 1) is not False:
        nmarkup.add(types.KeyboardButton(text='Следующая новость 👀'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    t_percentage = data['belivers'] / (data['belivers'] + data['nonbelivers'])
    text = f'Результаты других участников:\n🤦‍♂️ Это абсурд: {round(t_percentage * 100)}%\n' \
           f'👌 Это нормально: {round(100 - t_percentage * 100)}%'
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Нацизм в России или Украине 🙋‍♂️') | (F.text == '👈 Выбрать фото')),
                state=(MainMenuStates.games, MainMenuStates.nazigame), flags=flags)
async def mainmenu_tv_select(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenuStates.nazigame)
    how_many = len(await data_getter(f"SELECT id FROM ucraine_or_not_game"))
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text='Вернуться к мини-играм 👈'))
    nmarkup.add(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_countrygame_start'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text == 'Следующее фото 📷')),
                state=MainMenuStates.nazigame, flags=flags)
async def mainmenu_tv_one_lie(message: Message, state: FSMContext):
    if message.text in fancy_numbers:
        number = fancy_numbers.index(message.text) + 1
    else:
        number = (await state.get_data())['game_number'] + 1
    print(number)
    current_row = await sql_games_row_selecter('ucraine_or_not_game', number)
    print(current_row)
    await state.update_data(game_number=number, game_data=current_row)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Это в России 🇷🇺'))
    nmarkup.add(types.KeyboardButton(text='Это на Украине 🇺🇦'))
    await game_answer(message, current_row['plot_media'], current_row['plot_text'],
                      reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == 'Это в России 🇷🇺') | (F.text == 'Это на Украине 🇺🇦')),
                state=MainMenuStates.nazigame, flags=flags)
async def mainmenu_tv_one_reb(message: Message, state: FSMContext):
    data = (await state.get_data())['game_data']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать фото'))
    if await sql_games_row_selecter('ucraine_or_not_game', data['ROW_NUMBER'] + 1) is not False:
        nmarkup.add(types.KeyboardButton(text='Следующее фото 📷'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    reality = data['truth']
    text = ''
    if message.text == "Это на Украине 🇺🇦":
        if reality is True:
            text = 'Правильно! Это на Украине!'
        if reality is False:
            text = 'Вы ошиблись! Это в России!'
    elif message.text == "Это в России 🇷🇺":
        if reality is True:
            text = 'Вы ошиблись! Это на Украине!'
        if reality is False:
            text = 'Правильно! Это в России!'
    t_percentage = data['belivers'] / (data['belivers'] + data['nonbelivers'])
    await message.answer(
        f'{text}\nРезультаты других участников:\n'
        f'🇷🇺 В России: {round(100 - t_percentage * 100)}% \n🇺🇦 На Украине: {round(t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "А я сейчас вам покажу... ☝️") | (F.text.contains('👈'))),
                state=(MainMenuStates.games, MainMenuStates.strikememes), flags=flags)
async def mainmenu_ptn_select(message: Message, state: FSMContext):
    await state.set_state(MainMenuStates.strikememes)
    how_many = len(await data_getter(f"SELECT name FROM assets WHERE name LIKE 'prevent_strike_meme_%'"))
    await state.update_data(len=how_many)
    nmarkup = ReplyKeyboardBuilder()
    for i in range(how_many):
        nmarkup.row(types.KeyboardButton(text=f'{fancy_numbers[i]}'))
    nmarkup.adjust(5, 5, 5)
    nmarkup.row(types.KeyboardButton(text="Вернуться к мини-играм 👈"))
    nmarkup.add(types.KeyboardButton(text="Вернуться в главное меню 👇"))
    text = await sql_safe_select('text', 'texts', {'name': 'mainmenu_lmemes_start'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.in_(set(fancy_numbers))) | (F.text.in_({'😁', '🙂', '😕'}))),
                state=MainMenuStates.strikememes, flags=flags)
async def mainmenu_ptn_one_lie(message: Message, state: FSMContext):
    if message.text in {'😁', '🙂', '😕'}:
        number = (await state.get_data())['strk_number'] + 1
        if number > (await state.get_data())['len']:
            number = 1
    else:
        number = fancy_numbers.index(message.text) + 1
    await state.update_data(strk_number=number)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='😁'))
    nmarkup.add(types.KeyboardButton(text='🙂'))
    nmarkup.add(types.KeyboardButton(text='😕'))
    nmarkup.row(types.KeyboardButton(text='👈 Выбрать номер мема'))
    nmarkup.row(types.KeyboardButton(text='Вернуться в главное меню 👇'))
    tag = f'prevent_strike_meme_{number}'
    await simple_media(message, tag, nmarkup.as_markup(resize_keyboard=True))