import re

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InputMediaPhoto, ReplyKeyboardRemove

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import sql_safe_select, mongo_count_docs
from utils.elk_logger import Logger
from utilts import CoolPercReplacer, change_number_format

from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import sql_safe_select, mongo_count_docs
from resources.all_polls import shop_poll
from states.true_goals_states import Shop, TrueGoalsState
from utilts import CoolPercReplacer
import re

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=(Shop, TrueGoalsState.before_shop,TrueGoalsState.main))
router.poll_answer.filter(state=Shop)
router.callback_query.filter(state=Shop)

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
inline.button(text='1000 x 🚀' ,
              callback_data='1000 x 🚀 Детская площадка',)
inline.button(text='100 x 🏫',
              callback_data='100 x 🏫 Современная школа')
inline.button(text='1000 x ⚡',
              callback_data='1000 x ⚡️ Электробус')
inline.button(text='10 x 🛩',
              callback_data='10 x 🛩 Пассажирский самолёт (SuperJet)')
inline.button(text='100 км x 🛣 ',
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

inline.adjust(3,3,4)

inline2 = InlineKeyboardBuilder()
inline2.button(text='Очистить корзину',
              callback_data='Очистить корзину')
inline2.button(text='Оформить заказ',
              callback_data='Оформить заказ')
inline2.adjust(2)


@router.message((F.text.in_({'Продолжай ⏳', 'Хорошо 🤝', '*презрительно хмыкнуть* 🤨'})),
                state=TrueGoalsState.before_shop, flags=flags)
async def shop_welcome(message: types.Message, state: FSMContext):
    print("in shop")
    await state.set_state(Shop.main)
    text = await sql_safe_select("text", "texts", {"name": "shop_welcome"})
    await message.answer(text, disable_web_page_preview=True)
    await message.answer_poll("Как думаете, сколько денег Россия уже потратила на войну?", explanation_parse_mode="HTML",
                              options=shop_poll, correct_option_id=2, is_anonymous=False, type='quiz',
                              reply_markup=ReplyKeyboardRemove())
    Logger.log("TEST TEST TEST")


@router.poll_answer(state=Shop.main, flags=flags)
async def shop_after_first_poll(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='shop_after_first_poll',
                                value=poll_answer.option_ids[0])
    print(poll_answer.option_ids[0])
    right_answers = await mongo_count_docs('database', 'statistics_new', {'shop_after_first_poll': 2})
    all_answers = await mongo_count_docs('database', 'statistics_new', {'shop_after_first_poll': {'$exists': True}})
    await state.set_state(Shop.after_first_poll)
    await state.update_data(shop_after_first_poll=poll_answer.option_ids[0])
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='shop_after_first_poll', value=poll_answer.option_ids[0])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посетить магазин 💵"))
    nmarkup.row(types.KeyboardButton(text="Откуда такие цифры?🤔"))
    text = await sql_safe_select("text", "texts", {"name": "shop_after_first_poll"})
    result=(right_answers*100)/all_answers
    print(f'all {all_answers}')
    print(f'right {right_answers}')
    print(result)
    text = text.replace("AA", f"{str(result)[:-2]}")
    print(text)
    await bot.send_message(poll_answer.user.id, text,
                           reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(Shop.after_first_poll, F.text.contains("Посетить магазин"), flags=flags)
@router.message(Shop.shop_why_so_many, F.text.contains("Посетить магазин"), flags=flags)
async def shop_transfer(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_transfer', value="+")
    await state.set_state(Shop.shop_transfer)
    text = await sql_safe_select("text", "texts", {"name": "shop_transfer"})
    day = 209
    sum = day * 55000000000
    # now = datetime.datetime.now().date()
    # old = datetime.datetime(year=2022, month=2, day=24).date()
    # day = now-old
    # print(day)
    day=203
    sum = 203 * 55000000000
    await state.update_data(balance=sum)
    await state.update_data(balance_all=sum)
    balance=change_number_format(sum)
    text = text.replace("NN", f"{day}")
    text = text.replace("MM", f"{balance}")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти к покупкам 🛒"))
    nmarkup.row(types.KeyboardButton(text="Откуда такие цифры?🤔"))
    await state.update_data(seen_child_message="0")
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(Shop.shop_transfer, F.text.contains("Откуда такие цифры?"), flags=flags)
async def shop_why_so_many(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_why_so_many', value="+")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Перейти к покупкам 🛒"))
    await state.set_state(Shop.shop_why_so_many)
    text = await sql_safe_select("text", "texts", {"name": "shop_why_so_many"})

    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message(Shop.after_first_poll, F.text.contains("Откуда такие цифры?"), flags=flags)
async def shop_why_so_many(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_why_so_many', value="+")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посетить магазин 💵"))
    await state.set_state(Shop.shop_why_so_many)
    text = await sql_safe_select("text", "texts", {"name": "shop_why_so_many"})

    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(Shop.shop_transfer, F.text.contains("Перейти к покупкам"), flags=flags)
@router.message(Shop.shop_why_so_many, F.text.contains("Перейти к покупкам"), flags=flags)
async def shop_bucket(message: types.Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='shop_bucket', value="+")
    await state.set_state(Shop.shop_bucket)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Выйти из магазина ⬇"))
    await message.answer("Добро пожаловать!", reply_markup=nmarkup.as_markup(resize_keyboard=True))

    tag_list=['card1',
              'card2',
              'card3',
              'card4',
              'card5',
              'card6',
              'card7',
              'card8',
              'card9',
              'card10',]
    asset_list=[]
    for tag in tag_list:
        asset = await sql_safe_select("t_id","assets",{"name":tag})
        asset_list.append(InputMediaPhoto(media=asset))
    try:
        await message.answer_media_group(asset_list)
    except Exception as e:
        print(e)




    text = await sql_safe_select("text", "texts", {"name": "shop_bucket"})
    check_text=""
    data_dict = await state.get_data()
    for key in data_dict:
        text = text.replace(f"[{key}]", f"{data_dict[key]}")
        if key[0] == "1":
            word_list = key.split()
            num_list = []
            for word in word_list:
                if word.isnumeric():
                    num_list.append(int(word))
            good = key.replace(str(num_list[0]), "")
            if data_dict[key]!="0":
                check_text=check_text+f"<b>{data_dict[key]}</b> {good} "+"\n"
    text = re.sub(r'\[[^\]]+\]', '0', text)
    text = text.replace("MM", f"{change_number_format(data_dict['balance'])}")

    bot_message = await message.answer(text, reply_markup=inline.as_markup(resize_keyboard=True),
                                       disable_web_page_preview=True)  # TODO СДЕЛАТЬ АЛЬБОМ


    await message.answer(text=f"<b>БАЛАНС</b>:   <i>{change_number_format(data_dict['balance'])} руб                                                          💵</i>\n\n{check_text}",reply_markup=inline2.as_markup(resize_keyboard=True))


    print(bot_message.message_id)
    print(bot_message.from_user.id)
    await state.update_data(message_id_shop=bot_message.message_id)
    await state.update_data(chat_id_shop=message.from_user.id)
    shop_text = await sql_safe_select("text", "texts", {"name": "shop_bucket"})
    await state.update_data(text_shop=shop_text)


@router.callback_query(Shop.shop_bucket)
@router.callback_query(Shop.shop_callback)
@router.callback_query(TrueGoalsState.main)
async def shop_callback(query: types.CallbackQuery, bot: Bot, state: FSMContext):
    global count, text, balance, check_text
    await query.answer()
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
        check_text=""
        if int(balance) > 0:

            try:
                print(f"{int(count)}" + "+" + f"{num_list[0]}")
                await state.update_data({f"{data}": f"{int(count) + num_list[0]}"})
            except Exception as e:
                print(e)
            data_dict = await state.get_data()
            for key in data_dict:
                text = text.replace(f"[{key}]", f"{data_dict[key]}")
                print(data_dict[key])

                if key[0] == "1":
                    word_list = key.split()
                    num_list = []
                    for word in word_list:
                        if word.isnumeric():
                            num_list.append(int(word))
                    good=key.replace(str(num_list[0]),"")
                    print(data_dict[key])
                    if int(data_dict[key]) > 0:
                        check_text=check_text+f"<b>{data_dict[key]}</b> {good} "+"\n"
                        print(check_text)
            text = re.sub(r'\[[^\]]+\]', '0', text)
            text = text.replace("MM", f"{change_number_format(balance)}")
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                        reply_markup=inline.as_markup())

            await bot.edit_message_text(text=f"<b>БАЛАНС</b>:   <i>{change_number_format(data_dict['balance'])} руб                                                          💵</i>\n\n{check_text}",
                                        chat_id=chat_id,
                                        message_id=(message_id_shop+1),
                                        reply_markup=inline2.as_markup(resize_keyboard=True))


        else:
            balance = 0
            await state.update_data(balance=balance)
            for key in data_dict:
                text = text.replace(f"[{key}]", f"{data_dict[key]}")
                if key[0] == "1":
                    word_list = key.split()
                    num_list = []
                    for word in word_list:
                        if word.isnumeric():
                            num_list.append(int(word))
                    good=key.replace(str(num_list[0]),"")
                    print(data_dict[key])
                    if int(data_dict[key]) > 0:
                        check_text=check_text+f"<b>{data_dict[key]}</b> {good} "+"\n"
                        print(check_text)
            text = re.sub(r'\[[^\]]+\]', '0', text)
            text = text.replace("MM", f"{change_number_format(balance)}")
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                        reply_markup=inline.as_markup())
            await bot.edit_message_text(
                text=f"<b>БАЛАНС</b>:   <i>0 руб                                                          💵</i>\n\n{check_text}",
                chat_id=chat_id,
                message_id=(message_id_shop + 1),
            reply_markup=inline2.as_markup(resize_keyboard=True))

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
            if key[0] == "1":
                check_text = check_text + f"{key} : {data_dict[key]}" + "\n"
        text = re.sub(r'\[[^\]]+\]', '0', text)
        text = text.replace("MM", f"{balance}")
        await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id_shop,  # TODO СДЕЛАТЬ АЛЬБОМ
                                    reply_markup=inline.as_markup())
        print("123")
        await bot.edit_message_text(
            text=f"<b>БАЛАНС</b>:   <i>{data_dict['balance_all']} руб                                                          💵</i>\n\n",
            chat_id=chat_id,
            message_id=(message_id_shop + 1),
        reply_markup=inline2.as_markup(resize_keyboard=True))

    if query.data == "Оформить заказ":
        print(query.data)
        balance = (await state.get_data())['balance']
        balance_all = (await state.get_data())['balance_all']
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


@router.message(Shop.shop_callback, F.text.contains("Вернуться в магазин"), flags=flags)
@router.message(Shop.shop_bucket, (F.text.contains("Вернуться в магазин") | F.text.contains("Да, выйти ⬇")), flags=flags)
@router.message(TrueGoalsState.main, F.text.contains("Вернуться в магазин"), flags=flags)
async def shop_go_back(message: types.Message, bot: Bot, state: FSMContext):
    chat_id = (await state.get_data())['chat_id_shop']
    await state.set_state(Shop.shop_bucket)
    await bot.delete_message(chat_id,message.message_id-1)

@router.message(Shop.shop_callback, F.text.contains("Вернуться в магазин 🛒"), flags=flags)
@router.message(Shop.shop_bucket, (F.text.contains("Вернуться в магазин 🛒") | F.text.contains("Да, выйти ⬇")),
                flags=flags)
async def shop_go_back(message: types.Message, bot: Bot, state: FSMContext):
    chat_id = (await state.get_data())['chat_id_shop']
    await bot.delete_message(chat_id, message.message_id - 1)


@router.message(Shop.shop_callback, F.text.contains("Выйти из магазина ⬇"), flags=flags)
@router.message(Shop.shop_bucket, F.text.contains("Выйти из магазина ⬇"), flags=flags)
async def shop_out(message: types.Message, bot: Bot, state: FSMContext):
    await state.set_state(TrueGoalsState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернуться в магазин 🛒"))
    nmarkup.row(types.KeyboardButton(text="Да, выйти ⬇"))
    await message.answer("Уверены? Вы ещё не оформили заказ!", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Да, оформить заказ')), state=Shop.shop_callback)
async def shop_bucket(message: types.Message, bot: Bot, state: FSMContext):
    await state.set_state(TrueGoalsState.main)
    chat_id = (await state.get_data())['chat_id_shop']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Понятно 👌"))
    await bot.send_message(
        text="<b>Невозможно оформить заказ.</b> К сожалению, пока вы выбирали товары, наша страна уже потратила эти деньги на войну. 🤷‍♂️",
        chat_id=chat_id,
        reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
