from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from data_base.DBuse import data_getter, sql_safe_select, sql_safe_update
from filters.All_filters import PutinFilter
from handlers.stopwar_hand import StopWarState
from middleware import CounterMiddleware


class StateofPutin(StatesGroup):
    main = State()
    game1 = State()
    game2 = State()
    final = State()


router = Router()
router.message.middleware(CounterMiddleware())
router.message.filter(state=(StateofPutin))


@router.message(PutinFilter(), (F.text.in_({"Давай 🤝"})))
async def putin_love_putin(message: Message, state: FSMContext):
    await state.set_state(StateofPutin.main)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен, кто, если не Путин? 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен 🙅‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Давай 🤝"})))
async def putin_not_love_putin(message: Message, state: FSMContext):
    await state.set_state(StateofPutin.main)
    text = "Выберите описание Владимира Путина, которое вы считаете наиболее точным:"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Отличный президент ✊"))
    nmarkup.row(types.KeyboardButton(text="Военный преступник 😤"))
    nmarkup.row(types.KeyboardButton(text="Не лучший президент, но кто, если не Путин? 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Хороший президент, но его приказы плохо исполняют 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Был хорошим президентом раньше, но сейчас - нет 🙅"))
    nmarkup.adjust(2, 1, 1, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Нет, не согласен 🙅‍♂️", "Может и есть, но пока их не видно 🤷‍♂️", "Конечно такие люди есть 🙂"})))
async def putin_big_love_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_big_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да 👍"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет 👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Согласен, кто, если не Путин? 🤷‍♂️") | (F.text == "Не лучший президент, но кто, если не Путин? 🤷‍♂️"))
async def putin_only_one(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_only_one'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Может и есть, но пока их не видно 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Конечно такие люди есть 🙂"))
    nmarkup.row(types.KeyboardButton(text="Не говори такие вещи, Путин с нами надолго! ✊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    (F.text == "Не говори такие вещи, Путин с нами надолго! ✊") | (F.text == "Отличный президент ✊"))
async def putin_so_handsome(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_so_handsome'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да 👍"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет 👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Хороший президент, но его приказы плохо исполняют 🤷‍♀️"))
async def putin_not_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_not_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да 👍"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет 👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Скорее да 👍', "Скорее нет 👎"})))
async def putin_game_of_lie(message: Message, state: FSMContext):
    await state.set_state(StateofPutin.game1)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_game_of_lie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем!  🚀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Начнем!  🚀") | (F.text == "Нет, давай продолжим 👉") | (F.text == "Продолжаем 👉")),
                state=StateofPutin.game1)
async def putin_game1_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['pgamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.putin_lies")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal FROM public.putin_lies "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        await state.update_data(pgamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.add(types.KeyboardButton(text="Случайная ошибка / Не ложь 👍"))
        nmarkup.add(types.KeyboardButton(text="Целенаправленная ложь 👎"))
        if truth_data[0] is not None:
            capt = ""
            if truth_data[1] is not None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'{truth_data[1]}\n',
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
            "Ой, у меня закончились примеры :(\nНо не волуйтесь, у меня для вас есть еще одна игра!",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Случайная ошибка / Не ложь 👍") | (F.text == "Целенаправленная ложь 👎")), state=StateofPutin.game1)
async def putin_game1_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    END = bool(data['pgamecount'] == data_getter('SELECT COUNT(id) FROM public.putin_lies')[0][0])
    nmarkup = ReplyKeyboardBuilder()
    if END is False:
        nmarkup.row(types.KeyboardButton(text="Продолжаем 👉"))
        nmarkup.row(types.KeyboardButton(text="Достаточно ✋"))
    else:
        nmarkup.row(types.KeyboardButton(text="Хорошо 🤔"))
    if message.text == "Случайная ошибка / Не ложь 👍":
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Целенаправленная ложь 👎":
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("putin_lies", base_update_dict, {'id': data['pgamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    await message.answer(
        f'А вот что думают другие участники:\n👍 <b>Случайная ошибка / не ложь:</b> {round(t_percentage * 100)}%\n'
        f'👎 <b>Целенаправленная ложь: </b>'
        f'{round((100 - t_percentage * 100))}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
    if END is True:
        await message.answer('На этом давайте перейдём перейдём к другому, '
                             'не менее важному качеству хорошего президента.')


@router.message((F.text == "Достаточно ✋"), state=StateofPutin.game1)
async def putin_game1_are_you_sure(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, давай продолжим 👉"))
    nmarkup.row(types.KeyboardButton(text="Да, хватит 🙅‍♀️"))
    await message.answer('Точно?', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Да, хватит 🙅‍♀️") | (F.text == "Давай") | (F.text == "Хорошо 🤔")), state=StateofPutin.game1)
async def putin_plenty_promises(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StateofPutin.game2)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_plenty_promises'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Давай 👌")), state=StateofPutin.game2)
async def putin_nothing_done(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_nothing_done'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем! 🚀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Начнем! 🚀")), state=StateofPutin.game2)
async def putin_gaming(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_gaming'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я готов(а) 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Я готов(а) 👌") | (F.text == "Нет, давай продолжим 👉") | (F.text == "Продолжаем! 👉")),
                state=StateofPutin.game2)
async def putin_game2_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['pgamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.putin_old_lies")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal FROM public.putin_old_lies "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print(truth_data)
        await state.update_data(pgamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.add(types.KeyboardButton(text="Виноват 👎"))
        nmarkup.add(types.KeyboardButton(text="Не виноват 👍"))
        if truth_data[0] != None:
            capt = ""
            if truth_data[1] != None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'Вот что обещал Путин:\n\n{truth_data[1]}',
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, давай дальше"))
        await message.answer(
            "Боюсь, что пока что у меня кончились примеры. Я поищу еще, а пока что продолжим",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Не виноват 👍") | (F.text == "Виноват 👎")), state=StateofPutin.game2)
async def putin_game2_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    base_update_dict = dict()
    if message.text == "Не виноват 👍":
        print(data['belive'] + 1)
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Виноват 👎":
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("putin_old_lies", base_update_dict, {'id': data['pgamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем! 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно ✋"))
    await message.answer(
        f'А вот что думают другие участники:\n\n'
        f'👎 <b>Виноват</b>: {round((100 - t_percentage * 100))}% \n👍 <b>Не виноват</b>: {round(t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Достаточно ✋")), state=StateofPutin.game2)
async def putin_game2_are_you_sure(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, давай продолжим 👉"))
    nmarkup.row(types.KeyboardButton(text="Да, достаточно 🤷‍♀️"))
    await message.answer('Вы уверены? У меня еще есть примеры', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Да, достаточно 🤷‍♀️") | (F.text == "Хорошо, давай дальше")), state=StateofPutin.game2)
async def putin_in_the_past(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StateofPutin.final)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_in_the_past'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, я согласен(а) ✅"))
    nmarkup.row(types.KeyboardButton(text="Нет, я не согласен(а) ❌"))
    nmarkup.row(types.KeyboardButton(text="Докажи 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Докажи 🤔") | (F.text == "Нет, я не согласен(а) ❌")), state=StateofPutin.final)
async def putin_prove_me(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_prove_me'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Да, я согласен(а) ✅") | (F.text == "Военный преступник 😤") |
     (F.text == "Был хорошим президентом раньше, но сейчас - нет 🙅") |
     (F.text == "Давай 👌")), state=StateofPutin)
async def stopwar_start(message: Message, state: FSMContext):
    await state.set_state(StopWarState.main)
    text = (
        'Давайте поговорим о том, как закончить войну\n\n'
        'Как считаете, Путин готов закончить эту войну в ближайшие месяцы?')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да ✅"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет ❌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
