import asyncio
import re
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm import state
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import sql_safe_select, redis_just_one_write, redis_just_one_read, \
    mongo_select_info, mongo_update_end, del_key, poll_write, redis_delete_from_list, poll_get, mongo_count_docs
from filters.MapFilters import FinalPolFiler
from handlers.story.main_menu_hand import mainmenu_really_menu
from log import logg
from states.main_menu_states import MainMenuStates
from states.stopwar_states import StopWarState
from utilts import simple_media, percentage_replace, ref_master, ref_spy_sender, MasterCommander, CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=StopWarState)


@router.message(commands=['stopwar2'], flags=flags)
@router.message((F.text == "Ну, допустим, проскакивала мысль, и что? 🤔"), state=StopWarState, flags=flags)
async def stopwar_front_death(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:',
                               'Сторонник спецоперации ⚔️')  # TODO убарать
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_front_death'})
    await state.set_state(StopWarState.front_death)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжим 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({' Ни за что! 🙅‍♂️'})), state=StopWarState, flags=flags)
async def stopwar_how_to_avoid(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_to_avoid'})
    mini_text = "Рад это слышать!"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнём! 🪖"))
    nmarkup.row(types.KeyboardButton(text="Не стоит, мне это не интересно 👉"))
    await state.set_state(StopWarState.stopwar_how_to_avoid)
    await message.answer(mini_text, disable_web_page_preview=True)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Продолжим 👉'})), state=StopWarState, flags=flags)
async def stopwar_how_to_avoid(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_to_avoid'})
    await state.set_state(StopWarState.stopwar_how_to_avoid)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнём! 🪖"))
    nmarkup.row(types.KeyboardButton(text="Не стоит, мне это не интересно 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Не стоит, мне это не интересно 👉'})), state=StopWarState.stopwar_how_to_avoid,
                flags=flags)
async def stopwar_lifesaver(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_lifesaver'})
    await state.set_state(StopWarState.stopwar_lifesaver)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, спасём Вовочку! 🪖"))
    nmarkup.row(types.KeyboardButton(text="Всё равно продолжить 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Начнём! 🪖', 'Хорошо, спасём Вовочку! 🪖'})), state=StopWarState.stopwar_lifesaver,
                flags=flags)
@router.message((F.text.in_({'Начнём! 🪖', 'Хорошо, спасём Вовочку! 🪖'})), state=StopWarState.stopwar_how_to_avoid,
                flags=flags)
async def stopwar_save_vv_start(message: Message, state: FSMContext):
    await state.set_state(StopWarState.stopwar_save_vv_start)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем"))
    await message.answer("Здесь блок про вовчку, пока он не готов",
                         reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Продолжаем', 'Не стоит, мне это не интересно 👉'})),
                state=StopWarState.stopwar_save_vv_start, flags=flags)
@router.message((F.text.in_({'Продолжаем', 'Не стоит, мне это не интересно 👉'})), state=StopWarState.stopwar_lifesaver,
                flags=flags)
async def stopwar_how_and_when(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_how_and_when'})
    await state.set_state(StopWarState.stopwar_how_and_when)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Да, интересно 👍"))
    nmarkup.add(types.KeyboardButton(text="Нет, давай заканчивать "))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Нет, давай заканчивать'})), state=StopWarState.stopwar_how_and_when, flags=flags)
async def stopwar_nostradamus(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_nostradamus'})
    await state.set_state(StopWarState.stopwar_nostradamus)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ладно, расскажи 🙂"))
    nmarkup.row(types.KeyboardButton(text="Точно, давай заканчивать 👉"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)





@router.message((F.text.in_({'Да, интересно 👍', 'Ладно, расскажи 🙂'})), state=StopWarState.stopwar_how_and_when,
                flags=flags)
@router.message((F.text.in_({'Да, интересно 👍', 'Ладно, расскажи 🙂'})), state=StopWarState.stopwar_nostradamus,
                flags=flags)
async def stopwar_ukraine_will_not_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ukraine_will_not_stop'})
    await state.set_state(StopWarState.stopwar_ukraine_will_not_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой второй тезис?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Какой второй тезис?'})), state=StopWarState.stopwar_ukraine_will_not_stop, flags=flags)
async def stopwar_ukraine_at_the_borders(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ukraine_at_the_borders'})
    await state.set_state(StopWarState.stopwar_ukraine_at_the_borders)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Скорее да, будет ⚔️"))
    nmarkup.add(types.KeyboardButton(text="Скорее нет, не будет "))
    nmarkup.add(types.KeyboardButton(text="Я не знаю 🤷‍♂️"))
    nmarkup.adjust(2, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(state=StopWarState.stopwar_ukraine_at_the_borders, flags=flags)
async def stopwar_borders_result(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_borders_result'})
    await state.set_state(StopWarState.stopwar_borders_result)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Какой вопрос?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Какой вопрос?'})), state=StopWarState.stopwar_borders_result, flags=flags)
async def stopwar_will_it_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_will_it_stop'})
    await state.set_state(StopWarState.stopwar_will_it_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Да, это закончит войну 🕊"))
    nmarkup.add(types.KeyboardButton(text="Не обязательно, новый президент может продолжить войну 🗡"))
    nmarkup.add(types.KeyboardButton(text="Не знаю 🤷‍♀"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Да, это закончит войну 🕊'})), state=StopWarState.stopwar_will_it_stop, flags=flags)
async def stopwar_ofc(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_ofc'})
    await state.set_state(StopWarState.stopwar_ofc)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.in_({'Не обязательно, новый президент может продолжить войну 🗡','Не знаю 🤷‍♀'})), state=StopWarState.stopwar_will_it_stop, flags=flags)
async def stopwar_war_eternal(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_war_eternal'})
    await state.set_state(StopWarState.stopwar_war_eternal)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Продолжим 👌'})), state=StopWarState.stopwar_war_eternal, flags=flags)
@router.message((F.text.in_({'Продолжим 👌'})), state=StopWarState.stopwar_ofc, flags=flags)
async def stopwar_clever_bot(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_clever_bot'})
    await state.set_state(StopWarState.stopwar_clever_bot)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Говори! 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.in_({'Говори! 👌'})), state=StopWarState.stopwar_clever_bot, flags=flags)
async def stopwar_putin_will_not_stop(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_putin_will_not_stop'})
    await state.set_state(StopWarState.stopwar_putin_will_not_stop)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Понятно, продолжим 👉"))
    nmarkup.add(types.KeyboardButton(text="Звучит сомнительно 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.in_({'Звучит сомнительно 🤔'})), state=StopWarState.stopwar_putin_will_not_stop, flags=flags)
async def stopwar_putin_already_lost(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_putin_already_lost'})
    await state.set_state(StopWarState.stopwar_putin_already_lost)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text == "Точно, давай заканчивать 👉",
                state=StopWarState.stopwar_nostradamus, flags=flags)
@router.message(F.text == "Понятно, продолжим 👉",
                state=StopWarState.stopwar_putin_will_not_stop, flags=flags)
@router.message(F.text == "Продолжай ⏳",
                state=StopWarState.stopwar_putin_already_lost, flags=flags)
async def stopwar_doubting_ending(message: Message, state: FSMContext):
    user_status = await redis_just_one_read(f'Usrs: {message.from_user.id}: StopWar: NewPolitStat:')
    nmarkup = ReplyKeyboardBuilder()
    text = "не сработал иф"
    await state.set_state(StopWarState.stopwar_ending)
    if user_status == "Сторонник спецоперации ⚔️":
        nmarkup.row(types.KeyboardButton(text="Я всё же хочу поговорить о том, как остановить войну 👌"))
        nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
        nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_warbringer_ending'})
    if user_status == "Сомневающийся 🤷":
        nmarkup.row(types.KeyboardButton(text="Давай 👌"))
        nmarkup.row(types.KeyboardButton(text="Пропустить и перейти в главное меню 👇"))
        nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_doubting_ending'})
    if user_status == "Противник войны 🕊":
        nmarkup.row(types.KeyboardButton(text="Давай 👌"))
        nmarkup.row(types.KeyboardButton(text="Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺"))
        text = await sql_safe_select('text', 'texts', {'name': 'stopwar_peacemaker_ending'})
    if message.text == "Точно, давай заканчивать 👉":
        await message.answer("Хорошо 👌")
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.in_({'Подожди-подожди! А может ли Россия развалиться, если проиграет? 🗺'})), state=StopWarState.stopwar_ending, flags=flags)
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

@router.message((F.text.in_({'Пропустить и перейти в главное меню 👇'})), state=StopWarState.stopwar_ending, flags=flags)
async def stopwar_time_is_marching(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_time_is_marching'})
    text2 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})
    await state.set_state(StopWarState.stopwar_time_is_marching)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Перейти в главное меню 👇"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await message.answer(text2, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.in_({'Давай 👌'})), state=StopWarState.stopwar_ending, flags=flags)
@router.message((F.text.in_({'Я всё же хочу поговорить о том, как остановить войну 👌'})), state=StopWarState.stopwar_ending, flags=flags)
async def stopwar_big_responsibility(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_big_responsibility'})
    await state.set_state(StopWarState.stopwar_big_responsibility)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Что ты предлагаешь ❓❓❓"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.in_({'Я всё же хочу поговорить о том, как остановить войну 👌'})), state=StopWarState.stopwar_big_responsibility, flags=flags)
async def stopwar_save_them(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_save_them'})
    await state.set_state(StopWarState.stopwar_save_them)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="👍"))
    nmarkup.add(types.KeyboardButton(text="👎"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message(state=StopWarState.stopwar_save_them, flags=flags)
async def stopwar_viva_la_resistance(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_viva_la_resistance'})
    await state.set_state(StopWarState.stopwar_viva_la_resistance)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="👍"))
    nmarkup.add(types.KeyboardButton(text="👎"))
    media_id = await sql_safe_select('t_id', 'assets', {'name': "stopwar_viva_la_resistance"})
    await message.answer_video(media_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))