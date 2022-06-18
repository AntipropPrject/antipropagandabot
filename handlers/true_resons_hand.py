from typing import Dict, Any

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from filters.All_filters import option_filter, WarReason, second_donbass_filter
import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get, sql_safe_update
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll, nazizm
from filters.All_filters import OperationWar, WarReason
from handlers.nazi_hand import NaziState
from handlers.preventive_strike import PreventStrikeState
from data_base.DBuse import redis_delete_from_list

class truereasons_state(StatesGroup):
    main = State()
    game = State()
    final = State()


router = Router()
router.message.filter(state=truereasons_state)


@router.message(OperationWar(answer='Специальная военная операция (СВО)'), (F.text == 'Продолжай'))
async def reasons_operation(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо -- "война".'))
    nmarkup.row(types.KeyboardButton(text='Нет, это спецоперация.'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('война')))
@router.message(OperationWar(answer='Война / Вторжение в Украину'), (F.text == 'Продолжай'))
async def reasons_war(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Защитить русских в Донбассе'))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Денацификация / Уничтожить нацистов'))
async def reasons_denazi(message: Message, state=FSMContext):
    await state.set_state(NaziState.first_poll)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', 'Денацификация / Уничтожить нацистов')
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_start'})
    question = "Отметьте один или более вариантов, с которыми согласны или частично согласны"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    await message.answer_poll(question, nazizm, allows_multiple_answers=True, is_anonymous=False)




@router.message(WarReason(answer="Предотвратить вторжение на территорию России или ЛНР/ДНР"))
async def prevent_strike_start(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Предотвратить вторжение на территорию России или ЛНР/ДНР")
    await state.clear()
    await state.set_state(PreventStrikeState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай разберем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Демилитаризация / Снижение военной мощи"))
async def reasons_demilitarism(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Демилитаризация / Снижение военной мощи")
    text = "Кусок про демилитаризацию начинается здесь"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Предотвратить размещение военных баз НАТО в Украине"))
async def reasons_no_NATO(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Предотвратить размещение военных баз НАТО в Украине")
    text = "Кусок про военные базы"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Уничтожить биолаборатории / Предотвратить создание ядерного оружия"))
async def reasons_biopigeons(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Уничтожить биолаборатории / Предотвратить создание ядерного оружия")
    text = "Кусок про голубей и славянский геном"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Захватить территории Донбасса и юга Украины"))
async def reasons_take_lands(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Захватить территории Донбасса и юга Украины")
    text = "Кусок про имперское шило в одном месте."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Сменить власть в Украине"))
async def reasons_new_power(message: Message, state=FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Сменить власть в Украине")
    text = "Кусок про смену власти в Украине."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(state=truereasons_state.main)
async def reasons_normal_game_start(message: Message, state:FSMContext):
    await state.set_state(truereasons_state.game)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_normal_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем!'))
    nmarkup.row(types.KeyboardButton(text='Пропустим в этот раз'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Начнем!") | (F.text == "Продолжаем, давай еще!")), state=truereasons_state.game)
async def reasons_normal_game_question(message: Message, state:FSMContext):
    try:
        count = (await state.get_data())['ngamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.normal_game")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal FROM public.normal_game "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это ненормально!"))
        nmarkup.row(types.KeyboardButton(text="Это нормально."))
        if truth_data[0] != None:
            capt = ""
            if truth_data[1] != None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt, reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], caption=capt, reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'{truth_data[1]}', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, давай дальше"))
        await message.answer(
            "Боюсь, что пока что у меня кончились примеры. Я поищу еще, а пока что продолжим",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Это ненормально!") | (F.text == "Это нормально.")), state=truereasons_state.game)
async def reasons_normal_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Это нормально.":
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Это ненормально!":
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("normal_game", base_update_dict, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще!"))
    nmarkup.row(types.KeyboardButton(text="Достаточно."))
    await message.answer(
        f'Результаты других участников:\n\nЭто ненормально: {round((100 - t_percentage * 100), 1)}% \n Все в порядке: {round(t_percentage * 100, 1)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Достаточно.") | (F.text == "Хорошо, давай дальше") | (F.text == "Пропустим в этот раз")), state=truereasons_state.game)
async def reasons_normal_game_enough(message: Message, state:FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_normal_game_enough'})
    await state.set_state(truereasons_state.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Властям виднее."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


"""@router.message((F.text == "Властям виднее."), state=truereasons_state.final)
async def reasons_putin_start(message: Message, state:FSMContext):
    await state"""