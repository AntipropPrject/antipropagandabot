import asyncio
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bata import all_data
from data_base.DBuse import mongo_update_viewed_news, mongo_pop_news, mongo_update, sql_safe_select
from log.logg import send_to_chat, get_logger

router = Router()
data = all_data()
bot = data.get_bot()

logger = get_logger('SPAM')


async def start_spam(datet):
    asyncio.create_task(send_to_chat("Рассылка началась"))
    logger.info("Функция рассылки запущена")
    print('start spam')
    date = datetime.strptime(datet, '%Y.%m.%d %H:%M')
    client = data.get_mongo()
    database = client['database']
    all_mass_media_main = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    userinfo = database['userinfo']
    main_news_base = all_mass_media_main.find()
    logger.info("Главные новости были получены")
    today_actual = await actual_mass_media.find_one({'datetime': {'$eq': date}})
    logger.info("Актуальные новости были получены новости были получены")

    main_news_ids = list()
    main_news_list = list()

    async for n in main_news_base:
        main_news_list.append(n)
        main_news_ids.append(n['_id'])
    count = 0
    logger.info('Начало рассылки')
    async for user in userinfo.find({'datetime_end': {'$lt': datetime.utcnow() - timedelta(days=1)}}):
        if all_data().get_data_red().get(f"user_last_answer: {user['_id']}:") != '1':
            asyncio.create_task(news_for_user(user, main_news_list, today_actual, main_news_ids))
            count += 1
        else:
            asyncio.create_task(latecomers(user, main_news_list, today_actual, main_news_ids))
            count += 1
        await asyncio.sleep(0.033)
    try:
        asyncio.create_task(mongo_pop_news(m_id=today_actual['media'], coll='actu'))
    except:
        pass
    logger.info(f'Рассылка завершена, сообщение получили {count}')
    asyncio.create_task(send_to_chat(f"Рассылка завершена\n\nБыло отправлено: +-{count} сообщений"))


async def latecomers(user, main_news_base, today_actual, main_news_ids):
    for comers in range(5):
        if all_data().get_data_red().get(f"user_last_answer: {user['_id']}:") != '1':
            await news_for_user(user, main_news_base, today_actual, main_news_ids)
            break
        await asyncio.sleep(300)


async def news_for_user(user, main_news_base, today_actual, main_news_ids):
    user_id = user['_id']
    user_viewed_news = user['viewed_news']
    if len(user_viewed_news) >= len(main_news_base):
        if today_actual is not None:
            await send_spam(user_id=user_id, media_id=today_actual['media'], caption=today_actual['caption'])
        else:
            return
    else:
        list_not_view = [i for i in main_news_ids if i not in user_viewed_news]
        if list_not_view:
            for main_news in main_news_base:
                if main_news['_id'] == list_not_view[0]:
                    await send_spam(user_id=user_id, media_id=main_news['media'], caption=main_news['caption'])
                    await mongo_update_viewed_news(user_id, main_news['_id'])

        else:
            print('Главные новости для пользователя кончились, а актуальной не было')


async def send_spam(user_id, caption, media_id=None):
    try:
        if caption and media_id is None:
            await bot.send_message(chat_id=int(user_id), text=caption)
        else:
            if caption:
                try:
                    await bot.send_video(chat_id=int(user_id), video=str(media_id), caption=str(caption))
                except TelegramBadRequest:
                    await bot.send_photo(chat_id=int(user_id), photo=str(media_id), caption=str(caption))
            else:
                try:
                    await bot.send_video(chat_id=int((user_id)), video=(media_id))
                except TelegramBadRequest:
                    await bot.send_photo(chat_id=int(user_id), photo=(media_id))
    except TelegramForbiddenError:
        await mongo_update(int(user_id), 'userinfo', 'is_ban')
        print(f"ПОЛЬЗОВАТЕЛЬ {user_id} -- Заблокировал бота")


async def user_returner():
    client = all_data().get_mongo()
    redis = all_data().get_data_red()
    database = client['database']
    collection = database['userinfo']
    cursor = collection.find({'datetime_end': None})
    list_of_users = await cursor.to_list(length=None)
    for user in list_of_users:
        redis.set(f'Must_return_list: {user["_id"]}:', user['datetime'])


async def return_spam_send():
    asyncio.create_task(return_spam_send_task(datetime.now()))


async def return_spam_send_task(time_now: datetime):
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Current_users:*"):
        user_time = datetime.strptime(redis.get(key), '%m/%d/%Y %H:%M:%S')
        past_time = time_now - user_time
        user = int(key.strip('Current_users: '))
        if timedelta(hours=22) < past_time < timedelta(hours=22, seconds=1):
            text = await sql_safe_select('text', 'texts', {'name': 'come_back_22'})
            await bot.send_message(user, text)
        elif timedelta(hours=22) < past_time < timedelta(hours=46, seconds=1):
            text = await sql_safe_select('text', 'texts', {'name': 'come_back_46'})
            await bot.send_message(user, text)
        elif timedelta(hours=22) < past_time < timedelta(hours=166, seconds=1):
            text = await sql_safe_select('text', 'texts', {'name': 'come_back_166'})
            await bot.send_message(user, text)
