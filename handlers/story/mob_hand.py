from aiogram import Router, F, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, PollAnswer
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import sql_safe_select, mongo_count_docs
from resources.all_polls import mob_city, mob_wot_mvps_poll, mob_is_he_insane_poll, mob_laws_lol_poll, \
    mob_street_fighter_poll, mob_why_he_did_it_poll
from states.mob_states import MobState
from utilts import CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=MobState)
router.poll_answer.filter(state=MobState)

@router.message(commands=['mob'], state='*', flags=flags)
async def mob_lifesaver(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'mob_lifesaver'})
    await state.set_state(MobState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Начнём! 🪖"))
    nmarkup.row(KeyboardButton(text="Не стоит, мне это не интересно 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Не стоит, мне это не интересно 👉", state=MobState.main, flags=flags)
async def mob_how_to_avoid(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'mob_how_to_avoid'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Хорошо, спасём Вовочку! 🪖"))
    nmarkup.row(KeyboardButton(text="Всё равно продолжить 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Начнём! 🪖', 'Хорошо, спасём Вовочку! 🪖'}), state=MobState.main, flags=flags)
async def mob_save_vv_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.city_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_save_vv_start'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Где безопаснее?', mob_city, is_anonymous=False,
                        type='quiz', correct_option_id=0)


@router.poll_answer(MobState.city_poll)
async def mob_size_matters(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.nazi_poll)
    answer = mob_city[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_city_poll', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': {'$exists': True}})
    c_city = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': mob_city[0]})
    c_village = await mongo_count_docs('database', 'statistics_new', {'mob_city_poll': mob_city[1]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_size_matters'}), c_all)
    txt.replace('AA', c_city)
    txt.replace('BB', c_village)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Понятно 👌"))
    await bot.send_message(poll_answer.user.id, txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message(F.text.in_({'Понятно 👌'}), state=MobState.nazi_poll, flags=flags)
async def mob_wot_mvps(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_wot_mvps)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_wot_mvps'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Кто в большей безопасности от мобилизации?', mob_wot_mvps_poll, is_anonymous=False,
                        type='quiz', correct_option_id=0)


@router.poll_answer(MobState.mob_wot_mvps)
async def mob_nazi_is_here(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_nazi_is_here)
    answer = mob_wot_mvps_poll[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_nazi_is_here', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_nazi_is_here': {'$exists': True}})
    c_vova = await mongo_count_docs('database', 'statistics_new', {'mob_nazi_is_here': mob_wot_mvps_poll[0]})
    c_aisen = await mongo_count_docs('database', 'statistics_new', {'mob_nazi_is_here': mob_wot_mvps_poll[1]})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_nazi_is_here'}), c_all)
    txt.replace('AA', c_vova)
    txt.replace('BB', c_aisen)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Продолжим 👌"))
    await bot.send_message(poll_answer.user.id, txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Продолжим 👌'}), state=MobState.mob_nazi_is_here, flags=flags)
async def mob_is_he_insane(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_is_he_insane)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_is_he_insane'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'В каком случае?', mob_is_he_insane_poll, is_anonymous=False,
                        type='quiz', correct_option_id=3)


@router.poll_answer(MobState.mob_is_he_insane)
async def mob_only_to_lit(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_only_to_lit)
    answer = mob_is_he_insane_poll[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_only_to_lit', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_only_to_lit': {'$exists': True}})
    c_right = await mongo_count_docs('database', 'statistics_new', {'mob_only_to_lit': mob_is_he_insane_poll[3]})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_only_to_lit'}), c_all)
    txt.replace('XX', c_right)
    txt.replace('YY', (100-c_right))
    media_id=await sql_safe_select('t_id', 'assets', {'name': 'mob_only_to_lit'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Хорошо, запомнили и закрепили — не ходить в военкомат 👌"))
    try:
        await bot.send_video(poll_answer.user.id,video=media_id,caption=txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except Exception:
        await bot.send_message(poll_answer.user.id, f'Здесь будет видео: Звонок от человека, который сам пришёл в военкомат\n\n\n{txt()}',
                               reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message(F.text.in_({'Хорошо, запомнили и закрепили — не ходить в военкомат 👌'}), state=MobState.mob_only_to_lit, flags=flags)
async def mob_laws_lol(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_laws_lol)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_laws_lol'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Каким образом вручённая повестка имеет юридическую силу?', mob_laws_lol_poll, is_anonymous=False,
                        type='quiz', correct_option_id=3)


@router.poll_answer(MobState.mob_laws_lol)
async def mob_ignore_it_go_away(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_ignore_it_go_away)
    answer = mob_laws_lol_poll[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_ignore_it_go_away', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_ignore_it_go_away': {'$exists': True}})
    c_right = await mongo_count_docs('database', 'statistics_new', {'mob_ignore_it_go_away': mob_laws_lol_poll[3]})

    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_ignore_it_go_away'}), c_all)
    txt.replace('XX', c_right)
    txt.replace('YY', (100-c_right))

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Понятно 👌"))
    await bot.send_message(poll_answer.user.id, txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Понятно 👌'}), state=MobState.mob_ignore_it_go_away, flags=flags)
async def mob_they_coming_for_you(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_they_coming_for_you)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_they_coming_for_you'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Понятно, дверь незнакомцам не открываем 👌"))
    await message.answer(text, disable_web_page_preview=True,reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(F.text.in_({'Понятно 👌'}), state=MobState.mob_they_coming_for_you, flags=flags)
async def mob_street_fighter(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_street_fighter)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_street_fighter'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Что делать?',
                        mob_street_fighter_poll, is_anonymous=False,
                        type='regular')

@router.poll_answer(MobState.mob_street_fighter)
async def mob_bad_ingrish(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_bad_ingrish)
    answer = mob_street_fighter_poll[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_bad_ingrish', answer)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_bad_ingrish'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Понятно 👌"))
    nmarkup.row(KeyboardButton(text="А не лучше просто обходить стороной людей в форме? 🤔"))
    await bot.send_message(poll_answer.user.id, text,
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message(state=MobState.mob_bad_ingrish, flags=flags)
async def mob_rules_of_nature(message: Message, state: FSMContext):
    await state.set_state(MobState.mob_rules_of_nature)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_bad_ingrish'})
    media_id = await sql_safe_select('t_id', 'assets', {'name': 'mob_bad_ingrish'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Да, обсудим, что делать Вовочке, если он официально трудоустроен 👌"))
    nmarkup.row(KeyboardButton(text="Нет, пропустим это 👉"))
    if message.text=="А не лучше просто обходить стороной людей в форме? 🤔":
        await message.answer('Правильно мыслите! 😉')
    try:
        await message.answer_photo(photo=media_id,caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except Exception:
        await message.answer(f'Здесь будет фото:Не брать повестку! Не ходить в военкомат!\n\n\n{text}', reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(F.text.in_({'Да, обсудим, что делать Вовочке, если он официально трудоустроен 👌'}), state=MobState.mob_rules_of_nature, flags=flags)
async def mob_working_class(message: Message, bot: Bot, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'mob_working_class'})
    await message.answer(text, disable_web_page_preview=True)
    await mob_why_he_did_it(message,bot,state)

@router.message(F.text.in_({'Нет, пропустим это 👉'}), state=MobState.mob_rules_of_nature, flags=flags)
async def mob_why_he_did_it(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MobState.mob_why_he_did_it)
    text = await sql_safe_select('text', 'texts', {'name': 'mob_why_he_did_it'})
    await message.answer(text, disable_web_page_preview=True)
    await bot.send_poll(message.from_user.id, 'Что его ждёт, если не пойти в военкомат?',
                        mob_why_he_did_it_poll, is_anonymous=False,
                        type='quiz', correct_option_id=2)


@router.poll_answer(MobState.mob_why_he_did_it)
async def mob_still_ignore_it(poll_answer: PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(MobState.voenkomat_poll)
    answer = mob_why_he_did_it_poll[poll_answer.option_ids[0]]
    await mongo_update_stat_new(poll_answer.user.id, 'mob_still_ignore_it', answer)

    c_all = await mongo_count_docs('database', 'statistics_new', {'mob_still_ignore_it': {'$exists': True}})
    c_right = await mongo_count_docs('database', 'statistics_new', {'mob_still_ignore_it': mob_why_he_did_it_poll[2]})
    c_wrong_1 = await mongo_count_docs('database', 'statistics_new', {'mob_still_ignore_it': mob_why_he_did_it_poll[0]})
    c_wrong_2 = await mongo_count_docs('database', 'statistics_new', {'mob_still_ignore_it': mob_why_he_did_it_poll[1]})


    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'mob_still_ignore_it'}), c_all)
    media_id = await sql_safe_select('t_id', 'assets', {'name': 'mob_still_ignore_it'})
    txt.replace('AA', c_wrong_1)
    txt.replace('BB', c_wrong_2)
    txt.replace('CC', c_right)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(KeyboardButton(text="Понятно 👌"))
    try:
        await bot.send_video(poll_answer.user.id,video=media_id,caption=txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except Exception:
        await bot.send_message(poll_answer.user.id,f'Зесь будет видео:[Максим Кац: не ходите в военкомат!]\n\n\n {txt()}',
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)