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
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.truthgame")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT truth, t_id, text, belivers, nonbelivers, rebuttal FROM public.mistakeOrLie "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print('aaaaaa', truth_data)


        await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                not_belive=truth_data[4])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это правда!"))
        nmarkup.row(types.KeyboardButton(text="Это ложь."))
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
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
            "Ой, у меня закончились примеры для игры :(\n\nДавайте я лучше вместо этого расскажу вам анекдот!",
            reply_markup=nmarkup.as_markup())
@router.message((F.text == "Посмотреть еще раз"))
async def sme_statement_start_over(message: Message):
    # todo сделать сценарий если человех кочет посмотреть еще раз
    await message.answer('Еще не готово')



@router.message((F.text.in_({"Cлучайная ошибка", "Целенаправленная ложь"})))
async def smi_statement_enough(message: Message, state=FSMContext):

    if message.text == "Cлучайная ошибка":
        await sql_safe_update("mistakeOrLie", {"statement_asset": data["t_id"]}, {'name': data['name']})
    text = await sql_safe_select('text', 'texts',
                                 {
                                     'name': 'antip_people_stats'})  # todo Change asset name to correct\\check the media type
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно"))
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
