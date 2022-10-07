from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new, mongo_update_stat
from data_base.DBuse import sql_safe_select, mongo_count_docs, sql_games_row_selecter, mongo_game_answer
from resources.all_polls import welc_message_one
from states.preventstrike_states import PreventStrikeState
from states.true_goals_states import WarGoalsState
from utilts import simple_media, CoolPercReplacer, game_answer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=PreventStrikeState)


async def prevent_strike_any_brutality(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.main)
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
    await state.set_state(PreventStrikeState.results)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_q4'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, это странно 🤔'))
    nmarkup.row(types.KeyboardButton(text='Ничего подозрительного 🙅‍♂️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это странно 🤔', 'Ничего подозрительного 🙅‍♂️'})), state=PreventStrikeState.results,
                flags=flags)
async def prevent_strike_results(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_fourth_qstn', value=message.text)

    sq_all = await mongo_count_docs('database', 'statistics_new', {'$or': [{'prevent_first_qstn': {'$exists': True}},
                                                                           {'prevent_second_qstn': {'$exists': True}},
                                                                           {'prevent_third_qstn': {'$exists': True}},
                                                                           {'prevent_fourth_qstn': {'$exists': True}}
                                                                           ]})
    any_strange = await mongo_count_docs('database', 'statistics_new',
                                         {'$or': [{'prevent_first_qstn': 'Да, это странно 🤔'},
                                                  {'prevent_second_qstn': 'Да, это странно 🤔'},
                                                  {'prevent_third_qstn': 'Да, это странно 🤔'},
                                                  {'prevent_fourth_qstn': 'Да, это странно 🤔'}
                                                  ]})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'prevent_strike_results'}), sq_all)
    txt.replace('XX', any_strange)

    sq_first_all = await mongo_count_docs('database', 'statistics_new', {'prevent_first_qstn': {'$exists': True}})
    sq_first_str = await mongo_count_docs('database', 'statistics_new', {'prevent_first_qstn': 'Да, это странно 🤔'})
    txt.replace('AA', sq_first_str, temp_base=sq_first_all)
    sq_second_all = await mongo_count_docs('database', 'statistics_new', {'prevent_second_qstn': {'$exists': True}})
    sq_second_str = await mongo_count_docs('database', 'statistics_new', {'prevent_second_qstn': 'Да, это странно 🤔'})
    txt.replace('BB', sq_second_str, temp_base=sq_second_all)
    sq_third_all = await mongo_count_docs('database', 'statistics_new', {'prevent_third_qstn': {'$exists': True}})
    sq_third_str = await mongo_count_docs('database', 'statistics_new', {'prevent_third_qstn': 'Да, это странно 🤔'})
    txt.replace('CC', sq_third_str, temp_base=sq_third_all)
    sq_fourth_all = await mongo_count_docs('database', 'statistics_new', {'prevent_fourth_qstn': {'$exists': True}})
    sq_fourth_str = await mongo_count_docs('database', 'statistics_new', {'prevent_fourth_qstn': 'Да, это странно 🤔'})
    txt.replace('DD', sq_fourth_str, temp_base=sq_fourth_all)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👉'))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == 'Продолжим 👉', flags=flags)
