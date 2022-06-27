import asyncio

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import data_getter, poll_write, sql_safe_select, sql_safe_update, redis_delete_from_list, poll_get
from filters.All_filters import NaziFilter, RusHate_pr, NotNaziFilter, ManualFilters
from handlers import true_resons_hand
from middleware import CounterMiddleware
from resources.all_polls import nazizm, nazizm_pr
from utilts import simple_media


class NaziState(StatesGroup):
    main = State()
    small_poll = State()
    after_small_poll = State()
    genocide = State()
    first_poll = State()
    after_first_poll = State()
    game = State()
    final = State()
    rushate = State()
    third_part = State()
    neopower = State()


async def denanazification(message, state):
    naz_answers = await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:')
    if nazizm[2] in naz_answers:
        await nazi_genocide(message, state)
    elif nazizm[0] in naz_answers:
        await nazi_second_poll(message, state)
    elif nazizm[1] in naz_answers:
        await nazi_one_neonazi(message, state)
    else:
        await nazi_game_start(message, state)


router = Router()
router.message.middleware(CounterMiddleware())

router.message.filter(state=NaziState)


@router.message((F.text == "Покажи варианты ✍️"), state=NaziState.first_poll)
async def nazi_first_poll(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжить'))
    question = "Отметьте один или более вариантов, с которыми согласны или частично согласны"
    await message.answer_poll(question, nazizm, allows_multiple_answers=True, is_anonymous=False,
                              reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжить"), state=NaziState.first_poll)
async def nazi_poll_filler(message: Message):
    await message.answer('Пожалуйста, выберите в опросе те пункты, с которыми вы согласны, '
                         'и нажмите кнопку <b>"Подтвердить"</b> или <b>"Vote"</b>', reply_markup=ReplyKeyboardRemove())


@router.poll_answer(state=NaziState.first_poll)
async def npoll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    nazizm_answers = poll_answer.option_ids
    await state.update_data(nazizm_answers=nazizm_answers)
    for index in nazizm_answers:
        await poll_write(f'Usrs: {poll_answer.user.id}: Nazi_answers: first_poll:', nazizm[index])
    # это индекс "ненавидят евреев" в списке
    if 8 in nazizm_answers:
        await redis_delete_from_list(f'Usrs: {poll_answer.user.id}: Nazi_answers: first_poll:',
                                     "Многие украинцы ненавидят евреев")
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Давай 👌"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_word"})
        await bot.send_message(chat_id=poll_answer.user.id, text=text, parse_mode="HTML",
                               reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="А как же неонацизм? 🤨"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_negative"})
        await bot.send_message(poll_answer.user.id, text, parse_mode="HTML",
                               reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await state.set_state(NaziState.after_first_poll)


@router.message((F.text.contains('Давай 👌')), state=NaziState.after_first_poll)
async def nazi_in_masses(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай ⏳"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_in_masses"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Продолжай ⏳')), state=NaziState.after_first_poll)
async def nazi_propaganda(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="А как же неонацизм? 🤨"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_propaganda"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('А как же неонацизм? 🤨')))
async def nazi_neonazi(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Понятно 👌"))
    markup.row(types.KeyboardButton(text="Черт ногу сломит 🤦‍♂️"))
    markup.row(types.KeyboardButton(text="А можно попроще? 🤔"))
    markup.adjust(2, 1)
    text = await sql_safe_select("text", "texts", {"name": "nazi_neonazi"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Черт ногу сломит 🤦‍♂️')) | (F.text.contains('А можно попроще? 🤔')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Так понятнее! 👌"))
    markup.row(types.KeyboardButton(text="Ты всё слишком упрощаешь 🤷‍♀️"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_many_forms"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Ты всё слишком упрощаешь 🤷‍♀️')))
async def nazi_simple(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, продолжим 👌"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_simple"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(NotNaziFilter(), (
        (F.text.contains('Хорошо, продолжим 👌')) | (F.text.contains('Так понятнее! 👌')) | (
        F.text.contains('Понятно 👌'))))
async def nazi_not_zombie(message: Message, state: FSMContext):
    await nazi_game_start(message, state)


@router.message(((F.text.contains('Хорошо, продолжим')) | (F.text.contains('Так понятнее! 👌')) | (
        F.text.contains('Понятно 👌'))))
async def nazi_how_many(message: Message, state: FSMContext):
    await state.set_state(NaziState.small_poll)
    text = await sql_safe_select("text", "texts", {"name": "nazi_how_many"})
    question = 'Выберите один ответ'
    await message.answer(text, disable_web_page_preview=True)
    await message.answer_poll(question=question, options=nazizm_pr, is_anonymous=False,
                              reply_markup=ReplyKeyboardRemove())


@router.poll_answer(state=NaziState.small_poll)
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.set_state(NaziState.after_small_poll)
    pr_answers = poll_answer.option_ids
    for index in pr_answers:
        answer = nazizm_pr[index]
        first_poll_answers = await poll_get(f'Usrs: {poll_answer.user.id}: Nazi_answers: first_poll:')
        await poll_write(f'Usrs: {poll_answer.user.id}: Nazi_answers: small_poll:', answer)
        if answer == "📊 Менее 5%" and 'Многие украинцы ненавидят русских только за то, что они русские' not in first_poll_answers:
            markup = ReplyKeyboardBuilder()
            markup.row(types.KeyboardButton(text="Продолжай ⏳"))
            text = await sql_safe_select("text", "texts", {"name": "nazi_piechart"})
            media = await sql_safe_select('t_id', 'assets', {'name': 'nazi_piechart'})
            await bot.send_photo(chat_id=poll_answer.user.id, photo=media, caption=text,
                                 reply_markup=markup.as_markup(resize_keyboard=True))
        else:
            markup_1 = ReplyKeyboardBuilder()
            markup_1.row(types.KeyboardButton(text="Хорошо, давай продолжим 👌"))
            await bot.send_message(poll_answer.user.id,
                                   'Спасибо, я запомнил ваш ответ. Позже в разговоре мы его обсудим',
                                   reply_markup=markup_1.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Продолжай ⏳')), state=NaziState.after_small_poll)
async def nazi_canny(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, "nazi_canny", markup.as_markup())


@router.message((F.text.contains('Посмотрел(а) 📺')), state=NaziState.after_small_poll)
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжим 👌"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_feels"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(NaziFilter(answer="На Украине происходит геноцид русскоязычного населения"))
async def nazi_genocide(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await state.set_state(NaziState.genocide)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 nazizm[2])
    text = await sql_safe_select("text", "texts", {"name": "nazi_genocide"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=NaziState.genocide)
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, можно 💀"))
    markup.row(types.KeyboardButton(text="Нет, нельзя 🙅‍♀️"))
    markup.row(types.KeyboardButton(text="Я не в праве давать такие оценки 🤷"))
    markup.row(types.KeyboardButton(text="А как же пожар в доме Профсоюзов в Одессе 🔥"))
    markup.adjust(2, 1, 1)
    await simple_media(message, 'nazi_genocide_chart', markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('пожар')), state=NaziState.genocide)
async def nazi_odessa(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, это можно назвать геноцидом 💀"))
    markup.row(types.KeyboardButton(text="Это трагедия, но не геноцид 🙅‍♀️"))
    markup.row(types.KeyboardButton(text="Я не в праве давать такие оценки 🤷"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_odessa"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Нет, нельзя 🙅‍♀️") | (F.text == "Это трагедия, но не геноцид 🙅‍♀️")),
                state=NaziState.genocide)
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай..."))
    text = await sql_safe_select("text", "texts", {"name": "nazi_emotional"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text.contains("можно")) | (F.text == "Я не в праве давать такие оценки 🤷")),
                state=NaziState.genocide)
async def nazi_eight_years(message: Message, state: FSMContext):
    if message.text == "Я не в праве давать такие оценки 🤷":
        text = 'Понимаю, поэтому пусть оценку дадут факты. Задайте себе вопрос:'
    else:
        text = "В таком случае, если это так, у меня есть к вам большой вопрос:"
    await message.answer(text, reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
    await asyncio.sleep(3)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Я тоже задаюсь этим вопросом 🤔"))
    markup.row(types.KeyboardButton(text="Геноцида не было, но ненависть к русским - есть 😠"))
    markup.row(types.KeyboardButton(text="ООН предпочитает закрывать глаза на это ☝️"))
    text2 = await sql_safe_select("text", "texts", {"name": "nazi_eight_years"})
    await message.answer(text2, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    (F.text.in_({'Продолжай...', "Я тоже задаюсь этим вопросом 🤔", "ООН предпочитает закрывать глаза на это ☝️"})),
    state=NaziState.genocide)
async def nazi_exaggeration(message: Message, state: FSMContext):
    await state.set_state(NaziState.third_part)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Да, сильное преувеличение 👌"))
    markup.row(types.KeyboardButton(text="Нет, это геноцид 💀"))
    markup.row(types.KeyboardButton(text="Геноцида не было, но ненависть к русским - есть 😠"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_exaggeration"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


"""@router.message((F.text == "Да, сильное преувеличение 👌"), state=NaziState.genocide)
async def nazi_genocide_exit_2(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, давай"))
    await message.answer('Приятно иметь с вами дело. Тогда продолжим?',
                         reply_markup=markup.as_markup(resize_keyboard=True))"""


@router.message((F.text == "Геноцида не было, но ненависть к русским - есть 😠"), state=NaziState.third_part)
async def nazi_genocide_exit_1(message: Message, state: FSMContext):
    await nazi_second_poll(message, state)


@router.message((F.text == "Нет, это геноцид 💀"), state=NaziState.third_part)
async def nazi_bounds(message: Message, state: FSMContext):
    text = await sql_safe_select("text", "texts", {"name": "nazi_bounds"})
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, давай"))
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(NaziFilter(answer="Многие украинцы ненавидят русских только за то, что они русские"))
async def nazi_second_poll(message: Message, state: FSMContext):
    await state.set_state(NaziState.rushate)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 nazizm[0])
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_second_poll'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=ReplyKeyboardRemove())
    await message.answer_poll(question='Попробуйте угадать!', options=['95%', '76%', '45%', '21%', '6%'],
                              is_anonymous=False, allows_multiple_answers=False, correct_option_id=1)


@router.message(NaziState.rushate, (F.text == 'Продолжай'))
async def poll_filler(message: types.Message):
    await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"',
                         reply_markup=ReplyKeyboardRemove())


@router.poll_answer(state=NaziState.rushate)
async def nazi_76_percent(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_76_percent'})
    photo = await sql_safe_select('t_id', 'assets', {'name': 'nazi_76_percent'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я удивлен(а) 🤔"))
    nmarkup.row(types.KeyboardButton(text="Я не удивлен(а) 😐"))
    nmarkup.row(types.KeyboardButton(text="А я слышал(а) другие цифры 📊"))
    nmarkup.row(types.KeyboardButton(text="Я не доверяю соц. опросам 🙅"))
    nmarkup.adjust(2, 1, 1)
    try:
        await bot.send_photo(poll_answer.user.id, photo, caption=text,
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except TelegramBadRequest:
        await bot.send_video(poll_answer.user.id, photo, caption=text,
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('А я слышал(а) другие цифры')), state=NaziState.rushate)
async def nazi_manipulation(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я удивлен(а) 🤔"))
    nmarkup.row(types.KeyboardButton(text="Я не удивлен(а) 😐"))
    nmarkup.row(types.KeyboardButton(text="Я не доверяю соц. опросам 🙅"))
    await simple_media(message, 'nazi_manipulation', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('удивлен')) | (F.text == "Хорошо, покажи"), state=NaziState.rushate)
async def nazi_not_really(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а) 📺"))
    await simple_media(message, 'nazi_not_really', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('не доверяю соц. опросам')), state=NaziState.rushate)
async def nazi_poll_is_cool(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_poll_is_cool'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, покажи"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Посмотрел(а) 📺"), state=NaziState.rushate)
async def nazi_vs_gopnics(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_vs_gopnics'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Понятно ✔️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(RusHate_pr(), (F.text == "Понятно ✔️"), state=NaziState.rushate)
async def nazi_very_little(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_very_little'})
    text2 = await sql_safe_select('text', 'texts', {'name': 'nazi_less_than_5'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я согласен(на), неонацизм на Украине - преувеличение 👌"))
    nmarkup.row(types.KeyboardButton(text="Украинцы - хорошие люди. А власть у них захватили неонацисты. 😡"))
    nmarkup.row(types.KeyboardButton(text="Это было в 2021 году, а сейчас их полстраны 😬"))
    await message.answer(text)
    await message.answer(text2, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Понятно ✔️"), state=NaziState.rushate)
async def nazi_you_wrong(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_you_wrong'})
    answer_lower = ((await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: small_poll:'))[0]).lower
    text = text.replace('[[выбранный вариант ответа (с маленькой буквы)]]',
                        ((await poll_get(f'Usrs: {message.from_user.id}: Nazi_answers: small_poll:'))[0]).lower())
    text2 = await sql_safe_select('text', 'texts', {'name': 'nazi_less_than_5'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я согласен(на), неонацизм на Украине - преувеличение 👌"))
    nmarkup.row(types.KeyboardButton(text="Украинцы - хорошие люди. А власть у них захватили неонацисты. 😡"))
    nmarkup.row(types.KeyboardButton(text="Это было в 2021 году, а сейчас их полстраны 😬"))
    await message.answer(text)
    await message.answer(text2, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Это было в 2021 году, а сейчас их полстраны 😬"), state=NaziState.rushate)
async def nazi_vs_gopnics(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_half_country'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я согласен(на), неонацизм на Украине - преувеличение 👌"))
    nmarkup.row(types.KeyboardButton(text="Но мы освобождаем Украину, ведь власть у них захватили неонацисты 😡"))
    nmarkup.row(types.KeyboardButton(text="Я тут не соглашусь. 🙅‍♂️ Давай сменим тему"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('захватили')), state=NaziState.rushate)
async def nazi_thirdpart_end(message: Message, state: FSMContext):
    await nazi_one_neonazi(message, state)


@router.message(((F.text.contains('преувеличение')) | (F.text.contains('не соглашусь'))), state=NaziState.rushate)
async def nazi_manual_endpoint_1(message: Message, state: FSMContext):
    await denanazification(message, state)


@router.message(NaziFilter(answer="Власть на Украине захватили неонацисты"))
async def nazi_one_neonazi(message: Message, state: FSMContext):
    await state.set_state(NaziState.neopower)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', nazizm[1])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await simple_media(message, 'nazi_addict', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Продолжай ⏳')), state=NaziState.neopower)
async def nazi_elections(message: Message, state: FSMContext):
    await state.set_state(NaziState.third_part)
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_elections'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


# коридор с болванками
"""
@router.message(NaziFilter(answer="Русский язык притесняется на государственном уровне"))
async def nazi_russian_lang(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 "Русский язык притесняется на государственном уровне")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_russian_lang'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой-то недодел, прочь отсюда, прочь!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer="У них Бандера - национальный герой и это признак нацизма"))
async def nazi_bandera_start(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 "У них Бандера - национальный герой и это признак нацизма")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_bandera_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Бандера был в общем-то неплохим парнем, я все осознал"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer="В Украине есть националистические батальоны (например, Азов) и их надо уничтожить"))
async def nazi_azov_start(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 "В Украине есть националистические батальоны (например, Азов) и их надо уничтожить")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_azov_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(
        text="Если тут будет большая ветка, то разработчики помрут от переработок\nДвинусь-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer="В Украине проходят марши националистов и факельные шествия - это ненормально"))
async def nazi_parade(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 "В Украине проходят марши националистов и факельные шествия - это ненормально")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_parade'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну раз это не готово, пойду-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(
    answer="На Украине переписывают историю / Разрушают советские памятники / Унижают ветеранов"))
async def nazi_no_WW2(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                                 "В Украине переписывают историю Второй Мировой /  Разрушают советские памятники / Унижают ветеранов")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_no_WW2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну раз это не готово, пойду-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))"""


@router.message(state=(NaziState.after_small_poll, NaziState.third_part))
async def nazi_game_start(message: Message, state: FSMContext):
    await state.set_state(NaziState.game)
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text="Начнём! 🚀"))
    nmarkup.add(types.KeyboardButton(text="Пропустим игру 🙅‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Начнём! 🚀") | (F.text == "Ну давай еще 😎") | (F.text == "Продолжаем, давай еще! 👉")),
                state=NaziState.game)
async def country_game_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['ngamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.ucraine_or_not_game")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = \
            data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal, truth FROM public.ucraine_or_not_game "
                        "left outer join assets on asset_name = assets.name "
                        "left outer join texts ON text_name = texts.name "
                        f"where id = {count}")[0]
        print(truth_data)
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3], rebutt=truth_data[4],
                                truth=truth_data[5])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.add(types.KeyboardButton(text="Это Украина 🇺🇦"))
        nmarkup.add(types.KeyboardButton(text="Нет, это Россия 🇷🇺"))
        if truth_data[0] != None:
            capt = ""
            if truth_data[1] != None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'Вот что случилось:\n\n{truth_data[1]}',
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, давай дальше"))
        await message.answer(
            "Боюсь, что пока что у меня кончились примеры. Я поищу еще, а пока что продолжим",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Это Украина 🇺🇦") | (F.text == "Нет, это Россия 🇷🇺")), state=NaziState.game)
async def country_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    text, base_update_dict = "", dict()
    reality = data['truth']
    if message.text == "Это Украина 🇺🇦":
        if reality is True:
            text = 'Правильно! Это на Украине!'
        if reality is False:
            text = 'Вы ошиблись! Это в России!'
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Нет, это Россия 🇷🇺":
        if reality is True:
            text = 'Вы ошиблись! Это на Украине!'
        if reality is False:
            text = 'Правильно! Это в России!'
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("ucraine_or_not_game", base_update_dict, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще! 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, давай закончим 🙅"))
    END = bool(data['ngamecount'] == data_getter('SELECT COUNT(id) FROM public.ucraine_or_not_game')[0][0])
    if END is True:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Спасибо 🤝"))
    await message.answer(
        f'{text}\nРезультаты других участников:\n'
        f'🇷🇺 В России: {round(100 - t_percentage * 100)}% \n🇺🇦 На Украине: {round(t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
    if END is True:
        await message.answer('Мы посмотрели все фото. Спасибо за игру 🤝')


@router.message((F.text == "Достаточно, давай закончим 🙅"), state=NaziState.game)
async def putin_game2_are_you_sure(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну давай еще 😎"))
    nmarkup.row(types.KeyboardButton(text="Мне уже хватит 👌"))
    await message.answer('Вы уверены? У меня еще есть примеры', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(
    ((F.text == "Мне уже хватит 👌") | (F.text == "Спасибо 🤝") | (F.text == "Пропустим игру 🙅‍♂️")),
    state=NaziState.game)
async def putin_in_the_past(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(true_resons_hand.TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_finish'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
