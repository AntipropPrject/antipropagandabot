import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new

from data_base.DBuse import sql_safe_select, redis_just_one_write, redis_just_one_read, \
    mongo_select_info, mongo_update_end, del_key
from handlers.story.main_menu_hand import mainmenu_really_menu
from log import logg
from states.main_menu_states import MainMenuStates
from utilts import simple_media


class StopWarState(StatesGroup):
    main = State()
    next_1 = State()
    war_1 = State()
    arg_1 = State()
    arg_2 = State()
    arg_3 = State()


flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=StopWarState)


@router.message(F.text == "Скорее да ✅", flags=flags)
async def stopwar_rather_yes(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='is_putin_ready_to_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_rather_yes'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_rather_yes'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except Exception:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == "Не знаю 🤷‍♂️", flags=flags)
async def stopwar_idk(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='is_putin_ready_to_stop', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'stopwar_idk'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'stopwar_idk'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.add(types.KeyboardButton(text="Не согласен(а) 🙅"))
    try:
        await message.answer_photo(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except Exception:
        await message.answer_video(photo, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


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
    text_2 = await sql_safe_select('text', 'texts', {'name': 'stopwar_send_me'})
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
        sec = 5
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
            print(sec)
            m, s = divmod(sec, 60)
            sec_t = '{:02d}:{:02d}'.format(m, s)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=m_id, text=f'{sec_t}')
            await asyncio.sleep(1)
            sec -= 1
        await mongo_update_stat(message.from_user.id, 'end')
        await mongo_update_end(message.from_user.id)
        await asyncio.sleep(1)
        await del_key(f'Usrs: {message.from_user.id}: count:')
        await message.answer('Таймер вышел. Вы можете перейти в главное меню.'
                             ' Но если у вас есть ещё с кем поделиться ссылкой на меня'
                             ' — обязательно сделайте это!', reply_markup=markup.as_markup(resize_keyboard=True))
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
        await message.answer('Таймер вышел. Вы можете перейти в главное меню.'
                             ' Но если у вас есть ещё с кем поделиться ссылкой на меня'
                             ' — обязательно сделайте это!', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Покажи инструкцию, как поделиться со всем списком контактов 📝"), flags=flags)
async def stopwar_share_blindly(message: Message):
    timer = await redis_just_one_read(f'Usrs: {message.from_user.id}: count:')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти в главное меню 👇"))
    if timer == '1':
        await simple_media(message, 'stopwar_bulk_forwarding', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await message.answer('Таймер вышел. Вы можете перейти в главное меню.'
                             ' Но если у вас есть ещё с кем поделиться ссылкой на меня'
                             ' — обязательно сделайте это!', reply_markup=nmarkup.as_markup(resize_keyboard=True))


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