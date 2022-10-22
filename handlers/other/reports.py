import datetime
from aiogram import Router
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bata import all_data
from data_base.DBuse import redis_just_one_read, mongo_ez_find_one, mongo_easy_upsert

flags = {"throttling_key": "True"}
router = Router()
data = all_data()
bot = data.get_bot()
client = all_data().get_mongo()
database = client.database
collection_reports = database['reports']
channel_for_reports = -1001563584793


@router.message(commands=['report'], state='*')
async def report(message: types.Message):
    user_report_str = await redis_just_one_read(f'report: Users: {message.chat.id}')
    user_report_dict = eval(user_report_str)
    date_message = user_report_dict['date_message']
    user_id = user_report_dict['user_id']
    username = user_report_dict['username']
    state = user_report_dict['state']
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='Показать чат', callback_data=f'report_chat {user_id} {date_message}')
    nmarkup.button(text='Закрыть репорт', callback_data=f'close_report {user_id} {date_message}')
    report = await bot.send_message(channel_for_reports, f"🔴 New user report 🔴\n\n"
                                                            f"User: @{username}\n"
                                                            f"User_id: {user_id}\n"
                                                            f"State: {state}\n"
                                                            f"Date_message: {date_message}",
                                    reply_markup=nmarkup.as_markup())

    user_report_dict['report_id'] = report.message_id
    await report_mongo(user_report_dict)
    await message.answer('Спасибо, ваш отчет об ошибке отправлен разработчикам.')


async def report_mongo(user_report_dict):
    try:
        report_id = user_report_dict['report_id']
        user_id = user_report_dict['user_id']
        last_message = user_report_dict['last_message']
        date_message = user_report_dict['date_message']
        username = user_report_dict['username']
        state = user_report_dict['state']
        report_info = {'report_id': report_id, 'user_id': int(user_id), 'last_message': last_message,
                       'date_message': date_message,
                       'username': username, 'state': state}
        await collection_reports.insert_one(report_info)
    except Exception as error:
        print(error)


@router.callback_query(lambda call: "report_chat" in call.data)
async def report_chat(query: types.CallbackQuery):
    user_report = query.data.split()
    user_id = int(user_report[1])
    date_message = user_report[-2] + ' ' + user_report[-1]
    date_message = datetime.datetime.strptime(date_message, "%Y-%m-%d %H:%M:%S%z")
    user_report = await mongo_ez_find_one('database', 'reports', {'$and': [{'user_id': user_id}, {'date_message': date_message}]})
    user_id = user_report['user_id']
    username = user_report['username']
    state = user_report['state']
    report_id = user_report['report_id']
    from_chat_id = user_report['user_id']
    last_message_id = user_report['last_message']
    report_message_id_list = list()

    num = 0
    if int(last_message_id) >= 2:
        num = 2
        last_message_id = int(last_message_id) - 1

    if int(last_message_id) >= 4:
        num = 4
        last_message_id = int(last_message_id) - 3
    if int(last_message_id) >= 6:
        num = 6
        last_message_id = int(last_message_id) - 5

    try:
        for number_message in range(1, num):
            last_message_id = int(last_message_id) + 1
            print(number_message)
            try:
                message_report = await bot.forward_message(chat_id=channel_for_reports,
                                                       from_chat_id=from_chat_id, message_id=last_message_id)
                report_message_id_list.append(message_report.message_id)
            except Exception:
                bot.send_message(chat_id=channel_for_reports, text='This message cannot be forwarded')
        await mongo_easy_upsert('database', 'reports', {'$and': [{'user_id': user_id},
                                                                 {'date_message': date_message}]},
                                {'report_message_id_list': report_message_id_list})
        nmarkup = InlineKeyboardBuilder()
        nmarkup.button(text='Закрыть чат', callback_data=f'close_chat {user_id} {date_message}')
        nmarkup.button(text='Закрыть репорт', callback_data=f'close_report {user_id} {date_message}')
        await bot.edit_message_text(chat_id=channel_for_reports, message_id=int(report_id),
                                    text=f"🔴 New user report 🔴\n\n"
                                                             f"User: @{username}\n"
                                                             f"User_id: {user_id}\n"
                                                             f"State: {state}\n"
                                                             f"Date_message: {date_message}",
                                        reply_markup=nmarkup.as_markup())

    except Exception as e:
        await bot.send_message(chat_id=channel_for_reports, text=f'[ERROR]: {e}')


@router.callback_query(lambda call: "close_chat" in call.data)
async def close_report(query: types.CallbackQuery):
    user_report = query.data.split()
    user_id = int(user_report[1])
    date_message = user_report[-2] + ' ' + user_report[-1]
    date_message = datetime.datetime.strptime(date_message, "%Y-%m-%d %H:%M:%S%z")
    user_report = await mongo_ez_find_one('database', 'reports',
                                          {'$and': [{'user_id': user_id}, {'date_message': date_message}]})
    username = user_report['username']
    state = user_report['state']
    report_id = user_report['report_id']
    report_message_id_list = user_report['report_message_id_list']
    for i in report_message_id_list:
        try:
            await bot.delete_message(chat_id=channel_for_reports, message_id=i)
        except Exception:
            pass
    nmarkup = InlineKeyboardBuilder()
    nmarkup.button(text='Показать чат', callback_data=f'report_chat {user_id} {date_message}')
    nmarkup.button(text='Закрыть репорт', callback_data=f'close_report {user_id} {date_message}')
    await bot.edit_message_text(chat_id=channel_for_reports, message_id=int(report_id),
                                text=f"🔴 New user report 🔴\n\n"
                                     f"User: @{username}\n"
                                     f"User_id: {user_id}\n"
                                     f"State: {state}\n"
                                     f"Date_message: {date_message}",
                                reply_markup=nmarkup.as_markup())


@router.callback_query(lambda call:  "close_report" in call.data)
async def close_report(query: types.CallbackQuery):
    user_report = query.data.split()
    user_id = int(user_report[1])
    date_message = user_report[-2] + ' ' + user_report[-1]
    date_message = datetime.datetime.strptime(date_message, "%Y-%m-%d %H:%M:%S%z")

    user_report = await mongo_ez_find_one('database', 'reports',
                                          {'$and': [{'user_id': user_id}, {'date_message': date_message}]})

    username = user_report['username']
    state = user_report['state']
    report_id = user_report['report_id']
    report_message_id_list = user_report['report_message_id_list']
    for i in report_message_id_list:
        try:
            await bot.delete_message(chat_id=channel_for_reports, message_id=i)
        except Exception:
            pass
    await bot.edit_message_text(chat_id=channel_for_reports, message_id=int(report_id),
                                text=f"🟢 User report is done 🟢\n\n"
                                     f"User: @{username}\n"
                                     f"User_id: {user_id}\n"
                                     f"State: {state}\n"
                                     f"Date_message: {date_message}")