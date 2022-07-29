import asyncio
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bata import all_data
from data_base.DBuse import mongo_update_viewed_news

router = Router()
data = all_data()
bot = data.get_bot()


async def start_spam(datet):
    date = datetime.strptime(datet, '%Y.%m.%d %H:%M')
    client = data.get_mongo()
    database = client['database']
    all_mass_media_main = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    userinfo = database['userinfo']
    main_news_base = tuple(all_mass_media_main.find())
    today_actual = actual_mass_media.find_one({'datetime': {'$eq': date}})
    main_news_ids = list()
    for n in main_news_base:
        main_news_ids.append(n['_id'])

    async for user in userinfo.find({'datetime_end': {'$lt': datetime.utcnow() - timedelta(days=1)}}):
        if all_data().get_data_red().get(f"user_last_answer: {user['_id']}:") != '1':
            asyncio.create_task(news_for_user(user, main_news_base, today_actual, main_news_ids))
            print("Задача для спама создана")
        else:
            asyncio.create_task(latecomers(user, main_news_base, today_actual, main_news_ids))
            print("Задача для очереди создана")
        await asyncio.sleep(0.033)


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
            print('ОТПРАВКА АКТУАЛЬНОГО СООБЩЕНИЯ', today_actual['media'], today_actual['caption'])
        else:
            print('Актуальных новостей сегодня нет')
    else:
        list_not_view = [i for i in main_news_ids if i not in user_viewed_news]
        if list_not_view:
            for main_news in main_news_base:
                if main_news['_id'] == list_not_view[0]:
                    await send_spam(user_id=user_id, media_id=main_news['media'], caption=main_news['caption'])
                    print('ОТПРАВКА ГЛАВНОГО СООБЩЕНИЯ', main_news['media'], main_news['caption'])
                    await mongo_update_viewed_news(user_id, main_news['_id'])
                    print('ЗАПИСЬ АЙДИШНИКА НОВОСТИ В МОНГУ', user_id, list_not_view[0])

        else:
            print('Главные новости для пользователя кончились, а актуальной не было')


async def send_spam(user_id, media_id, caption):
    try:
        if str(caption) != 'None':
            try:
                await bot.send_video(chat_id=int(user_id), video=str(media_id), caption=str(caption))
            except TelegramBadRequest:
                await bot.send_photo(chat_id=int(user_id), photo=str(media_id), caption=str(caption))
        else:
            try:
                await bot.send_video(chat_id=int(user_id), video=media_id)
            except TelegramBadRequest:
                await bot.send_photo(chat_id=int(user_id), photo=media_id)
    except TelegramForbiddenError:
        print(f"ПОЛЬЗОВАТЕЛЬ {user_id} -- Заблокировал бота")
