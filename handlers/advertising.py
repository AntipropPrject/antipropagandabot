import asyncio
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bata import all_data
from data_base.DBuse import mongo_update_viewed_news, mongo_pop_news, mongo_update, redis_just_one_write, \
    redis_just_one_read, sql_safe_select, mongo_update_end, mongo_easy_upsert
from log.logg import send_to_chat, get_logger

router = Router()
data = all_data()
bot = data.get_bot()

logger = get_logger('SPAM')


async def start_spam():
    await redis_just_one_write('adversting: spam_count:', '0')
    asyncio.create_task(send_to_chat("Рассылка началась"))
    logger.info("Функция рассылки запущена")
    client = data.get_mongo()
    database = client['database']
    all_mass_media_main = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    userinfo = database['userinfo']
    main_news_base = all_mass_media_main.find()
    logger.info("Главные новости были получены")
    today_actual_object = actual_mass_media.find()
    logger.info("Актуальные новости были получены новости были получены")

    main_news_ids = list()
    main_news_list = list()
    today_actual = list()
    async for n in main_news_base:
        main_news_list.append(n)
        main_news_ids.append(n['_id'])

    async for n in today_actual_object:
        today_actual.append(n)
    logger.info('Начало рассылки')
    start_datetime_spam = datetime.now()
    async for user in userinfo.find({'datetime': {'$lt': datetime.utcnow() - timedelta(days=1)}}):
        if user.get('is_ban') is not True:
            if all_data().get_data_red().get(f"user_last_answer: {user['_id']}:") != '1':
                asyncio.create_task(news_for_user(user, main_news_list, today_actual, main_news_ids))
            else:
                asyncio.create_task(latecomers(user, main_news_list, today_actual, main_news_ids))
        await asyncio.sleep(0.033)

    try:
        asyncio.create_task(mongo_pop_news(m_id=today_actual[0]['media'], coll='actu'))
    except Exception:
        pass

    end_datetime_spam = datetime.now()
    result_spam_time = end_datetime_spam - start_datetime_spam
    count = int(await redis_just_one_read('adversting: spam_count:'))
    logger.info(f'Рассылка завершена, сообщение получили {count}')
    asyncio.create_task(send_to_chat(f"Рассылка завершена\n\nБыло отправлено: +-{count} сообщений\n"
                                     f"Время рассылки: {result_spam_time}"))


async def latecomers(user, main_news_base, today_actual, main_news_ids):
    for comers in range(5):
        if all_data().get_data_red().get(f"user_last_answer: {user['_id']}:") != '1':
            await news_for_user(user, main_news_base, today_actual, main_news_ids)
            break
        await asyncio.sleep(300)


async def news_for_user(user, main_news_base, today_actual, main_news_ids):
    user_id = user['_id']
    print(today_actual)
    print('start start')
    for news in main_news_base:
        print('0001')
        if news['_id'] not in user['viewed_news']:
            print('1111')
            await send_spam(user_id=user_id, media_id=news['media'], caption=news['caption'])
            await mongo_update_viewed_news(user_id, news['_id'])

        else:
            print('2222')
            if len(today_actual) != 0:
                print('3333')
                await send_spam(user_id=user_id, media_id=today_actual[0]['media'], caption=today_actual[0]['caption'])
            print('4444')

    return True



async def send_spam(user_id, caption, media_id=None):
    try:
        count = await redis_just_one_read('adversting: spam_count:')
        await redis_just_one_write('adversting: spam_count:', f'{int(count)+1 if count else 0}')
        if caption and media_id is None:
            await bot.send_message(chat_id=int(user_id), text=caption, disable_web_page_preview=True)
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
    except Exception as err:
        print(err)


async def return_spam_send_task(time_now: datetime):
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Current_users:*"):
        user_time = datetime.strptime(redis.get(key), '%m/%d/%Y %H:%M:%S')
        past_time = time_now - user_time
        user = int(key.strip('Current_users: '))
        try:
            if timedelta(hours=22) <= past_time <= timedelta(hours=22, seconds=1):
                text = await sql_safe_select('text', 'texts', {'name': 'come_back_22'})
                await bot.send_message(user, text)
            elif timedelta(hours=46) <= past_time <= timedelta(hours=46, seconds=1):
                text = await sql_safe_select('text', 'texts', {'name': 'come_back_46'})
                await bot.send_message(user, text)
            elif timedelta(hours=166) <= past_time <= timedelta(hours=166, seconds=1):
                text = await sql_safe_select('text', 'texts', {'name': 'come_back_166'})
                await mongo_update_end(user)
                await bot.send_message(user, text)
        except TelegramForbiddenError:
            redis.delete(key)
            await mongo_easy_upsert('database', 'userinfo', {'_id': user}, {'is_ban': True})
