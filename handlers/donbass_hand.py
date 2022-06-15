import csv

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from DBuse import data_getter, poll_write, sql_safe_select, redis_pop
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll
from filters.All_filters import option_filter

router = Router()
router.message.filter(state=donbass_state)


@router.message(F.text == 'Что главное')
async def donbass_chart_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_chart_1'})
    ph_id = await sql_safe_select('t_id', 'assets', {'name': 'donbass_chart_1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что значит "гражданские"?'))
    nmarkup.add(types.KeyboardButton(text='Да, знал'))
    nmarkup.add(types.KeyboardButton(text='Нет, не знал'))
    nmarkup.adjust(1,2)
    await message.answer_photo(ph_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('значит'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def eight_years_add(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_years_add'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Понятно'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('знал')))
async def donbass_chart_2(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years_selection)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_chart_2'})
    ph_id = await sql_safe_select('t_id', 'assets', {'name': 'donbass_chart_1'})
    await message.answer_photo(ph_id, caption=text)
    await message.reply_poll("Отметьте один или более вариантов, с которыми вы согласны или частично согласны", donbass_first_poll, is_anonymous=False, allows_multiple_answers=True)


@router.poll_answer(state = donbass_state.eight_years_selection)
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state=FSMContext):
    indexes = poll_answer.option_ids
    true_options = list()
    for index in indexes:
        true_options.append(donbass_first_poll[index])
        await poll_write(f'Donbass_polls: First: {poll_answer.user.id}', donbass_first_poll[index])
    if 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше' in true_options:
        text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
        nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
        nmarkup.row(types.KeyboardButton(text="Оба варианта"))
        nmarkup.adjust(2, 1)
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif 'ООН врет, не может быть таких жертв среди гражданского населения' in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'civil_casualties'})
        await redis_pop(f'Donbass_polls: First: {poll_answer.user.id}')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif 'Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко' in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = 'Считать, что люди заслуживают смерти только потому, что у них есть украинский паспорт — и есть нацизм.\n' \
               'В любом случае этот хэндлер будет готов принять любой сценарий, но пока что перейдите к следующей части.'
        await redis_pop(f'Poll_answers: Donbas: {poll_answer.user.id}')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'only_war_objects'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
        nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
        nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
    elif 'Так они используют население как живой щит! Поэтому погибают мирные жители' in true_options:
        text = 'Еще одна заглушка. Блок про живой щит начинается здесь'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
    elif 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = await sql_safe_select('text', 'texts', {'name': 'war_beginning'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="Тут другое дело! Мы шли освобождать их от неонацистов, захвативших власть."))
        nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
        nmarkup.row(types.KeyboardButton(
            text="Не согласен, в случае нападения на Россию пусть лучше солдаты сложат оружие, зато не будет жертв."))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
    elif 'Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны' in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'reasons_here'})
        data = await state.get_data()
        reason_list = data.values()
        reason_text = ''
        for reason in reason_list:
            reason_text = reason_text + '- ' + reason + '\n'
        text = text + '\n\n' + reason_text + '\n\nОбязательно их все обсудим, а пока что вернемся к теме Донбасса'
        await redis_pop(f'Poll_answers: Donbas: {poll_answer.user.id}')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    await state.set_state(donbass_state.after_poll)


@router.message(option_filter(option = 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше'), (F.text == 'Договорились') | (F.text == 'Хорошо')| (F.text == 'Понятно'))
async def preventive_strike(message: Message, state=FSMContext):
    text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
    nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
    nmarkup.row(types.KeyboardButton(text="Оба варианта"))
    nmarkup.adjust(2,1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('ДНР/ЛНР') | (F.text.contains('НАТО')) | (F.text.contains('Оба'))))
async def donbas_reason_to_war(message: Message, state=FSMContext):
    reason = str
    if message.text == "...на ДНР/ЛНР и Крым":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и Крым'
    if message.text == "...вместе с НАТО на Россию":
        reason = 'Если бы мы не напали первыми, то Украина бы напала вместе с НАТО на Россию'
    if message.text == "Оба варианта":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и вместе с НАТО на Россию'
    await state.update_data(war_reasons = reason)
    await redis_pop(f'Poll_answers: Donbas: {message.from_user.id}')
    text = await sql_safe_select('text', 'texts', {'name': 'reason_to_war'})
    video_id = await sql_safe_select('t_id', 'assets', {'name': 'putin_may'})
    await message.answer_video(video_id, caption=text, reply_markup=filler_kb())


