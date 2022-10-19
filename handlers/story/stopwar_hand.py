import asyncio
import re
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import sql_safe_select, redis_just_one_write, redis_just_one_read, \
    mongo_select_info, mongo_update_end, del_key, poll_write, redis_delete_from_list, poll_get, mongo_count_docs
from filters.MapFilters import FinalPolFiler
from handlers.story.main_menu_hand import mainmenu_really_menu
from handlers.story.mob_hand import mob_lifesaver
from keyboards.map_keys import stopwar_lecture_kb
from log import logg
from middleware.report_ware import Reportware
from states.main_menu_states import MainMenuStates
from states.stopwar_states import StopWarState
from utils.fakes import fake_message
from utilts import simple_media, percentage_replace, ref_master, ref_spy_sender, MasterCommander, CoolPercReplacer, \
    day_counter

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=StopWarState)
router.message.middleware(Reportware())


@router.message((F.text == "Подведём итоги 📊"), flags=flags)
async def new_stopwar_start(message: Message, state: FSMContext):
    await state.set_state(StopWarState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_why_they_sad'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Повторим вопросы 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


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
    nmarkup.row(types.KeyboardButton(text="Не стану этого делать 🕊"))
    nmarkup.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"Начну военную операцию ⚔️", "Не стану этого делать 🕊",
                             "Затрудняюсь ответить 🤷‍♀️"})), state=StopWarState.must_watch, flags=flags)
async def stopwar_here_they_all(message: Message, bot: Bot):
    await mongo_update_stat_new(message.from_user.id, 'stopwar_will_you_start_war', value=message.text)
    first_question = await poll_get(f'Usrs: {message.from_user.id}: StopWar: NewPolitList:')
    if first_question[0] == "Продолжать военную операцию ⚔️" and message.text == "Начну военную операцию ⚔️":
        await redis_just_one_write(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:',
                                   'Сторонник спецоперации ⚔️')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_end',
                                    value='Сторонник спецоперации')
    elif first_question[0] == "Переходить к мирным переговорам 🕊" and message.text == "Не стану этого делать 🕊":
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
    start_warbringers_count = await mongo_count_docs('database', 'statistics_new',
                                                     {'NewPolitStat_start': 'Сторонник спецоперации'})
    start_peacefull_count = await mongo_count_docs('database', 'statistics_new',
                                                   {'NewPolitStat_start': 'Противник войны'})
    start_doubting_count = await mongo_count_docs('database', 'statistics_new',
                                                  {'NewPolitStat_start': 'Сомневающийся'})
    all_count = start_doubting_count + start_peacefull_count + start_warbringers_count
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
    at_the_end = await mongo_count_docs('database', 'statistics_new',
                                        [{'NewPolitStat_start': 'Сторонник спецоперации'},
                                         {'NewPolitStat_end': {'$exists': True}}],
                                        hard_link=True)
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
    at_the_end = await mongo_count_docs('database', 'statistics_new',
                                        [{'NewPolitStat_start': 'Сомневающийся'},
                                         {'NewPolitStat_end': {'$exists': True}}],
                                        hard_link=True)
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
        nmarkup.row(types.KeyboardButton(text="✅ Скорее да, был непредвзят"))
        nmarkup.add(types.KeyboardButton(text="❌ Скорее нет, был предвзят"))
        nmarkup.row(types.KeyboardButton(text="🤷‍♂️ Не знаю"))
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({"✅ Скорее да, был непредвзят", "❌ Скорее нет, был предвзят", "🤷‍♂️ Не знаю"})),
                state=StopWarState.must_watch, flags=flags)
async def stopwar_thanks_for_time(message: Message, bot: Bot, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='CredibleBot', value=message.text)
    await state.set_state(StopWarState.after_new_stat)
    await del_key(f'Usrs: {message.from_user.id}: StopWar: NewPolitList:')
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_thanks_for_time'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что же? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    # ООР
    await MasterCommander(bot, 'chat', message.from_user.id).add({'menu': 'Главное меню'}, check_default_scope=False)
    await mongo_update_end(message.from_user.id)


@router.message(FinalPolFiler(status='Сторонник спецоперации ⚔️'), F.text == "Что же? 🤔", flags=flags)
async def stopwar_stat_lecture_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stat_lecture_war'})
    await message.answer(text, reply_markup=stopwar_lecture_kb(), disable_web_page_preview=True)


