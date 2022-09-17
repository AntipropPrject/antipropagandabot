from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import sql_safe_select, mongo_count_docs
from filters.MapFilters import OperationWar
from states.true_goals_states import TrueGoalsState

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=TrueGoalsState)


@router.message((F.text.contains('нтересно')) | (F.text.contains('скучно')), flags=flags)
async def goals_war_point_now(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_war_point_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(OperationWar(answer='(СВО)'), (F.text == "Продолжай ⏳"),
                state=TrueGoalsState.before_shop, flags=flags)
async def goals_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop_operation)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Продолжай ⏳", state=TrueGoalsState.before_shop_operation, flags=flags)
async def goals_not_operation(message: Message, state: FSMContext):
    await state.set_state(TrueGoalsState.before_shop)
    text = await sql_safe_select('text', 'texts', {'name': 'goals_not_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 🤝"))
    nmarkup.add(types.KeyboardButton(text="*презрительно хмыкнуть* 🤨"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Понятно 👌')) | (F.text.contains('Да, выйти ⬇️')), flags=flags)
async def goals_big_war(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_big_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="И какие цели настоящие? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains("И какие цели настоящие? 🤔")), flags=flags)
async def goals_big_war(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'goals_no_clear'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи результаты 📊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains("Покажи результаты 📊")), flags=flags)
async def goals_big_war(message: Message, state: FSMContext):
    var_aims = dict()
    var_aims['♻️ Сменить власть на Украине / Сделать её лояльной России'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Сменить власть на Украине"}})
    var_aims['💂 Предотвратить размещение военных баз НАТО на Украине'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "НАТО на Украине"}})
    var_aims['📈 Повысить рейтинг доверия Владимира Путина'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "рейтинг доверия Владимира Путина"}})
    var_aims['👪 Защитить русских в Донбассе'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Защитить русских в Донбассе"}})
    var_aims['🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Предотвратить вторжение"}})
    var_aims['🤬 Денацификация / Уничтожить нацистов'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Денацификация"}})
    var_aims['💣 Демилитаризация / Снижение военной мощи'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Демилитаризация"}})
    var_aims['🗺 Вернуть России исторические земли / Объединить русский народ'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Объединить русский народ"}})
    var_aims['🤯 Предотвратить секретные разработки: биологическое оружие / ядерное оружие'] = await mongo_count_docs('database', 'statistics_new', {'war_aims_ex': {'$regex': "Предотвратить секретные разработки"}})
    for i in var_aims:
        print(i)

    a = dict(sorted(var_aims.items(), key=lambda x: x[1]))
    print(a)
