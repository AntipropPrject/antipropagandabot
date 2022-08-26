import asyncio
import re
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import sql_safe_select, redis_just_one_write, redis_just_one_read, \
    mongo_select_info, mongo_update_end, del_key, poll_write, redis_delete_from_list, poll_get, mongo_count_docs, \
    mongo_ez_find_one
from handlers.story.main_menu_hand import mainmenu_really_menu
from log import logg
from states.main_menu_states import MainMenuStates
from utilts import simple_media, percentage_replace, ref_master, ref_spy_sender


class StopWarState(StatesGroup):
    main = State()
    questions = State()
    must_watch = State()
    next_1 = State()
    war_1 = State()
    arg_1 = State()
    arg_2 = State()
    arg_3 = State()


flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=StopWarState)


@router.message(F.text == "Повторим вопросы 👌", flags=flags)
async def stopwar_question_1(message: Message, state: FSMContext):
    await state.set_state(StopWarState.questions)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_question_1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжать военную операцию ⚔️"))
    nmarkup.row(types.KeyboardButton(text="Переходить к мирным переговорам 🕊"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Продолжать военную операцию ⚔️", "Переходить к мирным переговорам 🕊",
                             "Затрудняюсь ответить 🤷‍♀️"})), state=StopWarState.questions, flags=flags)
async def stopwar_question_2(message: Message, state: FSMContext):
    await state.set_state(StopWarState.must_watch)
    await poll_write(f'Usrs: {message.from_user.id}: StopWar: NewPolitList:', message.text)
    await mongo_update_stat_new(message.from_user.id, 'stopwar_continue_or_peace_results', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_question_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начну военную операцию ⚔️"))
    nmarkup.row(types.KeyboardButton(text="Не стану этого делать 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Начну военную операцию ⚔️", "Не стану этого делать 🙅‍♂️",
                             "Затрудняюсь ответить 🤷‍♀️"})), state=StopWarState.must_watch, flags=flags)
