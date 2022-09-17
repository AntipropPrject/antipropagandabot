import re

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import sql_safe_select, mongo_count_docs
from utils.elk_logger import Logger
from utilts import CoolPercReplacer

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import data_getter, sql_safe_select, mongo_game_answer, mongo_count_docs
from utilts import simple_media, simple_media_bot, CoolPercReplacer
from filters.MapFilters import PutinFilter
from handlers.story.stopwar_hand import StopWarState
from utilts import simple_media
import re

flags = {"throttling_key": "True"}
router = Router()


class Shop(StatesGroup):
    main = State()
    after_first_poll = State()
    shop_transfer = State()
    shop_bucket = State()
    shop_why_so_many = State()
    shop_callback = State()


price_dict = {'1000 x 🚀 Детская площадка': 1150000,
              '100 x 🏫 Современная школа': 560000000,
              '1000 x ⚡️ Электробус': 31400000,
              '10 x 🛩 Пассажирский самолёт (SuperJet)': 2400000000,
              '100 км x 🛣 Автомагистраль (от 4 полос)': 5230000000,
              '100 x 🌳 Большой парк': 500000000,
              '10 x 💊 Детский онкологический центр': 1500000000,
              '10 x 🏥 Корпус ядерной медицины': 2600000000,
              '1 x 🔥 Северный поток — 2': 1037000000000,
              '100 x 🧸 Спасти жизнь ребёнку': 121000000
              }

inline = InlineKeyboardBuilder()
inline.button(text='1000 x 🚀',
              callback_data='1000 x 🚀 Детская площадка',)
inline.button(text='100 x 🏫',
              callback_data='100 x 🏫 Современная школа')
inline.button(text='1000 x ⚡',
              callback_data='1000 x ⚡️ Электробус')
inline.button(text='10 x 🛩',
              callback_data='10 x 🛩 Пассажирский самолёт (SuperJet)')
inline.button(text='100 км x 🛣',
              callback_data='100 км x 🛣 Автомагистраль (от 4 полос)')
inline.button(text='100 x 🌳',
              callback_data='100 x 🌳 Большой парк')
inline.button(text='10 x 💊',
              callback_data='10 x 💊 Детский онкологический центр')
inline.button(text='10 x 🏥',
              callback_data='10 x 🏥 Корпус ядерной медицины')
inline.button(text='1 x 🔥',
              callback_data='1 x 🔥 Северный поток — 2')
inline.button(text='100 x 🧸',
              callback_data='100 x 🧸 Спасти жизнь ребёнку')
inline.button(text='Очистить корзину',
              callback_data='Очистить корзину')
inline.button(text='Оформить заказ',
              callback_data='Оформить заказ')

inline.adjust(3,3,4,2)


@router.message(commands=["shop"], flags=flags)
@router.message((F.text.contains("shop")), flags=flags)
async def shop_welcome(message: types.Message, state: FSMContext):
    print("in shop")
    await state.set_state(Shop.main)
    text = await sql_safe_select("text", "texts", {"name": "shop_welcome"})

    nmarkup = ReplyKeyboardBuilder()
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
    await message.answer_poll("Сколько?", explanation_parse_mode="HTML",
                              allows_multiple_answers=True,
                              options=["Около 1 000 000 000 (1 миллиарда) рублей",
                                       "Около 100 000 000 000 (100 миллиардов) рублей",
                                       "Около 10 000 000 000 000 (10 триллионов) рублей",
                                       "Около 1 000 000 000 000 000 (1 квадриллиона) рублей"], is_anonymous=False,
                              reply_markup=nmarkup.as_markup(resize_keyboard=True))
    Logger.log("TEST TEST TEST")


