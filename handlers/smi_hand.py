from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, Update, Chat, poll_answer
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import *
from states.antiprop_states import propaganda_victim

router = Router()
router.message.filter(state=propaganda_victim)


# todo Attach a state to this handler


# todo Write a filter to allow access only for involved peaple

# todo Get name of TVHosts and include in logic


@router.message((F.text.in_({"Начнем!", 'Скажи еще что нибудь!'})))
@router.message(commands=["test1"])
async def smi_statement(message: Message, state=FSMContext):
    person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')

    try:
        count = (await state.get_data())['gamecount']
    except:
        count = 0
    how_many_rounds = data_getter(f"SELECT COUNT (*) FROM public.mistakeorlie where asset_name like '%{str(person_list[0])[-5:-1].strip()}%'")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds :
        count += 1
        try:
            truth_data = data_getter("SELECT truth, t_id, text, belivers, nonbelivers, rebuttal, asset_name FROM public.mistakeorlie "
                                     "left outer join assets on asset_name = assets.name "
                                     "left outer join texts ON text_name = texts.name "
                                     f"where asset_name like '%{str(person_list[0])[-5:-1].strip()}%' and asset_name like '%{str(count)}%'")[0]

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
        await redis_delete_first_item("Usrs: 5316104187: Start_answers: who_to_trust")
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        # await message.answer(
        #     "Ой, у меня закончились примеры",
        #     reply_markup=nmarkup.as_markup())
        await sme_statement_start_over(message)


@router.message((F.text == "Посмотреть еще раз"))
async def sme_statement_start_over(message: Message):
    # todo сделать сценарий если человех кочет посмотреть еще раз
    text = text = await sql_safe_select('text', 'texts',
                                 {
                                     'name': 'antip_game_continue'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хватит, не будем слушать остальных"))
    nmarkup.row(types.KeyboardButton(text="Давай посмотрим еще!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Хватит, не будем слушать остальных')))
async def sme_statement_skip(message: Message,state=FSMContext):
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




@router.message((F.text.in_({"Cлучайная ошибка", "Целенаправленная ложь"})))
async def smi_statement_enough(message: Message, state=FSMContext):
    if message.text == "Cлучайная ошибка":
        await sql_safe_update("mistakeOrLie", {"statement_asset": data["t_id"]}, {'name': data['name']})
    text = await sql_safe_select('text', 'texts',
                                 {
                                     'name': 'antip_people_stats'})  # todo Change asset name to correct\\check the media type
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хватит, не будем слушать остальных"))
    nmarkup.row(types.KeyboardButton(text="Скажи еще что нибудь!"))

    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Достаточно"))
async def smi_statement(message: Message):
    text = await sql_safe_select('text', 'texts',
                                 {
                                     'name': 'antip_people_stats'})  # todo Change asset name to correct\\check the media type
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно"))
    nmarkup.row(types.KeyboardButton(text="Скажи еще что нибудь!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