async def prevent_strike_hitler_did_it(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.before_game)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Да, хочу 🙂'))
    nmarkup.row(types.KeyboardButton(text='Нет, продолжим разговор ⏱'))
    await simple_media(message, 'prevent_strike_hitler_did_it', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Нет, продолжим разговор ⏱', state=PreventStrikeState.before_game, flags=flags)
async def prevent_strike_end_point(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='game_i_show_u', value='Пропустили')
    await prevent_strike_do_you_agree(message, state)


@router.message(F.text == 'Да, хочу 🙂', flags=flags)
async def prevent_strike_will_show(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='game_i_show_u', value='Начали и НЕ закончили')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а) 📺'))
    await simple_media(message, 'prevent_strike_will_show', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Посмотрел(а) 📺', flags=flags)
async def prevent_strike_its_all_memes(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_its_all_memes'})
    await state.clear()
    await state.set_state(PreventStrikeState.memes)
    await message.answer(text)
    await prevent_strike_memes(message, state)


@router.message(F.text.in_({'Ещё! 🙂', 'Нет, покажи ещё мем 🙂'}), state=PreventStrikeState.memes, flags=flags)
async def prevent_strike_memes(message: Message, state: FSMContext):
    count = (await state.get_data()).get('lgamecount', 0)
    count += 1
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='😁'))
    nmarkup.add(types.KeyboardButton(text='🙂'))
    nmarkup.add(types.KeyboardButton(text='😕'))
    meme_data = await sql_games_row_selecter('strikememes', count)
    await game_answer(message, meme_data['t_id'], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    await state.update_data({'meme_data': meme_data, 'lgamecount': count})


@router.message(F.text.in_({'😁', '🙂', '😕'}), state=PreventStrikeState.memes, flags=flags)
async def prevent_strike_memes_more(message: Message, state: FSMContext):
    data = await state.get_data()
    count = data.get('lgamecount')
    meme_data = data.get('meme_data')
    answer = str()
    if message.text == '😁':
        answer = 'funny_reaction'
    elif message.text == '🙂':
        answer = 'positive_reaction'
    elif message.text == '😕':
        answer = 'negative_reaction'
    await mongo_game_answer(message.from_user.id, 'strikememes', meme_data.get('id'),
                            answer, {'id': meme_data.get('id')})

    all_usrs = meme_data.get('funny_reaction') + meme_data.get('positive_reaction') + meme_data.get('negative_reaction')
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'prevent_strike_memes_more'}), all_usrs)
    txt.replace('XX', meme_data.get('funny_reaction'))
    txt.replace('YY', meme_data.get('positive_reaction'))
    txt.replace('ZZ', meme_data.get('negative_reaction'))

    next_meme = await sql_games_row_selecter('strikememes', count + 1)
    nmarkup = ReplyKeyboardBuilder()
    if next_meme:
        nmarkup.add(types.KeyboardButton(text='Ещё! 🙂'))
        nmarkup.add(types.KeyboardButton(text='Достаточно ✋'))
    else:
        await state.set_state(PreventStrikeState.after_game)
        nmarkup.row(types.KeyboardButton(text='Продолжим 🙂'))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Достаточно ✋', flags=flags)
async def prevent_strike_sure_memes(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Нет, покажи ещё мем 🙂'))
    nmarkup.row(types.KeyboardButton(text='Да, закончим ✋'))
    await message.answer("Уверены?", reply_markup=nmarkup.as_markup(resize_keyboard=True),
                         disable_web_page_preview=True)


@router.message(F.text == 'Продолжим 🙂', state=PreventStrikeState.after_game, flags=flags)
@router.message(F.text == 'Да, закончим ✋', state=PreventStrikeState.memes, flags=flags)
async def prevent_strike_do_you_agree(message: Message, state: FSMContext):
    await state.set_state(PreventStrikeState.after_game)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_do_you_agree'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Скорее да, это лишь предлог 👌'))
    nmarkup.row(types.KeyboardButton(text='Скорее нет, это настоящая причина 🙅‍♂️'))
    nmarkup.row(types.KeyboardButton(text='Затрудняюсь ответить 🤷‍♀️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Скорее да, это лишь предлог 👌', 'Скорее нет, это настоящая причина 🙅‍♂️',
                            'Затрудняюсь ответить 🤷‍♀️'}), state=PreventStrikeState.after_game, flags=flags)
async def prevent_strike_honesty_time(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='preventive_final_result', value=message.text)

    luca_all = await mongo_count_docs('database', 'statistics_new', {'preventive_final_result': {'$exists': True},
                                                                     'war_aims_ex': welc_message_one[1]})
    luca_yes = await mongo_count_docs('database', 'statistics_new',
                                      {'preventive_final_result': 'Скорее да, это лишь предлог 👌'})
    luca_idk = await mongo_count_docs('database', 'statistics_new',
                                      {'preventive_final_result': 'Скорее нет, это настоящая причина 🙅‍♂️',
                                       'war_aims_ex': welc_message_one[1]})
    luca_no = await mongo_count_docs('database', 'statistics_new',
                                     {'preventive_final_result': 'Затрудняюсь ответить 🤷‍♀️',
                                      'war_aims_ex': welc_message_one[1]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'prevent_strike_honesty_time'}), luca_all)
    txt.replace('AA', luca_yes)
    txt.replace('BB', luca_no)
    txt.replace('CC', luca_idk)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='prevent_strike_fin', value='Да')
    await mongo_update_stat(message.from_user.id, 'prevent_strike')
    await state.set_state(WarGoalsState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