@router.poll_answer(state=Shop.main, flags=flags)
async def shop_after_first_poll(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    # await mongo_update_stat_new(tg_id=poll_answer.user.id, column='shop_after_first_poll',
    #                             value=poll_answer.option_ids[0])
    print(poll_answer.option_ids[0])
    # right_answers = await mongo_count_docs('database', 'statistics_new', {'shop_after_first_poll': 2})
    # all_answers = await mongo_count_docs('database', 'statistics_new', {'shop_after_first_poll': {'$exists': True}})
    await state.set_state(Shop.after_first_poll)
    await state.update_data(shop_after_first_poll=poll_answer.option_ids[0])
    # await mongo_update_stat_new(tg_id=poll_answer.user.id, column='shop_after_first_poll', value=poll_answer.option_ids[0])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посетить магазин 💵"))
    nmarkup.row(types.KeyboardButton(text="Откуда такие цифры?🤔"))
    text = await sql_safe_select("text", "texts", {"name": "shop_after_first_poll"})
    # result= (right_answers*100)/all_answers
    # txt = CoolPercReplacer(text, all_answers)
    # txt.replace('AA', right_answers)
    await bot.send_message(poll_answer.user.id, text,
                           reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(Shop.after_first_poll, F.text.contains("Посетить магазин"), flags=flags)
async def shop_transfer(message: types.Message, state: FSMContext):
    # await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_transfer', value="+")
    await state.set_state(Shop.shop_transfer)
    text = await sql_safe_select("text", "texts", {"name": "shop_transfer"})
    day = 203
    sum = day * 55000000000
    await state.update_data(balance=sum)
    await state.update_data(balance_all=sum)
    text = text.replace("NN", f"{day}")
    text = text.replace("MM", f"{sum}")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти к покупкам 🛒"))
    nmarkup.row(types.KeyboardButton(text="Откуда такие цифры?🤔"))
    await state.update_data(seen_child_message="0")
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(Shop.shop_transfer, F.text.contains("Откуда такие цифры?"), flags=flags)
@router.message(Shop.after_first_poll, F.text.contains("Откуда такие цифры?"), flags=flags)
async def shop_why_so_many(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_why_so_many', value="+")
    await state.set_state(Shop.shop_why_so_many)
    text = await sql_safe_select("text", "texts", {"name": "shop_why_so_many"})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти к покупкам 🛒"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(Shop.shop_transfer, F.text.contains("Перейти к покупкам"), flags=flags)
@router.message(Shop.shop_why_so_many, F.text.contains("Перейти к покупкам"), flags=flags)
async def shop_bucket(message: types.Message, state: FSMContext):
    # await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_bucket', value="+")
    await state.set_state(Shop.shop_bucket)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Выйти из магазина ⬇"))

    await message.answer("Отлично!", reply_markup=nmarkup.as_markup(resize_keyboard=True))
    text = await sql_safe_select("text", "texts", {"name": "shop_bucket"})

    data_dict = await state.get_data()
    for key in data_dict:
        text = text.replace(f"[{key}]", f"{data_dict[key]}")
    text = re.sub(r'\[[^\]]+\]', '0', text)
    text = text.replace("MM", f"{data_dict['balance']}")

    bot_message = await message.answer(text, reply_markup=inline.as_markup(resize_keyboard=True),
                                       disable_web_page_preview=True)  # TODO СДЕЛАТЬ АЛЬБОМ

    # nmarkup_quit = ReplyKeyboardBuilder()
    # nmarkup_quit.row(types.KeyboardButton(text="Выйти из магазина ⬇"))
    # balance_message = await message.answer(text=f"           БАЛАНС: {data_dict['balance']}", reply_markup=nmarkup_quit.as_markup(resize_keyboard=True))
    print(bot_message.message_id)
    print(bot_message.from_user.id)
    await state.update_data(message_id_shop=bot_message.message_id)
    await state.update_data(chat_id_shop=message.from_user.id)
    # await state.update_data(balance_message=balance_message.message_id)
    shop_text = await sql_safe_select("text", "texts", {"name": "shop_bucket"})
    await state.update_data(text_shop=shop_text)


@router.callback_query(Shop.shop_bucket)
@router.callback_query(Shop.shop_callback)
async def shop_callback(query: types.CallbackQuery, bot: Bot, state: FSMContext):
    global count, text, balance
    await query.answer(" ")
    await state.set_state(Shop.shop_callback)

    text = ((await state.get_data())["text_shop"])
    message_id_shop = (await state.get_data())['message_id_shop']
    chat_id = (await state.get_data())['chat_id_shop']
    data = query.data

    if data[0] == "1":

        word_list = query.data.split()
        num_list = []
        for word in word_list:
            if word.isnumeric():
                num_list.append(int(word))
        try:
            count = (await state.get_data())[f"{data}"]
        except Exception:
            count = 0
            await state.update_data({f"{data}": f"{int(count)}"})

        try:
            data_dict = await state.get_data()
            await state.update_data(balance=int(data_dict['balance']) - (price_dict[f'{query.data}'] * num_list[0]))
        except:
            print("о или о")
        balance = (await state.get_data())['balance']
        print(balance)
        data_dict = await state.get_data()
        if int(balance) > 0:

            try:
                print(f"{int(count)}" + "+" + f"{num_list[0]}")
                await state.update_data({f"{data}": f"{int(count) + num_list[0]}"})
            except Exception as e:
                print(e)
            data_dict = await state.get_data()
            for key in data_dict:
                text = text.replace(f"[{key}]", f"{data_dict[key]}")
            text = re.sub(r'\[[^\]]+\]', '0', text)
            text = text.replace("MM", f"{balance}")
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                        reply_markup=inline.as_markup())


        else:
            balance = 0
            await state.update_data(balance=balance)
            for key in data_dict:
                text = text.replace(f"[{key}]", f"{data_dict[key]}")
            text = re.sub(r'\[[^\]]+\]', '0', text)
            text = text.replace("MM", f"{balance}")
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                        reply_markup=inline.as_markup())

        print(int(data_dict["100 x 🧸 Спасти жизнь ребёнку"]))
        seen_cild_message = (await state.get_data())["seen_child_message"]
        print(seen_cild_message)
        if int(data_dict["100 x 🧸 Спасти жизнь ребёнку"]) > 7000:
            print(type(seen_cild_message))
            if seen_cild_message == "0":
                print(seen_cild_message)
                nmarkup = ReplyKeyboardBuilder()
                nmarkup.row(types.KeyboardButton(text="Отлично!"))
                child_text = "Поздравляю! Вы спасли всех тяжелобольных детей в России. Больши ни одному родителю не придётся собирать деньги на лечение ребёнка через фонды, группы ВК и чаты в Whatsapp."
                child_message = await bot.send_message(text=child_text, chat_id=chat_id,
                                                       reply_markup=nmarkup.as_markup(resize_keyboard=True))
                await state.update_data(child_message=child_message.message_id)
                await state.update_data(seen_child_message="1")

    if query.data == "Очистить корзину":
        print(query.data)
        data_dict = await state.get_data()

        for key in data_dict:
            if key[0] == '1':
                await state.update_data({f"{key}": "0"})
        await state.update_data(balance=data_dict["balance_all"])
        data_dict = await state.get_data()
        balance = (await state.get_data())['balance']
        for key in data_dict:
            text = text.replace(f"[{key}]", f"{data_dict[key]}")
        text = re.sub(r'\[[^\]]+\]', '0', text)
        text = text.replace("MM", f"{balance}")
        await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                    reply_markup=inline.as_markup())
    if query.data == "Оформить заказ":
        print(query.data)
        balance = (await state.get_data())['balance']
        balance_all=(await state.get_data())['balance_all']
        low_amount = int(balance_all) * 0.2
        print(low_amount)
        if balance < low_amount:
            nmarkup = ReplyKeyboardBuilder()
            nmarkup.row(types.KeyboardButton(text="Понятно 👌"))
            await bot.send_message(
                text="<b>Невозможно оформить заказ.</b> К сожалению, пока вы выбирали товары, наша страна уже потратила эти деньги на войну. 🤷‍♂️",
                chat_id=chat_id,
                reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
        if balance > low_amount:
            nmarkup = ReplyKeyboardBuilder()
            nmarkup.row(types.KeyboardButton(text="Вернуться в магазин 🛒"))
            nmarkup.row(types.KeyboardButton(text="Да, оформить заказ"))
            await bot.send_message(
                text="Уверены? Вы потратили ещё не все деньги!",
                chat_id=chat_id,
                reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")



    data_dict = await state.get_data()
    await mongo_update_stat_new(tg_id=chat_id, column='shop_callback', value=data_dict['balance'])


@router.message(Shop.shop_callback, F.text.contains("Отлично"), flags=flags)
async def shop_children_ok(message: types.Message, bot: Bot, state: FSMContext):
    message_id = (await state.get_data())['child_message']
    chat_id = (await state.get_data())['chat_id_shop']
    await bot.delete_message(chat_id, message_id)

@router.message(Shop.shop_callback, F.text.contains("Вернуться в магазин 🛒"), flags=flags)
@router.message(Shop.shop_bucket, (F.text.contains("Вернуться в магазин 🛒")|F.text.contains("Да, выйти ⬇")), flags=flags)
async def shop_go_back(message: types.Message, bot: Bot, state: FSMContext):
    chat_id = (await state.get_data())['chat_id_shop']
    await bot.delete_message(chat_id,message.message_id-1)


@router.message(Shop.shop_callback, F.text.contains("Выйти из магазина ⬇"), flags=flags)
@router.message(Shop.shop_bucket, F.text.contains("Выйти из магазина ⬇"), flags=flags)
async def shop_out(message: types.Message, bot: Bot, state: FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в магазин 🛒"))
    nmarkup.row(types.KeyboardButton(text="Да, выйти ⬇"))
    await message.answer("Уверены? Вы ещё не оформили заказ!", reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message((F.text.contains('Да, оформить заказ')), state=Shop.shop_callback)
async def shop_bucket(message: types.Message, bot: Bot, state: FSMContext):
    chat_id = (await state.get_data())['chat_id_shop']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Понятно 👌"))
    await bot.send_message(
        text="<b>Невозможно оформить заказ.</b> К сожалению, пока вы выбирали товары, наша страна уже потратила эти деньги на войну. 🤷‍♂️",
        chat_id=chat_id,
        reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")