@router.message(FinalPolFiler(status='Сомневающийся 🤷'), F.text == "Что же? 🤔", flags=flags)
async def stopwar_idk(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stat_lecture_doub'})
    await message.answer(text, reply_markup=stopwar_lecture_kb(), disable_web_page_preview=True)


@router.message(FinalPolFiler(status='Противник войны 🕊'), F.text == "Что же? 🤔", flags=flags)
async def stopwar_rather_no(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_stat_lecture_peace'})
    await message.answer(text, reply_markup=stopwar_lecture_kb(), disable_web_page_preview=True)


@router.message((F.text == "Ну, допустим, проскакивала мысль, и что? 🤔"), flags=flags)
async def stopwar_front_death(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_front_death'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Ни за что! 🙅‍♂️', "Продолжим 👉"})), state=StopWarState.after_new_stat, flags=flags)
async def stopwar_mob_start(message: Message, state: FSMContext):
    if message.text == 'Ни за что! 🙅‍♂️':
        await message.answer("Рад это слышать!", disable_web_page_preview=True)
    await mob_lifesaver(message, state)


# -- дальше надо будет изменить роутеры на прием сообщений из конца мобилизации

@router.message((F.text == 'ПЕРЕХОД'), state=StopWarState.stopwar_how_and_when, flags=flags)
async def stopwar_how_and_when(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_and_when'})
    await state.set_state(StopWarState.stopwar_how_and_when)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, интересно 👍"))
    nmarkup.add(types.KeyboardButton(text="Нет, давай заканчивать 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Нет, давай заканчивать 👉'), state=StopWarState.stopwar_how_and_when, flags=flags)
async def stopwar_nostradamus(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_nostradamus'})
    await state.set_state(StopWarState.stopwar_nostradamus)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ладно, расскажи 🙂"))
    nmarkup.row(types.KeyboardButton(text="Точно, давай заканчивать 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Точно, давай заканчивать 👉'), state=StopWarState.stopwar_nostradamus, flags=flags)
async def stopwar_buffer_001(message: Message, bot: Bot):
    await message.answer('Хорошо 👌')
    await asyncio.sleep(1)
    await router.parent_router.feed_update(bot, fake_message(message.from_user, "Продолжай ⏳"))


@router.message((F.text.in_({'Да, интересно 👍', 'Ладно, расскажи 🙂'})),
                state=(StopWarState.stopwar_how_and_when, StopWarState.stopwar_nostradamus),
                flags=flags)
async def stopwar_ukraine_will_not_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ukraine_will_not_stop'})
    await state.set_state(StopWarState.stopwar_ukraine_will_not_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой второй тезис?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Какой второй тезис?'), state=StopWarState.stopwar_ukraine_will_not_stop, flags=flags)
async def stopwar_ukraine_at_the_borders(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ukraine_at_the_borders'})
    await state.set_state(StopWarState.stopwar_ukraine_at_the_borders)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да, будет ⚔️"))
    nmarkup.add(types.KeyboardButton(text="Скорее нет, не будет "))
    nmarkup.row(types.KeyboardButton(text="Я не знаю 🤷‍♂️"))
    nmarkup.adjust(2, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(state=StopWarState.stopwar_ukraine_at_the_borders, flags=flags)
async def stopwar_borders_result(message: Message, state: FSMContext):
    await state.set_state(StopWarState.stopwar_borders_result)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='stopwar_borders_result', value=message.text)
    all_answers = await mongo_count_docs('database', 'statistics_new', {'stopwar_borders_result': {'$exists': True}})
    answer_1 = await mongo_count_docs('database', 'statistics_new',
                                      {'stopwar_borders_result': 'Скорее да, будет ⚔️'})
    answer_2 = await mongo_count_docs('database', 'statistics_new',
                                      {'stopwar_borders_result': 'Скорее нет, не будет '})
    answer_3 = await mongo_count_docs('database', 'statistics_new',
                                      {'stopwar_borders_result': 'Я не знаю 🤷‍♂️'})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'stopwar_borders_result'}), all_answers)
    txt.replace('AA', answer_1)
    txt.replace('BB', answer_2)
    txt.replace('CC', answer_3)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Какой вопрос?"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Какой вопрос?'), state=StopWarState.stopwar_borders_result, flags=flags)
async def stopwar_will_it_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_will_it_stop'})
    await state.set_state(StopWarState.stopwar_will_it_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, это закончит войну 🕊"))
    nmarkup.row(types.KeyboardButton(text="Не обязательно, новый президент может продолжить войну 🗡"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Да, это закончит войну 🕊'), state=StopWarState.stopwar_will_it_stop, flags=flags)
async def stopwar_ofc(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ofc'})
    await state.set_state(StopWarState.stopwar_ofc)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Не обязательно, новый президент может продолжить войну 🗡', 'Не знаю 🤷‍♀'})),
                state=StopWarState.stopwar_will_it_stop, flags=flags)
async def stopwar_war_eternal(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_war_eternal'})
    await state.set_state(StopWarState.stopwar_war_eternal)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Продолжим 👌'), state=(StopWarState.stopwar_war_eternal, StopWarState.stopwar_ofc),
                flags=flags)
async def stopwar_clever_bot(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_clever_bot'})
    await state.set_state(StopWarState.stopwar_clever_bot)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Говори! 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Говори! 👌'), state=StopWarState.stopwar_clever_bot, flags=flags)
async def stopwar_putin_will_not_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_putin_will_not_stop'})
    await state.set_state(StopWarState.stopwar_putin_will_not_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Понятно, продолжим 👉"))
    nmarkup.row(types.KeyboardButton(text="Звучит сомнительно 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Звучит сомнительно 🤔'), state=StopWarState.stopwar_putin_will_not_stop, flags=flags)
async def stopwar_putin_already_lost(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_putin_already_lost'})
    await state.set_state(StopWarState.stopwar_putin_already_lost)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FinalPolFiler(status='Сторонник спецоперации ⚔️'),
                (F.text.in_({"Понятно, продолжим 👉", "Продолжай ⏳"})),
                state=(StopWarState.stopwar_nostradamus, StopWarState.stopwar_putin_already_lost,
                       StopWarState.stopwar_putin_will_not_stop), flags=flags)
async def stopwar_warbringer_ending(message: Message, state: FSMContext):
    await state.set_state(StopWarState.stopwar_ending)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_warbringer_ending'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я всё же хочу поговорить о том, как остановить войну 👌"))
    nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
    nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FinalPolFiler(status='Сомневающийся 🤷'),
                (F.text.in_({"Понятно, продолжим 👉", "Продолжай ⏳"})),
                state=(StopWarState.stopwar_nostradamus, StopWarState.stopwar_putin_already_lost,
                       StopWarState.stopwar_putin_will_not_stop), flags=flags)
async def stopwar_doubting_ending(message: Message, state: FSMContext):
    await state.set_state(StopWarState.stopwar_ending)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_doubting_ending'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
    nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(FinalPolFiler(status='Противник войны 🕊'),
                (F.text.in_({"Понятно, продолжим 👉", "Продолжай ⏳"})),
                state=(StopWarState.stopwar_nostradamus, StopWarState.stopwar_putin_already_lost,
                       StopWarState.stopwar_putin_will_not_stop), flags=flags)
async def stopwar_peacemaker_ending(message: Message, state: FSMContext):
    await state.set_state(StopWarState.stopwar_ending)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_peacemaker_ending'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺'),
                state=StopWarState.stopwar_ending, flags=flags)
async def stopwar_putin_already_lost(message: Message, state: FSMContext):
    user_status = await redis_just_one_read(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:')
    nmarkup = ReplyKeyboardBuilder()
    text = "не сработал иф"
    if user_status == "Сторонник спецоперации ⚔️":
        nmarkup.row(types.KeyboardButton(text="Я всё же хочу поговорить о том, как остановить войну 👌"))
        nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
        text = "Заглушка"
    if user_status == "Сомневающийся 🤷":
        nmarkup.row(types.KeyboardButton(text="Давай 👌"))
        nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
        text = "Заглушка"
    if user_status == "Противник войны 🕊":
        nmarkup.row(types.KeyboardButton(text="Давай 👌"))
        text = "Заглушка"
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Пропустить и перейти в главное меню 👇'), state=StopWarState.stopwar_ending, flags=flags)
async def stopwar_time_is_marching(message: Message, bot: Bot, state: FSMContext):
    link = await ref_master(bot, message.from_user.id)
    time = await day_counter(message.from_user)
    text = (await sql_safe_select('text', 'texts', {'name': 'stopwar_time_is_marching'})).replace('[YY:YY]', time)
    text_2 = re.sub('(?<=href\=\")(.*?)(?=\")', link,
                    (await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})))
    await state.set_state(StopWarState.stopwar_time_is_marching)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Перейти в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await message.answer(text_2, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Давай 👌', 'Я всё же хочу поговорить о том, как остановить войну 👌'})),
                state=StopWarState.stopwar_ending, flags=flags)
async def stopwar_big_responsibility(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_big_responsibility'})
    await state.set_state(StopWarState.stopwar_big_responsibility)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Что ты предлагаешь ❓❓❓"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Что ты предлагаешь ❓❓❓'), state=StopWarState.stopwar_big_responsibility, flags=flags)
async def stopwar_save_them(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_save_them'})
    await state.set_state(StopWarState.stopwar_save_them)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="👍"))
    nmarkup.add(types.KeyboardButton(text="👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'👍', '👎'})), state=StopWarState.stopwar_save_them, flags=flags)
async def stopwar_viva_la_resistance(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_viva_la_resistance'})
    await state.set_state(StopWarState.stopwar_viva_la_resistance)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="👍"))
    nmarkup.add(types.KeyboardButton(text="👎"))
    media_id = await sql_safe_select('t_id', 'assets', {'name': "stopwar_viva_la_resistance"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'👍', '👎'})), flags=flags, state=StopWarState.stopwar_viva_la_resistance)
async def stopwar_lets_fight(message: Message, state: FSMContext):
    await state.set_state(StopWarState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Объясни 🤔"))
    nmarkup.row(types.KeyboardButton(text="Нет, власти всё равно будут делать, что хотят 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="🤝"))
    await simple_media(message, 'stopwar_lets_fight', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Объясни 🤔") | (F.text == "Нет, власти всё равно будут делать, что хотят 🙅‍♂️"),
                state=StopWarState.final, flags=flags)
async def stopwar_The(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='will_they_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_The'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие аргументы? 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Какие аргументы? 🤔"), state=StopWarState.final, flags=flags)
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
    nmarkup.row(types.KeyboardButton(text="Да, убедили 👍"))
    nmarkup.row(types.KeyboardButton(text="Нет, не убедили 👎"))
    nmarkup.row(types.KeyboardButton(text="Не знаю 🤷‍♀️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({"Да, убедили 👍", "Нет, не убедили 👎", "Не знаю 🤷‍♀️"}),
                state=StopWarState.arg_3, flags=flags)
async def stopwar_result(message: Message, state: FSMContext):
    await state.set_state(StopWarState.result)
    await mongo_update_stat_new(tg_id=message.from_user.id, column='stopwar_final_result', value=message.text)
    f_all = await mongo_count_docs('database', 'statistics_new', {'stopwar_final_result': {'$exists': True}})
    f_yes = await mongo_count_docs('database', 'statistics_new', {'stopwar_final_result': 'Да, убедили 👍'})
    f_no = await mongo_count_docs('database', 'statistics_new', {'stopwar_final_result': 'Нет, не убедили 👎'})
    f_idk = await mongo_count_docs('database', 'statistics_new', {'stopwar_final_result': 'Не знаю 🤷‍♀️'})
    txt = CoolPercReplacer(await sql_safe_select('text', 'texts', {'name': 'stopwar_result'}), f_all)
    txt.replace('AA', f_yes)
    txt.replace('BB', f_no)
    txt.replace('CC', f_idk)
    await message.answer(txt(), disable_web_page_preview=True)
    await stopwar_pre_timer(message)


@router.message(F.text.contains('🤝'), state=StopWarState.final, flags=flags)
async def stopwar_pre_timer(message: Message):
    text_1 = await sql_safe_select('text', 'texts', {'name': 'stopwar_pre_timer'})
    time = await day_counter(message.from_user)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Получить ссылку 🎉"))
    await message.answer(text_1.replace('[YY:YY]', str(time)), reply_markup=nmarkup.as_markup(resize_keyboard=True),
                         disable_web_page_preview=True)


@router.message((F.text == "Получить ссылку 🎉"), flags=flags)
async def stopwar_timer(message: Message, bot: Bot):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='will_they_stop', value=message.text)
    link = await ref_master(bot, message.from_user.id)
    text_1 = (await sql_safe_select('text', 'texts', {'name': 'stopwar_hello_world'})).replace('[LINK]', link)
    text_2 = re.sub('(?<=href\=\")(.*?)(?=\")', link,
                    (await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})))
    text_3 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_the_message'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие советы? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
    user_info = await mongo_select_info(message.from_user.id)
    if user_info['datetime_end'] is None:
        sec = 299
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
        bot_message = await message.answer('5:00')
        try:
            await message.answer(text_1, disable_web_page_preview=True)
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
        await asyncio.sleep(1)
        await del_key(f"Current_users: {message.from_user.id}")
        await del_key(f'Usrs: {message.from_user.id}: count:')
        textend = await sql_safe_select('text', 'texts', {'name': 'stopwar_end_timer'})
        await message.answer(textend, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                             disable_web_page_preview=True)
        await bot.delete_message(chat_id=message.from_user.id, message_id=m_id)
    else:
        await del_key(f'Usrs: {message.from_user.id}: count:')
        try:
            await message.answer(text_1, disable_web_page_preview=True)
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
        await message.answer(textend, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                             disable_web_page_preview=True)


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
async def main_menu(message: Message, bot: Bot, state: FSMContext):
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
