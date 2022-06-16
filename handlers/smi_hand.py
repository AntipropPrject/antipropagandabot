from aiogram import Router, F
from aiogram import types
from aiogram.types import Message, Update, Chat
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import *

router = Router()


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

        person_list = await poll_get(f'Start_answers: who_to_trust_persons: {message.from_user.id}')
        statements = await sql_safe_select_like("t_id", "name", "assets", 'statement', f'{person_list[0]}')
        assets_list = await poll_get(f'Statements:statement_assets: {message.from_user.id}')
        if assets_list.__len__() == 0:
            for st in statements:
                print(st[0])
                await poll_write(f'Statements:statement_assets: {message.from_user.id}', st[0])

        assets_list = await poll_get(f'Statements:statement_assets: {message.from_user.id}')

        print(assets_list)

        await message.answer_photo(str(assets_list[0]), reply_markup=nmarkup.as_markup(resize_keyboard=True))
        await redis_delete_first_item(f'Statements:statement_assets: {message.from_user.id}')

        assets_list = await poll_get(f'Statements:statement_assets: {message.from_user.id}')
        if assets_list.__len__() == 0:
            await redis_delete_first_item(f'Start_answers: who_to_trust_persons: {message.from_user.id}')


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
async def smi_statement_is_exposure(message: Message):
    media_id = await sql_safe_select('t_id', 'assets', {
        'name': 'test_photo_tag'})  # todo Change asset name to correct\\check the media type
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Cлучайная ошибка"))
    nmarkup.row(types.KeyboardButton(text="Целенаправленная ложь"))
    await message.answer_photo(media_id, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Cлучайная ошибка", "Целенаправленная ложь"})))
async def smi_statement_enough(message: Message):
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