async def stopwar_here_they_all(message: Message, bot: Bot):
    await mongo_update_stat_new(message.from_user.id, 'stopwar_will_you_start_war', value=message.text)
    first_question = await poll_get(f'Usrs: {message.from_user.id}: StopWar: NewPolitList:')
    if first_question[0] == "Продолжать военную операцию ⚔️" and message.text == "Начну военную операцию ⚔️":
        await redis_just_one_write(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:',
                                   'Сторонник спецоперации ⚔️')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_end',
                                    value='Сторонник спецоперации')
    elif first_question[0] == "Переходить к мирным переговорам 🕊" and message.text == "Не стану этого делать 🙅‍♂️":
        await redis_just_one_write(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:',
                                   'Противник войны 🕊')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_end',
                                    value='Противник войны')
    else:
        await redis_just_one_write(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:',
                                   'Сомневающийся 🤷')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_end',
                                    value='Сомневающийся')

    if await redis_just_one_read(f'Usrs: {message.from_user.id}: Ref'):
        parent_text = await sql_safe_select('text', 'texts', {'name': 'ref_end_polit'})
        start_answer = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:')
        await ref_spy_sender(bot, message.from_user.id, parent_text,
                             {'[first_q_start]': start_answer[0], '[second_q_start]': start_answer[1],
                              '[first_q_end]': first_question[0], '[second_q_end]': message.text})

    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_here_they_all'})
    start_staus = await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:')
    end_status = await redis_just_one_read(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:')
    text = text.replace('[начальный политический статус]', str(start_staus))
    text = text.replace('[конечный политический статус]', str(end_status))
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Взглянем на результаты 📊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Взглянем на результаты 📊", state=StopWarState.must_watch, flags=flags)
async def stopwar_how_it_was(message: Message, state: FSMContext):
    for x in ('War', 'Peace', 'Doubt'):
        await poll_write(f'Usrs: {message.from_user.id}: Stop_war_answers:', x)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_it_was'})
    await mongo_update_stat_new(message.from_user.id, 'SecondNewPolit')
    client = all_data().get_mongo()
    database = client.database
    collection = database['statistics_new']

    start_warbringers_count = await mongo_count_docs('database', 'statistics_new',
                                                     {'NewPolitStat_start': 'Сторонник спецоперации'})
    start_peacefull_count = await mongo_count_docs('database', 'statistics_new',
                                                   {'NewPolitStat_start': 'Противник войны'})
    start_doubting_count = await mongo_count_docs('database', 'statistics_new',
                                                  {'NewPolitStat_start': 'Сомневающийся'})
    all_count = start_doubting_count + start_peacefull_count + start_warbringers_count
    print(start_warbringers_count, start_peacefull_count, start_doubting_count, all_count)
    start_war_percentage = str(round(start_warbringers_count / all_count * 100))
    start_peace_percentage = str(round(start_peacefull_count / all_count * 100))
    start_doubt_percentage = str(round(start_doubting_count / all_count * 100))
    text = text.replace('XX', start_war_percentage)
    text = text.replace('YY', start_peace_percentage)
    text = text.replace('ZZ', start_doubt_percentage)
    all_count_end = await mongo_count_docs('database', 'statistics_new', [
        {'NewPolitStat_end': 'Сомневающийся'}, {'NewPolitStat_end': 'Сторонник спецоперации'},
        {'NewPolitStat_end': 'Противник войны'}])
    await state.update_data({'How_many_will_end': all_count_end, 'start_warbringers_count': start_warbringers_count,
                             'start_peacefull_count': start_peacefull_count,
                             'start_doubting_count': start_doubting_count})

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Сторонники спецоперации ⚔️"))
    nmarkup.add(types.KeyboardButton(text="Сомневающиеся 🤷"))
    nmarkup.add(types.KeyboardButton(text="Противники войны 🕊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Сторонники спецоперации ⚔️", state=StopWarState.must_watch, flags=flags)
async def stopwar_how_was_warbringers(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_was_warbringers'})
    at_the_end = await mongo_count_docs('database', 'statistics_new', [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                                                       {'SecondNewPolit': True}], hard_link=True)
    start_war = (await state.get_data())['start_warbringers_count']
    end_war_war = await mongo_count_docs('database', 'statistics_new',
                                         [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                          {'NewPolitStat_end': 'Сторонник спецоперации'}], hard_link=True)
    end_war_peace = await mongo_count_docs('database', 'statistics_new',
                                           [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                            {'NewPolitStat_end': 'Противник войны'}], hard_link=True)
    end_war_doubt = await mongo_count_docs('database', 'statistics_new',

                                           [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                            {'NewPolitStat_end': 'Сомневающийся'}], hard_link=True)

                                         [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                          {'NewPolitStat_end': 'Сомневающийся'}], hard_link=True)
    print(start_war, at_the_end, end_war_war, end_war_doubt, end_war_peace)

    text = percentage_replace(text, 'MM', at_the_end, start_war)
    text = percentage_replace(text, 'AA', end_war_war, at_the_end)
    text = percentage_replace(text, 'BB', end_war_doubt, at_the_end)
    text = percentage_replace(text, 'CC', end_war_peace, at_the_end)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Stop_war_answers:', 'War')
    await message.answer(text)
    await stopwar_must_watch_all(message)


@router.message(F.text == "Сомневающиеся 🤷", state=StopWarState.must_watch, flags=flags)
async def stopwar_how_was_doubting(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_was_doubting'})
    at_the_end = await mongo_count_docs('database', 'statistics_new', [{'NewPolitStat_start': 'Сомневающийся'},
                                                                       {'SecondNewPolit': True}], hard_link=True)
    start_doub = (await state.get_data())['start_doubting_count']
    end_doub_war = await mongo_count_docs('database', 'statistics_new',
                                          [{'NewPolitStat_start': 'Сомневающийся'},
                                           {'NewPolitStat_end': 'Сторонник спецоперации'}], hard_link=True)
    end_doub_doub = await mongo_count_docs('database', 'statistics_new',
                                           [{'NewPolitStat_start': 'Сомневающийся'},
                                            {'NewPolitStat_end': 'Сомневающийся'}], hard_link=True)
    end_doub_peace = await mongo_count_docs('database', 'statistics_new',

                                            [{'NewPolitStat_start': 'Сомневающийся'},
                                             {'NewPolitStat_end': 'Противник войны'}], hard_link=True)

                                           [{'NewPolitStat_start': 'Сомневающийся'},
                                            {'NewPolitStat_end': 'Противник войны'}], hard_link=True)

    text = percentage_replace(text, 'NN', at_the_end, start_doub)
    text = percentage_replace(text, 'DD', end_doub_war, at_the_end)
    text = percentage_replace(text, 'EE', end_doub_doub, at_the_end)
    text = percentage_replace(text, 'FF', end_doub_peace, at_the_end)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Stop_war_answers:', 'Doubt')
    await message.answer(text)
    await stopwar_must_watch_all(message)


@router.message(F.text == "Противники войны 🕊", state=StopWarState.must_watch, flags=flags)
async def stopwar_how_was_peacefull(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_was_peacefull'})

    at_the_end = await mongo_count_docs('database', 'statistics_new',
                                        [{'NewPolitStat_start': 'Противник войны'},
                                         {'NewPolitStat_end': {'$exists': True}}],
                                        hard_link=True)

    at_the_end = await mongo_count_docs('database', 'statistics_new', [{'NewPolitStat_start': 'Противник войны'},
                                        {'SecondNewPolit': True}], hard_link=True)

    start_peace = (await state.get_data())['start_peacefull_count']
    end_peace_war = await mongo_count_docs('database', 'statistics_new',
                                           [{'NewPolitStat_start': 'Противник войны'},
                                            {'NewPolitStat_end': 'Сторонник спецоперации'}], hard_link=True)
    end_peace_doub = await mongo_count_docs('database', 'statistics_new',
                                            [{'NewPolitStat_start': 'Противник войны'},
                                             {'NewPolitStat_end': 'Сомневающийся'}], hard_link=True)
    end_peace_peace = await mongo_count_docs('database', 'statistics_new',

                                             [{'NewPolitStat_start': 'Противник войны'},
                                              {'NewPolitStat_end': 'Противник войны'}], hard_link=True)

                                           [{'NewPolitStat_start': 'Противник войны'},
                                            {'NewPolitStat_end': 'Противник войны'}], hard_link=True)

    text = percentage_replace(text, 'OO', at_the_end, start_peace)
    text = percentage_replace(text, 'GG', end_peace_war, at_the_end)
    text = percentage_replace(text, 'HH', end_peace_doub, at_the_end)
    text = percentage_replace(text, 'II', end_peace_peace, at_the_end)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Stop_war_answers:', 'Peace')
    await message.answer(text)
    await stopwar_must_watch_all(message)


async def stopwar_must_watch_all(message: Message):
    not_watched = await poll_get(f'Usrs: {message.from_user.id}: Stop_war_answers:')
    nmarkup = ReplyKeyboardBuilder()
    if not_watched:
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_must_watch_all'})
        if 'War' in not_watched:
            nmarkup.row(types.KeyboardButton(text="Сторонники спецоперации ⚔️"))
        if 'Doubt' in not_watched:
            nmarkup.add(types.KeyboardButton(text="Сомневающиеся 🤷"))
        if 'Peace' in not_watched:
            nmarkup.add(types.KeyboardButton(text="Противники войны 🕊"))
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    else:
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_plastic_views'})
        nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Продолжай ⏳", state=StopWarState.must_watch, flags=flags)
async def stopwar_old_start(message: Message, state: FSMContext):
    await state.set_state(StopWarState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_old_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да ✅"))
    nmarkup.add(types.KeyboardButton(text="Скорее нет ❌"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Скорее да ✅", flags=flags)
async def stopwar_rather_yes(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='is_putin_ready_to_stop', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    await simple_media(message, 'stopwar_rather_yes', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Не знаю 🤷‍♂️", flags=flags)
async def stopwar_idk(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='is_putin_ready_to_stop', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    await simple_media(message, 'stopwar_idk', nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Скорее нет ❌", flags=flags)
async def stopwar_rather_no(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='is_putin_ready_to_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_no'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не согласен(а) 🙅") | (F.text == "Согласен(а) 👌") | (F.text == "Продолжим 👌"),
                flags=flags)
async def stopwar_will_it_stop(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_will_it_stop'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, это закончит войну 🕊"))
    nmarkup.row(types.KeyboardButton(text="Не обязательно, новый президент может продолжить войну 🗡"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, это закончит войну 🕊"), flags=flags)
async def stopwar_ofc(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='no_putin_will_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ofc'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Не знаю 🤷‍♀️") | (F.text == "Не обязательно, новый президент может продолжить войну 🗡"),
                flags=flags)
async def stopwar_war_eternal(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='no_putin_will_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_war_eternal'})
    await state.set_state(StopWarState.war_1)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=StopWarState.war_1, flags=flags)
async def stopwar_isolation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_isolation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжим👌"), flags=flags)
async def stopwar_stop_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stop_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В результате выборов 📊"))
    nmarkup.row(types.KeyboardButton(text="По иным причинам 💀"))
    nmarkup.row(types.KeyboardButton(text="Сложно сказать 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "В результате выборов 📊") | (F.text == "Сложно сказать 🤔"), flags=flags)
async def stopwar_stolen_votes(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='how_putin_ends', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stolen_votes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "По иным причинам 💀"), flags=flags)
async def stopwar_just_a_scene(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='how_putin_ends', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_just_a_scene'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А что главное?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(commands=['end'], flags=flags)
@router.message((F.text == "А что главное?"), flags=flags)
async def stopwar_end_it_now(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_it_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что ты предлагаешь ❓ ❓ ❓"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Что ты предлагаешь ❓ ❓ ❓"), flags=flags)
async def stopwar_lets_fight(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Объясни 🤔"))
    nmarkup.row(types.KeyboardButton(text="Нет, власти всё равно будут делать, что хотят 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Да, согласен(а), это остановит войну 🕊"))
    await simple_media(message, 'stopwar_lets_fight', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Объясни 🤔") | (F.text == "Нет, власти всё равно будут делать, что хотят 🙅‍♂️"),
                flags=flags)
async def stopwar_The(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='will_they_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_The'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие аргументы? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Какие аргументы? 🤔"), flags=flags)
async def stopwar_first_manipulation_argument(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_first_manipulation_argument'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Следующий аргумент 👉"))
    await state.set_state(StopWarState.arg_1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Следующий аргумент 👉"), state=StopWarState.arg_1, flags=flags)
async def stopwar_second_manipulation_argument(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_second_manipulation_argument'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Следующий аргумент 👉"))
    await state.set_state(StopWarState.arg_2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Следующий аргумент 👉"), state=StopWarState.arg_2, flags=flags)
async def stopwar_third_manipulation_argument(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_third_manipulation_argument'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Следующий аргумент 👉"))
    await state.set_state(StopWarState.arg_3)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Следующий аргумент 👉"), state=StopWarState.arg_3, flags=flags)
async def stopwar_fourth_manipulation_argument(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_fourth_manipulation_argument'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(
        types.KeyboardButton(text="Это разумные аргументы. Важно, чтобы россияне поняли — война им не нужна 🕊"))
    nmarkup.row(types.KeyboardButton(text="Перевороты и революция — это страшно и я не хочу этого 💔"))
    nmarkup.row(types.KeyboardButton(text="Я так и знал(а). Правдобот, ты — проект США 🇺🇸 и хочешь развалить Россию"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Перевороты и революция — это страшно и я не хочу этого 💔"), flags=flags)
async def stopwar_I_understand_you_fear(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='after_argum', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_I_understand_you_fear'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await state.set_state(StopWarState.next_1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=StopWarState.next_1, flags=flags)
async def stopwar_like_this_in_a_revolution(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_like_this_in_a_revolution'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), важно, чтобы россияне поняли — война им не нужна 🕊"))
    nmarkup.row(types.KeyboardButton(text="Ну не знаю... 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Я так и знал(а). Правдобот, ты — проект США 🇺🇸 и хочешь развалить Россию"), flags=flags)
async def stopwar_made_a_big_team(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='after_argum', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_made_a_big_team'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да нет, я согласен(а), важно, чтобы россияне поняли — война им не нужна 🕊"))
    nmarkup.row(types.KeyboardButton(text="Да, закончим разговор, прощай! 🖕"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, закончим разговор, прощай! 🖕"), flags=flags)
async def stopwar_I_told_you_everything(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_I_told_you_everything'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я передумал(а). Важно, чтобы россияне поняли — война им не нужна 🕊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains('Я передумал(а). Важно, чтобы россияне поняли — война им не нужна 🕊')) |
                 (F.text.contains('Да, согласен(а), это остановит войну 🕊')) |
                 (F.text.contains('Да нет, я согласен(а), важно, чтобы россияне поняли — война им не нужна 🕊')) |
                 (F.text.contains('Ну не знаю... 🤷‍♀️')) |
                 (F.text.contains('Это разумные аргументы. Важно, чтобы россияне поняли — война им не нужна 🕊')) |
                 (F.text.contains('Согласен(а), важно, чтобы россияне поняли — война им не нужна 🕊'))), flags=flags)
async def stopwar_timer(message: Message, bot: Bot):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='will_they_stop', value=message.text)
    text_1 = await sql_safe_select('text', 'texts', {'name': 'stopwar_hello_world'})
    link = await ref_master(bot, message.from_user.id)
    text_2 = re.sub('(?<=href\=\")(.*?)(?=\")', link,
                    (await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})))
    text_3 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_the_message'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие советы? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
    user_info = await mongo_select_info(message.from_user.id)
    date_start = user_info['datetime'].replace('_', ' ')
    usertime = datetime.strptime(date_start, "%d-%m-%Y %H:%M")
    time_bot = datetime.strptime(datetime.strftime(datetime.now(), "%d-%m-%Y %H:%M"), "%d-%m-%Y %H:%M") - usertime
    str_date = str(time_bot)[:-3].replace('days', '').replace("day", '')
    if int(time_bot.days) == 1:
        days_pr = 'день,'
    elif 1 <= int(time_bot.days) <= 4:
        days_pr = 'дня,'
    else:
        days_pr = 'дней,'
    act_time = str_date.replace(',', days_pr)
    if user_info['datetime_end'] is None:  # c is не работает так как объект находится не в озу а в базе
        sec = 299
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
        bot_message = await message.answer('5:00')
        try:
            await message.answer(text_1.replace('[YY:YY]', act_time), disable_web_page_preview=True)
            await message.answer(text_2, disable_web_page_preview=True)
            await message.answer(text_3, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                                 disable_web_page_preview=True)
        except Exception as er:
            await logg.get_error(er)
        m_id = bot_message.message_id
        await bot.pin_chat_message(chat_id=message.from_user.id, message_id=m_id, disable_notification=True)
        await mongo_update_stat_new(tg_id=message.from_user.id, column='timer', value='Да')
        await redis_just_one_write(f'Usrs: {message.from_user.id}: count:', '1')
        while sec:
            m, s = divmod(sec, 60)
            sec_t = '{:02d}:{:02d}'.format(m, s)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=m_id, text=f'{sec_t}')
            await asyncio.sleep(1)
            sec -= 1
        await mongo_update_stat(message.from_user.id, 'end')
        await mongo_update_end(message.from_user.id)
        await asyncio.sleep(1)
        await del_key(f'Usrs: {message.from_user.id}: count:')
        textend = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_timer'})
        await message.answer(textend, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
        await bot.delete_message(chat_id=message.from_user.id, message_id=m_id)
        print('Countdown finished.')
    else:
        await del_key(f'Usrs: {message.from_user.id}: count:')
        try:
            await message.answer(text_1.replace('[YY:YY]', act_time), disable_web_page_preview=True)
            await message.answer(text_2, disable_web_page_preview=True)
            await message.answer(text_3, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                                 disable_web_page_preview=True)
        except Exception as er:
            await logg.get_error(er)


@router.message((F.text == "Какие советы? 🤔"), flags=flags)
async def stopwar_share_blindly(message: Message):
    timer = await redis_just_one_read(f'Usrs: {message.from_user.id}: count:')
    if timer == '1':
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_share_blindly'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Покажи инструкцию, как поделиться со всем списком контактов 📝"))
        nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
        textend = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_timer'})
        await message.answer(textend, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Покажи инструкцию, как поделиться со всем списком контактов 📝"), flags=flags)
async def stopwar_bulk_forwarding(message: Message):
    timer = await redis_just_one_read(f'Usrs: {message.from_user.id}: count:')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
    if timer == '1':
        await simple_media(message, 'stopwar_bulk_forwarding', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        textend = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_timer'})
        await message.answer(textend, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Перейти в главное меню 👇"), flags=flags)
async def main_menu(message: Message, state: FSMContext):
    timer = await redis_just_one_read(f'Usrs: {message.from_user.id}: count:')
    if timer == '1':
        await message.answer('Пожалуйста, дождитесь окончания таймера,'
                             ' прежде, чем попасть в главное меню. Не теряйте'
                             ' это время зря — поделитесь мной со своими родственниками,'
                             ' друзьями и знакомыми! 🙏')
    else:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='main_menu', value='Да')
        await state.set_state(MainMenuStates.main)
        await mainmenu_really_menu(message, state)
