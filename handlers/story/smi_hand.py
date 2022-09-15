from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import *
from handlers.story.anti_prop_hand import antip_funny_propaganda, antip_web_exit_1
from states.antiprop_states import propaganda_victim

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=propaganda_victim)



@router.message((F.text.contains("Начнём 🙂")), flags=flags)
@router.message((F.text.contains("Хорошо, давай послушаем 🗣")), flags=flags)
@router.message((F.text.contains('послушаем его еще! 🗣')), flags=flags)
@router.message(commands=["testsmi"], flags=flags)
async def smi_statement(message: Message, state: FSMContext):
    if message.text == 'Начнём 🙂':
        await mongo_update_stat_new(tg_id=message.from_user.id, column='false_on_prop', value='Да')
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    data = await state.get_data()
    # try:
    #     person_vewed_list = list(data['person_viewed'])
    #     for person in person_vewed_list:
    #         message_text = message.text
    #         trimed = message_text.rstrip(message_text[-1])
    #         print(trimed)
    #         print(person == trimed)
    #         if person == trimed:
    #             await state.update_data({f'{person_list[0]}_gamecount': 0})
    # except:
    #     print('not_viewed contains nothing ')


    try:
        count = (await state.get_data())[f'{person_list[0]}_gamecount']
    except:
        await state.update_data({f'{person_list[0]}_gamecount': 0})
        count = 0

    how_many_rounds = (await data_getter(
        f"SELECT COUNT (*) FROM public.mistakeorlie where asset_name like '%{str(person_list[0])[-5:-1].strip()}%'"))[
        0][0]
    try:
        how_many_rounds_redis = (await state.get_data())[f'{person_list[0]}_howmanyrounds']
    except:
        await state.update_data({f'{person_list[0]}_howmanyrounds': how_many_rounds})
    if count < how_many_rounds:
        count += 1
        try:
            truth_data = (await data_getter(
                "SELECT t_id, text, belivers, nonbelivers, rebuttal, asset_name, id FROM public.mistakeorlie "
                "left outer join assets on asset_name = assets.name "
                "left outer join texts ON text_name = texts.name "
                f"where asset_name like '%{str(person_list[0])[-5:-1].strip()}%' and asset_name like '%{str(count)}%'"))[
                0]
            await state.update_data({f'{person_list[0]}_gamecount': count})
            await state.update_data(rebuttal=truth_data[5], belive=truth_data[2],
                                    not_belive=truth_data[3], last_media=truth_data[5], gid=truth_data[6])

        except IndexError as er:
            await message.answer(text=f"Медиафайл не найден {er}")

        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Целенаправленная ложь 👎"))
        nmarkup.row(types.KeyboardButton(text="Случайная ошибка / Не ложь 👍"))
        if truth_data[0] is not None:
            capt = ""
            if truth_data[4] is not None:
                capt = truth_data[4]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML"
                                           )
            except:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))

        else:
            await message.answer(truth_data[4], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await state.update_data(person_viewed=person_list[0])
        # await message.answer(
        #     "Ой, у меня закончились примеры",
        #     reply_markup=nmarkup.as_markup())
        await sme_statement_start_over(message, state)


@router.message((F.text.in_({"Случайная ошибка / Не ложь 👍", "Целенаправленная ложь 👎"})), flags=flags)
async def smi_statement_enough(message: Message, state: FSMContext):
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    data = await state.get_data()
    answer_group = str()
    if message.text == "Случайная ошибка / Не ложь 👍":
        answer_group = 'belivers'
    elif message.text == "Целенаправленная ложь 👎":
        answer_group = 'nonbelivers'
    await mongo_game_answer(message.from_user.id, 'mistakeorlie', data['gid'],
                            answer_group, {'id': data['gid']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()

    how_many_rounds = (await data_getter(
        f"SELECT COUNT (*) FROM public.mistakeorlie where asset_name like '%{str(person_list[0])[-5:-1].strip()}%'"))[
        0][0]
    count = data[f'{person_list[0]}_gamecount']
    if count < how_many_rounds:
        nmarkup.row(types.KeyboardButton(text=f"{person_list[0]} - послушаем его еще! 🗣"))

    nmarkup.row(types.KeyboardButton(text="Достаточно 🤚"))

    await message.answer(
        f'А вот что думают другие мои собеседники:\n👍Случайная ошибка: {round(t_percentage * 100)}%\n👎 Целенаправленная ложь: {round(100 - t_percentage * 100)}%',
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
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    person = person_list[0]
    person_list.remove(person)
    #data = await state.get_data()  # Удаление после просмотра всех сюжетов
    #if data[f"{person}_howmanyrounds"] == data[f"{person}_gamecount"]:  # Удаление после просмотра всех сюжетов
    await redis_delete_first_item(f"Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:")
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    try:
        person = person_list[0]
    except IndexError:
        await antip_funny_propaganda(message, state)
    else:
        nmarkup = ReplyKeyboardBuilder()
        options = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
        for person in options:
            nmarkup.row(types.KeyboardButton(text=f'{person}🗣'))
            nmarkup.adjust(2)
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
    redis = all_data().get_data_red()

    list_to_customize = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
    list_to_customize1 = list_to_customize.copy()


    try:
        message_text = message.text
        trimed = message_text.rstrip(message_text[-1])
        if not list_to_customize.__contains__(trimed):
            await state.update_data({f'{trimed}_gamecount': 0})
        list_to_customize.remove(trimed)
    except:
        print('дубликатов нет')

    redis.delete(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    if message.text == "Хватит, не будем слушать остальных 🙅‍♂️":
        for person in list_to_customize1:
            await poll_write(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', person)
        await sme_statement_skip(message, state)
    else:
        redis.lpush(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', trimed)
        for person in list_to_customize:
            await poll_write(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:', person)

        await smi_statement(message, state)


@router.message((F.text.contains('Хватит, не будем слушать остальных 🙅‍♂️')), flags=flags)
async def sme_statement_skip(message: Message, state=FSMContext):
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
    if len(lst_web_answers) == 1:
        string = "врёт"

    await message.answer(f"Я хотел показать вам еще, как {string} "
                         f"{lst_web_answers}, "
                         "ну когда вы ещё увидите такую подборку в одном месте? Для нашей "
                         "дальнейшей беседы важно, чтобы мы "
                         "разобрались, кому можно верить, а кому нет.\n\n"
                         "Можно я все-таки покажу хотя бы один "
                         f"сюжет от {next_channel}?", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(F.text.contains('Не надо'))
async def skipskip(message: Message, state=FSMContext):
    redis = all_data().get_data_red()
    redis.delete(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:')

    await antip_web_exit_1(message, state)
