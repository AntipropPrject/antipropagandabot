from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, Update, Chat
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import *
from middleware import CounterMiddleware
from states.antiprop_states import propaganda_victim

router = Router()
router.message.middleware(CounterMiddleware())

router.message.filter(state=propaganda_victim)


# todo Attach a state to this handler


# todo Write a filter to allow access only for involved peaple

# todo Get name of TVHosts and include in logic

@router.message((F.text.in_({"Начнем!", 'Скажи еще что нибудь!'})))
@router.message(commands=["test1"])
async def smi_statement(message: Message):
    global statements, tag_name, person_list, assets_list
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел(а). Что не так?"))
    nmarkup_new = nmarkup.copy()
    nmarkup_new.row(types.KeyboardButton(text="Посмотреть еще раз"))

    try:

        person_list = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')
        statements = await sql_safe_select_like("t_id", "name", "assets", 'statement', f'{person_list[0]}')
        assets_list = await poll_get(f'Usrs: {message.from_user.id}: Statements:statement_assets:')
        if assets_list.__len__() == 0:
            for st in statements:
                print(st[0])
                await poll_write(f'Usrs: {message.from_user.id}: Statements:statement_assets:', st[0])

        assets_list = await poll_get(f'Usrs: {message.from_user.id}: Statements:statement_assets:')

        print(assets_list[0])
        print(str(assets_list[0]))

        await message.answer_photo(str(assets_list[0]), reply_markup=nmarkup.as_markup(resize_keyboard=True))
        await redis_delete_first_item(f'Usrs: {poll_answer.user.id}: Statements:statement_assets:')

        assets_list = await poll_get(f'Usrs: {message.from_user.id}: Statements:statement_assets:')
        if assets_list.__len__() == 0:
            await redis_delete_first_item(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust_persons:')


    except IndexError as err:
        logg.get_info(err)
        logg.get_info(': All statements watched')
        await message.answer('Похоже вы посмотрели все материалы',
                             reply_markup=nmarkup_new.as_markup(resize_keyboard=True))


@router.message((F.text == "Посмотреть еще раз"))
async def sme_statement_start_over(message: Message):
    # todo сделать сценарий если человех кочет посмотреть еще раз
    await message.answer('Еще не готово')


@router.message((F.text == "Посмотрел(а). Что не так?"))
async def smi_statement_is_exposure(message: Message, state=FSMContext):
    media_id = await sql_safe_select('t_id', 'assets', {
        'name': 'test_photo_tag'})  # todo Change asset name to correct\\check the media type
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Cлучайная ошибка"))
    nmarkup.row(types.KeyboardButton(text="Целенаправленная ложь"))
    try:
        count = (await state.get_data())['gamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.truthgame")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT truth, t_id, text, belivers, nonbelivers, rebuttal FROM public.truthgame "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print('aaaaaa', truth_data)

        await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                not_belive=truth_data[4])
        if truth_data[1] != None:
            try:
                await message.answer_video(truth_data[1], reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[1], reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
            "Ой, у меня закончились примеры для игры :(\n\nДавайте я лучше вместо этого расскажу вам анекдот!",
            reply_markup=nmarkup.as_markup())
    # await message.answer_photo(media_id, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Cлучайная ошибка", "Целенаправленная ложь"})))
async def smi_statement_enough(message: Message, state=FSMContext):
    if message.text == "Cлучайная ошибка":
        await sql_safe_update("truthgame", base_update_dict, {'id': str(data['gamecount'])})
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
