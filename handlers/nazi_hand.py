from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, sql_safe_update, redis_delete_from_list
from filters.All_filters import NaziFilter
from handlers import true_resons_hand
from resources.all_polls import nazizm


class NaziState(StatesGroup):
    main = State()
    first_poll = State()
    game = State()
    final = State()


router = Router()
router.message.filter(state=NaziState)

@router.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state=FSMContext):
    nazizm_answers = poll_answer.option_ids
    await state.update_data(nazizm_answers=nazizm_answers)
    for index in nazizm_answers:
        await poll_write(f'Usrs: {poll_answer.user.id}: Nazi_answers: first_poll:', nazizm[index])
    if 0 in nazizm_answers:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Давай"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_word"})
        await Bot(bata.all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="А как же неонацизм?"))
        text = await sql_safe_select("text", "texts", {"name": "nazi_negative"})
        await bot.send_message(poll_answer.user.id, text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Давай')))
async def nazi_in_masses(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжай"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_in_masses"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Давай')))
async def nazi_propaganda(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="А как же неонацизм?"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_propaganda"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('А как же неонацизм?')))
async def nazi_neonazi(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Понятно"))
    markup.row(types.KeyboardButton(text="Черт ногу сломит"))
    markup.row(types.KeyboardButton(text="А можно попроще?"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_neonazi"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Черт ногу сломит')) | (F.text.contains('А можно попроще?')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Так понятнее!"))
    markup.row(types.KeyboardButton(text="Ты всё слишком упрощаешь"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_many_forms"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Ты всё слишком упрощаешь')))
async def nazi_simple(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_simple"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Хорошо, продолжим')) | (F.text.contains('Так понятнее!')) | (F.text.contains('Понятно!'))) #AntisemitFilter(if answer != 'Ничего из вышеперечисленного...')
async def nazi_how_many(message: Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Хорошо, продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_how_many"})
    question = 'Выберите один ответ'
    await message.answer_poll(question=question, options=nazizm_pr, is_anonymous=False)
    await state.set_state(NaziState.first_poll)

@router.poll_answer(state=NaziState.first_poll)
async def poll_answer_handler(poll_answer: types.PollAnswer, state=FSMContext):
    data = await state.get_data()
    pr_answers = poll_answer.option_ids
    if 'Менее 5%' in pr_answers:
        if 'Многие украинцы ненавидят русских только за то, что они русские' not in data['nazizm_answers']:
            markup = ReplyKeyboardBuilder()
            markup.row(types.KeyboardButton(text="Продолжай"))
            text = await sql_safe_select("text", "texts", {"name": "nazi_piechart"})
            media  = await sql_safe_select('t_id', 'assets', {'name': 'nazi_piechart'})
            await Bot(bata.all_data().bot_token).send_photo(chat_id=poll_answer.user.id, photo=media, text=text,
                                                            reply_markup=markup.as_markup(resize_keyboard=True))
    markup_1 = ReplyKeyboardBuilder()
    markup_1.row(types.KeyboardButton(text="Хорошо, продолжим"))
    await Bot(bata.all_data().bot_token).send_message('Спасибо, я запомнил ваш ответ. Позже в разговоре мы его обсудим', reply_markup=markup_1.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Продолжай')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Посмотрел(а)"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_canny"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Посмотрел(а)')))
async def nazi_many_forms(message: Message):
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжим"))
    text = await sql_safe_select("text", "texts", {"name": "nazi_feels"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))

"""@router.message(NaziFilter(answer='В Украине происходит геноцид русскоязычного населения'), (F.text.contains('Хорошо, продолжим')) | (F.text.contains('Продолжим')))
async def nazi_many_forms(message: Message):
    #тут нужно делать либо иф либо еще как-то
    pass"""










































































































































































































































@router.message(NaziFilter(answer = "Власть на Украине захватили неонацисты"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "Власть на Украине захватили неонацисты")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_one_neonazi'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="С неонацизмом понял, ухожу"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer = "Русский язык притесняется на государственном уровне"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "Русский язык притесняется на государственном уровне")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_russian_lang'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой-то недодел, прочь отсюда, прочь!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer = "У них Бандера - национальный герой и это признак нацизма"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "У них Бандера - национальный герой и это признак нацизма")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_bandera_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Бандера был в общем-то неплохим парнем, я все осознал"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer = "В Украине есть националистические батальоны (например, Азов) и их надо уничтожить"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "В Украине есть националистические батальоны (например, Азов) и их надо уничтожить")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_azov_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Если тут будет большая ветка, то разработчики помрут от переработок\nДвинусь-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer = "В Украине проходят марши националистов и факельные шествия - это ненормально"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "В Украине проходят марши националистов и факельные шествия - это ненормально")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_parade'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну раз это не готово, пойду-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(NaziFilter(answer="В Украине переписывают историю Второй Мировой /  Разрушают советские памятники / Унижают ветеранов"))
async def putin_gaming(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:', "В Украине переписывают историю Второй Мировой /  Разрушают советские памятники / Унижают ветеранов")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_no_WW2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну раз это не готово, пойду-ка я дальше"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message(state = NaziState.main)
async def putin_gaming(message: Message, state: FSMContext):
    await state.set_state(NaziState.game)
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я готов(а)"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Я готов(а)") | (F.text == "Ну давай еще") | (F.text == "Продолжаем!")),
                state=NaziState.game)
async def putin_game2_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['ngamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.putin_old_lies")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal, truth FROM public.ucraine_or_not_game "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print(truth_data)
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3], rebutt = truth_data[4], truth = truth_data[5])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это Украина!"))
        nmarkup.row(types.KeyboardButton(text="Нет, это Россия!"))
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


@router.message(((F.text == "Это Украина!") | (F.text == "Нет, это Россия!")), state=NaziState.game)
async def putin_game2_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    text, base_update_dict = "", dict()
    reality = data['truth']
    if message.text == "Это Украина!":
        if reality is True:
            text = 'Вы совершенно правы, это Украина'
        if reality is False:
            text = 'Вы не угадали, это Россия'
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Нет, это Россия!":
        if reality is True:
            text = 'Нет, это Украина'
        if reality is False:
            text = 'Да, это Российская Федерация'
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("ucraine_or_not_game", base_update_dict, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем!"))
    nmarkup.row(types.KeyboardButton(text="Достаточно."))
    await message.answer(
        f'{text}\n\n{data["rebutt"]} \n\n\nА вот как считают другие участники:\n'
        f'Это Россия: {round((100 - t_percentage * 100), 1)}% \nЭто Украина: {round(t_percentage * 100, 1)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Достаточно.")), state=NaziState.game)
async def putin_game2_are_you_sure(message: Message, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ну давай еще"))
    nmarkup.row(types.KeyboardButton(text="Мне уже хватит"))
    await message.answer('Вы уверены? У меня еще есть примеры', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Мне уже хватит") | (F.text == "Хорошо, давай дальше")), state=NaziState.game)
async def putin_in_the_past(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(NaziState.final)
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_finish'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ого, да сценарий блока не готов! Пойду-ка я к следующим..."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message()
async def nazi_exit(message: Message, state: FSMContext):
    await state.set_state(true_resons_hand.truereasons_state.main)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Продолжим"))
    await message.answer('Это выход из нацизма', reply_markup=markup.as_markup())