import asyncio
import pathlib

from psycopg2 import sql
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message, PollAnswer
from bata import all_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from states.donbass_states import donbass_state
from DBuse import data_getter, poll_get, poll_write, redis_pop
from keyboards.main_keys import filler_kb

router = Router()
router.message.filter(state = (donbass_state.eight_years, donbass_state.eight_years_selection))

@router.message(text_contains=('значит'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    text = data_getter("SELECT text from public.texts WHERE name = 'donbas_years_add';")[0][0]
    await message.answer(text)

@router.message(text_contains=('знал'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    photo_id = data_getter("SELECT t_id from public.assets WHERE name = 'donbass_chart_2';")[0][0]
    text = data_getter("SELECT text from public.texts WHERE name = 'donbas_years_select';")[0][0]
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Получить опрос"))
    await message.answer_photo(photo_id, caption=text, parse_mode="HTML", reply_markup=nmarkup.as_markup(resize_keyboard=True, input_field_placeholder="В истории много странностей, не находите?"))


@router.message(text_contains=('опрос'), content_types=types.ContentType.TEXT, text_ignore_case=True, state = donbass_state.eight_years)
async def eight_years_add_point(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years_selection)
    options = await poll_get('Donbas: Poll_answers: Base')
    await message.reply_poll("Отметьте один или более вариантов, с которыми вы согласны или частично согласны", options, is_anonymous=False, allows_multiple_answers=True)


@router.poll_answer(state = donbass_state.eight_years_selection)
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    base_options = await poll_get('Donbas: Poll_answers: Base')
    indexes = poll_answer.option_ids
    print (indexes)
    true_options = list()
    for index in indexes:
        true_options.append(base_options[index])
    for true_option in true_options:
        await poll_write(poll_answer.user.id, 'Donbas', true_option)
    if 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше' in true_options:
        text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
        nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
        nmarkup.row(types.KeyboardButton(text="Оба варианта"))
        nmarkup.adjust(2, 1)
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
        await state.set_state(donbass_state.after_poll)
        return
    if 'ООН врет, не может быть таких жертв среди гражданского населения' in true_options:
        text = data_getter("SELECT text from public.texts WHERE name = 'civil_casualties';")[0][0]
        await redis_pop(f'Poll_answers: Donbas: {poll_answer.user.id}')
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    if 'Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко' in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = 'Считать, что люди заслуживают смерти только потому, что у них есть украинский паспорт — и есть нацизм.\n' \
               'В любом случае этот хэндлер будет готов принять любой сценарий, но пока что перейдите к следующей части.'
        await redis_pop(f'Poll_answers: Donbas: {poll_answer.user.id}')
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    if 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
        text = data_getter("SELECT text from public.texts WHERE name = 'only_war_objects';")[0][0]
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
        nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
        nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    if 'Так они используют население как живой щит! Поэтому погибают мирные жители' in true_options:
        text = 'Еще одна заглушка. Блок про живой щит начинается здесь'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    if 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = data_getter("SELECT text from public.texts WHERE name = 'war_beginning';")[0][0]
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="Тут другое дело! Мы шли освобождать их от неонацистов, захвативших власть."))
        nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
        nmarkup.row(types.KeyboardButton(
            text="Не согласен, в случае нападения на Россию пусть лучше солдаты сложат оружие, зато не будет жертв."))
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    if 'Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны' in true_options:
        text = data_getter("SELECT text from public.texts WHERE name = 'reasons_here';")[0][0]
        data = await state.get_data()
        reason_list = data.values()
        reason_text = ''
        for reason in reason_list:
            reason_text = reason_text + '- ' + reason + '\n'
        text = text + '\n\n' + reason_text + '\n\nОбязательно их все обсудим, а пока что вернемся к теме Донбасса'
        await redis_pop(f'Poll_answers: Donbas: {poll_answer.user.id}')
        await Bot(all_data().bot_token).send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
        await state.set_state(donbass_state.after_poll)
        return
    #await state.set_state(donbass_state.after_poll)
    #nmarkup = ReplyKeyboardBuilder()
    #nmarkup.row(types.KeyboardButton(text="Договорились"))
    #await Bot(all_data().bot_token).send_message(poll_answer.user.id, text='Хорошо, давайте разберемся по-порядку.', reply_markup=nmarkup.as_markup(resize_keyboard=True))


