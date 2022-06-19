from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage import redis
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import *
from handlers.anti_prop_hand import antip_truth_game_start_question, antip_truth_game_start
from middleware import CounterMiddleware
from states import antiprop_states
from states.antiprop_states import propaganda_victim

router = Router()
router.message.middleware(CounterMiddleware())

router.message.filter(state=propaganda_victim.ppl_propaganda)

messageDict = dict()


@router.message((F.text.contains("Давайте начнём!")))
@router.message((F.text.contains('скажи еще что нибудь!')))
async def smi_statement(message: Message, state: FSMContext):
    messageDict.update({message.from_user.id: message})

    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    try:
        count = (await state.get_data())['gamecount']
    except:
        count = 0

    try:
        how_many_rounds = data_getter(
            f"SELECT COUNT (*) FROM public.mistakeorlie where asset_name like '%{str(person_list[0])[-5:-1].strip()}%'")[
            0][0]
    except IndexError as er:
        errmarkup = ReplyKeyboardBuilder()
        errmarkup.rows(types.KeyboardButton(text="Переход к игре в правду"))
        await message.answer("У Надо продумать, что будет если закончились материалы и при этом нет больше красных личностей? ")
        # Todo send user on truthgame

    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        try:
            truth_data = data_getter(
                "SELECT truth, t_id, text, belivers, nonbelivers, rebuttal, asset_name FROM public.mistakeorlie "
                "left outer join assets on asset_name = assets.name "
                "left outer join texts ON text_name = texts.name "
                f"where asset_name like '%{str(person_list[0])[-5:-1].strip()}%' and asset_name like '%{str(count)}%'")[
                0]

            print('aaaaaa', truth_data)

            await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                    not_belive=truth_data[4], last_media=truth_data[6])

        except IndexError as er:
            await message.answer(text=f"Медиафайл не найден {er}")
            await state.update_data(gamecount=count)

        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Случайная ошибка"))
        nmarkup.row(types.KeyboardButton(text="Целенаправленная ложь"))
        if truth_data[1] != None:
            capt = ""
            if truth_data[2] != None:
                capt = truth_data[2]
            try:
                await message.answer_video(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await redis_delete_first_item("Usrs: 5316104187: Start_answers: who_to_trust_persons:")
        await state.update_data(gamecount=0)
        # await message.answer(
        #     "Ой, у меня закончились примеры",
        #     reply_markup=nmarkup.as_markup())
        await sme_statement_start_over(message, state)


@router.poll_answer(state=antiprop_states.propaganda_victim.dialogue_start_over)
async def smi_statement_poll(poll_answer: types.PollAnswer, state: FSMContext):
    await state.update_data(gamecount=0)
    options = await state.get_data()
    lst_options = options["options_start_over"]
    lst_answers = poll_answer.option_ids
    lst = []
    for index in lst_answers:
        lst.append(lst_options[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:', lst_options[index])
        list_to_customize = await poll_get(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:')
        newset = set(list_to_customize)
        redis = all_data().get_data_red()
        all_data().get_data_red().delete(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:')
        for person in newset:
            await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: who_to_trust_persons:', person)
    try:
        await smi_statement(messageDict.get(poll_answer.user.id), state)
    except:
        await Bot(all_data().bot_token).send_message(chat_id=poll_answer.user.id, text="Ошибка")


@router.message((F.text == "Достаточно"))
async def sme_statement_start_over(message: Message, state: FSMContext):

    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    try:
        person = person_list[0]
    except IndexError:
        await smi_statement_enough(message, state)
    else:
        options = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')
        options.append("Никого...")
        text = await sql_safe_select('text', 'texts',
                                     {
                                         'name': 'antip_game_continue'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хватит, не будем слушать остальных"))
        # nmarkup.row(types.KeyboardButton(text="Давай посмотрим еще!"))
        await state.update_data(options_start_over=options)
        await message.answer(text)

        await message.answer_poll(text, options, is_anonymous=False, allows_multiple_answers=False,
                                  reply_markup=nmarkup.as_markup(resize_keyboard=True))
        await state.set_state(antiprop_states.propaganda_victim.dialogue_start_over)


@router.message((F.text.contains('Хватит, не будем слушать остальных')))
async def sme_statement_skip(message: Message, state=FSMContext):
    data = await state.get_data()

    not_viewed = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Хорошо, давай посмотрим'))
    markup.row(types.KeyboardButton(text='Не надо, я и так знаю, что они врут'))
    markup.row(types.KeyboardButton(text='Не надо, я все равно буду доверять им'))
    lst_web_answers = str(', '.join(not_viewed))
    next_channel = str(not_viewed[0])
    await state.update_data(not_viewed_chanel=not_viewed[0])
    await message.answer("Я хотел показать вам еще, как врут "
                         f"{lst_web_answers}, ведь вы "
                         "отметили, что доверяете им. Для нашей "
                         "дальнейшей беседы важно, чтобы мы "
                         "разобрались, кому можно верить, а кому нет.\n\n"
                         "Можно я все-таки покажу хотя бы один "
                         f"сюжет от {next_channel}?", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Случайная ошибка", "Целенаправленная ложь"})))
async def smi_statement_enough(message: Message, state=FSMContext):
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Cлучайная ошибка":
        base_update_dict = {'belivers': data['belive'] + 1}
        print('Этому верит', base_update_dict)
    elif message.text == "Целенаправленная ложь":
        base_update_dict = {'nonbelivers': data['not_belive'] + 1}
        print('Этому верит', base_update_dict)
    await sql_safe_update("mistakeorlie", base_update_dict, {'asset_name': f"{data['last_media']}"})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    try:
        nmarkup.row(types.KeyboardButton(text=f"{person_list[0]} - скажи еще что нибудь!!"))
        nmarkup.row(types.KeyboardButton(text="Достаточно"))
    except IndexError as er:
        print(er)
    await message.answer(
        f'А вот что думаютдругие мои собеседники:\nСлучайная ошибка: {round(t_percentage * 100, 1)}%\nЦеленаправленная ложь: {round((100 - t_percentage * 100), 1)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Не надо, я и так знаю, что они врут", "Не надо, я все равно буду доверять им", "Переход к игре в правду"})))
async def smi_statement_enough(message: Message, state: FSMContext):
    for key in all_data().get_data_red().scan_iter(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:*'):
        all_data().get_data_red().delete(key)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Переход!!!"))
    await message.answer("Переходим к игре в правду(как будет выглядетть жтот переход, решат наши дизайнеры. В это место мы так же попадаем, если закончились материалы и личности.", reply_markup=nmarkup.as_markup(resize_keyboard=True))

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
