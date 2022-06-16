import csv

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from DBuse import data_getter, poll_write, sql_safe_select, redis_pop, poll_get, sql_safe_update
from handlers.admin_hand import admin_home
from keyboards.main_keys import filler_kb
from keyboards.admin_keys import main_admin_keyboard
from states.antiprop_states import propaganda_victim
from states.donbass_states import donbass_state
from resources.all_polls import donbass_first_poll, donbass_second_poll
from filters.All_filters import option_filter, PutinFilter, second_donbass_filter


router = Router()


class StateofPutin(StatesGroup):
    main = State()
    game1 = State()
    game2 = State()
    final = State()

@router.message(PutinFilter(), (F.text.in_({'Почему бы и нет', "Начнем"})))
async def putin_love_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен, кто, если не Путин?"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Почему бы и нет', "Начнем"})))
async def putin_love_putin(message: Message, state=FSMContext):
    text = "Выберите описание Владимира Путина, которое вы считаете наиболее точным:"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Не лучший президент, но кто, если не Путин?"))
    nmarkup.row(types.KeyboardButton(text="Превосходный лидер и отличный президент"))
    nmarkup.row(types.KeyboardButton(text="Хороший президент, но его указания плохо исполняют"))
    nmarkup.row(types.KeyboardButton(text="Военный преступник"))
    nmarkup.row(types.KeyboardButton(text="Был хорошим раньше"))
    nmarkup.adjust(1,1,1,2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Нет, не согласен.', "Может и есть, но пока их не видно", "Конечно такие люди есть"})))
async def putin_big_love_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_big_love_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Согласен, кто, если не Путин?") | (F.text == "Не лучший президент, но кто, если не Путин?"))
async def putin_only_one(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_only_one'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Может и есть, но пока их не видно"))
    nmarkup.row(types.KeyboardButton(text="Конечно такие люди есть"))
    nmarkup.row(types.KeyboardButton(text="Не говори так, Путин с нами надолго!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Не говори так, Путин с нами надолго!") | (F.text == "Превосходный лидер и отличный президент"))
async def putin_so_handsome(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_so_handsome'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Может и есть, но пока их не видно"))
    nmarkup.row(types.KeyboardButton(text="Конечно такие люди есть"))
    nmarkup.row(types.KeyboardButton(text="Не говори так, Путин с нами надолго!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Хороший президент, но его указания плохо исполняют"))
async def putin_not_putin(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_not_putin'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'Скорее да', "Скорее нет"})))
async def putin_game_of_lie(message: Message, state:FSMContext):
    await state.set_state(StateofPutin.game1)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_game_of_lie'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Приступим!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Приступим!") | (F.text == "Ладно, давай еще")), state=StateofPutin.game1)
async def putin_game1_question(message: Message, state:FSMContext):
    try:
        count = (await state.get_data())['pgamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.putin_lies")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal FROM public.putin_lies "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print(truth_data)
        await state.update_data(pgamecount=count, rebuttal=truth_data[4], belive=truth_data[2],
                                not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это случайная ошибка"))
        nmarkup.row(types.KeyboardButton(text="Специально соврал!"))
        if truth_data[0] != None:
            try:
                await message.answer_video(truth_data[0], reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[1], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
            "Ой, у меня закончились примеры :(\n\nДавайте я лучше вместо этого расскажу вам анекдот!",
            reply_markup=nmarkup.as_markup())


@router.message(((F.text == "Это случайная ошибка") | (F.text == "Специально соврал!")), state=StateofPutin.game1)
async def putin_game1_answer(message: Message, state=FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Это случайная ошибка":
        base_update_dict.update({'belivers':data['belive']+1})
    elif message.text == "Специально соврал!":
        base_update_dict.update({'nonbelivers': data['not_belive'] + 1})
    await sql_safe_update("putin_lies", base_update_dict, {'id': str(data['pgamecount'])})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем!"))
    nmarkup.row(types.KeyboardButton(text="Достаточно."))
    await message.answer(f'А вот что думают другие участники:\nПравда: {round(t_percentage * 100, 1)}%\nЛожь: {round((100 - t_percentage * 100), 1)}',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Достаточно.")), state=StateofPutin.game1)
async def putin_game1_are_you_sure(message: Message, state:FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ладно, давай еще"))
    nmarkup.row(types.KeyboardButton(text="Нет, хватит с меня"))
    await message.answer('Вы уверены? У меня еще есть примеры',reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message(((F.text == "Нет, хватит с меня")), state=StateofPutin.game1)
async def putin_game1_are_you_sure(message: Message, state:FSMContext):
    await state.clear()
    await state.set_state(StateofPutin.game2)
    text = await sql_safe_select('text', 'texts', {'name': 'putin_plenty_promises'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text,reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Давай")), state=StateofPutin.game2)
async def putin_game1_are_you_sure(message: Message, state:FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_nothing_done'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Начнем!")), state=StateofPutin.game2)
async def putin_game1_are_you_sure(message: Message, state:FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'putin_nothing_done'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))