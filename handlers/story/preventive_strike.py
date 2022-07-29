from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new

from data_base.DBuse import sql_safe_select, sql_select_row_like
from filters.MapFilters import ManualFilters
from handlers.story import true_resons_hand
from utilts import simple_media, dynamic_media_answer


class PreventStrikeState(StatesGroup):
    main = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()


flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=PreventStrikeState)


@router.message((F.text == 'Давай разберём 👌'), flags=flags)
async def prevent_strike_any_brutality(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_start', value='Да')
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_any_brutality'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Каким образом? 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ну попробуй 😕'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Каким образом? 🤔', 'Ну попробуй 😕'})), flags=flags)
async def prevent_strike_some_days(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_some_days'})
    await state.set_state(PreventStrikeState.q1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Какие ❓'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Какие ❓'})), state=PreventStrikeState.q1, flags=flags)
async def prevent_strike_q1(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного 🙅‍♂️'))
    await state.set_state(PreventStrikeState.q2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это странно 🤔', 'Ничего подозрительного 🙅‍♂️'})), state=PreventStrikeState.q2,
                flags=flags)
async def prevent_strike_q2(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_first_qstn', value=message.text)
    await state.set_state(PreventStrikeState.q3)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного 🙅‍♂️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это странно 🤔', 'Ничего подозрительного 🙅‍♂️'})), state=PreventStrikeState.q3,
                flags=flags)
async def prevent_strike_q3(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_second_qstn', value=message.text)
    await state.set_state(PreventStrikeState.q4)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного 🙅‍♂️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это странно 🤔', 'Ничего подозрительного 🙅‍♂️'})), state=PreventStrikeState.q4,
                flags=flags)
async def prevent_strike_q4(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_third_qstn', value=message.text)
    await state.set_state(PreventStrikeState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q4'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного 🙅‍♂️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это странно 🤔', 'Ничего подозрительного 🙅‍♂️'})), state=PreventStrikeState.main,
                flags=flags)
async def prevent_strike_now_you(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_fourth_qstn', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_now_you'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, превентивный удар - лишь повод 👌'))
    nmarkup.row(types.KeyboardButton(text='Я и так не верил(а) в то, что Украина готовит нападение 🤷‍♂️'))
    nmarkup.row(types.KeyboardButton(text='Нет, это настоящая причина начала военных действий ☝️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    F.text.in_(
        {'Да, превентивный удар - лишь повод 👌', 'Я и так не верил(а) в то, что Украина готовит нападение 🤷‍♂️'}),
    flags=flags)
async def prevent_strike_hitler_allright(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_convinced', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, хочу 🙂'))
    nmarkup.row(types.KeyboardButton(text='Нет, продолжим разговор ⏱'))
    await simple_media(message, 'prevent_strike_hitler_allright', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Нет, это настоящая причина начала военных действий ☝️', flags=flags)
async def prevent_strike_hitler_did_it(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, хочу 🙂'))
    nmarkup.row(types.KeyboardButton(text='Нет, продолжим разговор ⏱'))
    await simple_media(message, 'prevent_strike_hitler_did_it', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('продолжим'), flags=flags)
async def prevent_strike_end_point(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_fin', value='Да')
    await state.set_state(true_resons_hand.TruereasonsState.main)
    await mongo_update_stat(message.from_user.id, 'prevent_strike')
    ManualFilters(message, state)


@router.message(F.text == 'Да, хочу 🙂', flags=flags)
async def prevent_strike_will_show(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а) 📺'))
    await simple_media(message, 'prevent_strike_will_show', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text.in_({'Посмотрел(а) 📺', '😁', '🙂', '😕', 'Достаточно, продолжим ✋'}), flags=flags)
async def prevent_strike_memes(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['lgamecount']
    except:
        count = 0
    try:
        count += 1
        isEND = await sql_select_row_like('assets', count + 1, {'name': 'prevent_strike_meme_'})
        nmarkup = ReplyKeyboardBuilder()
        if isEND is not False:
            nmarkup.add(types.KeyboardButton(text='😁'))
            nmarkup.add(types.KeyboardButton(text='🙂'))
            nmarkup.add(types.KeyboardButton(text='😕'))
            nmarkup.row(types.KeyboardButton(text='Достаточно, продолжим ✋'))
        else:
            nmarkup.row(types.KeyboardButton(text='Продолжим 🙂'))
        await dynamic_media_answer(message, 'prevent_strike_meme_', count, nmarkup.as_markup(resize_keyboard=True))
        await state.update_data(lgamecount=count)
        if isEND is False:
            await state.set_state(true_resons_hand.TruereasonsState.main)
            await mongo_update_stat(message.from_user.id, 'prevent_strike')
            text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_oh_stop_it'})
            await message.answer(text)
    except TelegramBadRequest:  # Это бессмысленный экцепт, можно потом убрать
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text='Продолжим 🙂'))
        await message.answer('Я устал шутить про Лукашенко 😌 Продолжим?',
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))
