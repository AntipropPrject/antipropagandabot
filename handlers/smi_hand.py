from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from data_base.DBuse import *
from handlers.anti_prop_hand import antip_truth_game_start
from states.antiprop_states import propaganda_victim

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=propaganda_victim)
messageDict = dict()


@router.message((F.text.contains("Давайте начнём!")), flags=flags)
@router.message((F.text.contains("Хорошо, давай послушаем 🗣")), flags=flags)
@router.message((F.text.contains('послушаем его еще! 🗣')), flags=flags)
@router.message(commands=["testsmi"], flags=flags)
async def smi_statement(message: Message, state: FSMContext):
    messageDict.update({message.from_user.id: message})

    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    for person in person_list:
        try:
            count = (await state.get_data())[f'{person}_gamecount']
        except:
            await state.update_data({f'{person}_gamecount': 0})
            count = 0

    try:
        how_many_rounds = (await data_getter(
            f"SELECT COUNT (*) FROM public.mistakeorlie where asset_name like '%{str(person_list[0])[-5:-1].strip()}%'"))[
            0][0]
    except:
        errmarkup = ReplyKeyboardBuilder()
        errmarkup.rows(types.KeyboardButton(text="Переход к игре в правду"))
        await message.answer(
            "У Надо продумать, что будет если закончились материалы и при этом нет больше красных личностей? ")
        # Todo send user on truthgame

    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        try:
            truth_data = (await data_getter(
                "SELECT truth, t_id, text, belivers, nonbelivers, rebuttal, asset_name FROM public.mistakeorlie "
                "left outer join assets on asset_name = assets.name "
                "left outer join texts ON text_name = texts.name "
                f"where asset_name like '%{str(person_list[0])[-5:-1].strip()}%' and asset_name like '%{str(count)}%'"))[
                0]

            print('aaaaaa', truth_data)

            await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                    not_belive=truth_data[4], last_media=truth_data[6])

        except IndexError as er:
            await message.answer(text=f"Медиафайл не найден {er}")


        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Целенаправленная ложь 👎"))
        nmarkup.row(types.KeyboardButton(text="Случайная ошибка / Не ложь 👍"))
        if truth_data[1] is not None:
            capt = ""
            if truth_data[5] is not None:
                capt = truth_data[5]
            try:
                await message.answer_video(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML"
                                           )
            except:
                await message.answer_photo(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            await state.update_data({f'{person}_gamecount': count})
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:

        # await message.answer(
        #     "Ой, у меня закончились примеры",
        #     reply_markup=nmarkup.as_markup())
        await sme_statement_start_over(message, state)


@router.message((F.text.in_({"Случайная ошибка / Не ложь 👍", "Целенаправленная ложь 👎"})), flags=flags)
async def smi_statement_enough(message: Message, state: FSMContext):
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    data = await state.get_data()
    base_update_dict = dict()
    print(message.text)
    if message.text == "Случайная ошибка / Не ложь 👍":
        base_update_dict = {'belivers': data['belive'] + 1}
        print('Этому верит', base_update_dict)
    elif message.text == "Целенаправленная ложь 👎":
        base_update_dict = {'nonbelivers': data['not_belive'] + 1}
        print('Этому верит', base_update_dict)
    await sql_safe_update("mistakeorlie", base_update_dict, {'asset_name': data['last_media']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    try:
        nmarkup.row(types.KeyboardButton(text=f"{person_list[0]} - послушаем его еще! 🗣"))
        nmarkup.row(types.KeyboardButton(text="Достаточно 🤚"))
    except IndexError as er:
        print(er)
    await message.answer(
        f'А вот что думаютдругие мои собеседники:\nСлучайная ошибка: {round(t_percentage * 100)}%\nЦеленаправленная ложь: {round(100 - t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


# @router.poll_answer(state=antiprop_states.propaganda_victim.dialogue_start_over)
# async def smi_statement(poll_answer: types.PollAnswer, state=FSMContext):
#     text = await sql_safe_select('text', 'texts',
#                                  {
#                                      'name': 'antip_people_stats'})  # todo Change asset name to correct\\check the media type
#     nmarkup = ReplyKeyboardBuilder()
#     nmarkup.row(types.KeyboardButton(text="Достаточно"))
#     nmarkup.row(types.KeyboardButton(text="Скажи еще что нибудь!"))
#     await Bot(all_data().bot_token).send_message(chat_id=poll_answer.user.id, text=text,
#                                                  reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Достаточно 🤚"), flags=flags)
async def sme_statement_start_over(message: Message, state: FSMContext):
    await redis_delete_first_item("Usrs: 5316104187: Start_answers: who_to_trust_persons:")
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    print(person_list)

    try:
        person = person_list[0]
    except IndexError:
        await antip_truth_game_start(message, state)
    else:
        nmarkup = ReplyKeyboardBuilder()
        options = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons_newpoll:')
        for person in options:
            nmarkup.row(types.KeyboardButton(text=f'{person}🗣'))
        nmarkup.row(types.KeyboardButton(text="Хватит, не будем слушать остальных 🙅‍♂️"))
        await state.set_state(propaganda_victim.options)
        text = await sql_safe_select('text', 'texts',
                                     {
                                         'name': 'antip_game_continue'})

        await state.update_data(options_start_over=options)
        await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

        # await state.set_state(antiprop_states.propaganda_victim.ppl_propaganda.dialogue_start_over)


@router.message(state=propaganda_victim.options, flags=flags)
async def smi_statement_poll(message: Message, state: FSMContext):
    trimed = ""
    redis = all_data().get_data_red()

    list_to_customize = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    list_to_customize1 = list_to_customize.copy()

    print(list_to_customize)

    try:
        message_text = message.text
        trimed = message_text.rstrip(message_text[-1])
        list_to_customize.remove(trimed)
    except:
        print('дубликатов нет')
    print(list_to_customize)

    redis.delete(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    if message.text == "Хватит, не будем слушать остальных 🙅‍♂️":
        for person in list_to_customize1:
            await poll_write(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', person)
        await sme_statement_skip(message, state)
    else:

        for person in list_to_customize:
            await poll_write(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', person)
            redis.lpush(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', trimed)
        await smi_statement(message, state)


@router.message((F.text.contains('Хватит, не будем слушать остальных 🙅‍♂️')), flags=flags)
async def sme_statement_skip(message: Message, state=FSMContext):
    data = await state.get_data()

    not_viewed = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    try:
        next_channel = str(not_viewed[0])
    except:
        await message.answer("Нету личностей в списке, надо зайти в раздел заново")
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Хорошо, давай послушаем 🗣'))
    markup.row(types.KeyboardButton(text='Не надо, я и так знаю, что они врут 😒'))
    markup.row(types.KeyboardButton(text='Не надо, я все равно буду доверять им 👍'))
    lst_web_answers = str(', '.join(not_viewed))

    await state.update_data(not_viewed_chanel=not_viewed[0])
    string = "врут"
    if lst_web_answers.__sizeof__() == 1:
        string = "врёт"

    await message.answer(f"Я хотел показать вам еще, как {string} "
                         f"{lst_web_answers}, ведь вы "
                         "отметили, что доверяете им. Для нашей "
                         "дальнейшей беседы важно, чтобы мы "
                         "разобрались, кому можно верить, а кому нет.\n\n"
                         "Можно я все-таки покажу хотя бы один "
                         f"сюжет от {next_channel}?", reply_markup=markup.as_markup(resize_keyboard=True))
