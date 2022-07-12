import asyncio
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest

from bata import all_data
from data_base.DBuse import mongo_update_viewed_news
from log import logg

router = Router()
data = all_data()
bot = data.get_bot()


async def start_spam(date):
    client = all_data().get_mongo()
    database = client['database']
    userinfo = database['userinfo']
    all_mass_media_main = database['spam_news_main']
    all_main_media = []  # список всех новостей
    list_for_spam = []  # Лист для рассылки

    # все главные новости
    for media in all_mass_media_main.find():
        all_main_media.append(media['_id'])

    # все у кого прошло 24ч после окончания прохождения
    for i in userinfo.find({'datetime_end': {'$lt': datetime.utcnow()-timedelta(days=1)}}):
        list_for_spam.append({i['_id']: i['viewed_news']})

    datet = datetime.strptime(date, '%Y.%m.%d %H:%M')
    #date = datetime.strptime('2022.07.12 11:00', '%Y.%m.%d %H:%M')
    await send_spam(all_main_media, list_for_spam, datet)


async def send_spam(all_main_media, list_for_spam, date):
    client = all_data().get_mongo()
    database = client['database']
    main_mass_media = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    for user_for_spam in list_for_spam:
        for news_in_user in user_for_spam.values():
            if all_data().get_data_red().get(f"user_last_answer: {list(user_for_spam.keys())[0]}:") != '1':
                #  если юзер посмотрел все главные новости
                if len(news_in_user) >= len(all_main_media):
                    user_id = list(user_for_spam.keys())[0]
                    media = actual_mass_media.find_one({'datetime': {'$eq': date}})
                    caption = media['caption']
                    try:
                        if str(caption) != 'None':
                            try:
                                await bot.send_photo(user_id, photo=media['media'], caption=caption)
                            except TelegramBadRequest:
                                await bot.send_video(user_id, video=media['media'], caption=caption)
                        else:
                            try:
                                await bot.send_photo(user_id, photo=media['media'])
                            except TelegramBadRequest:
                                await bot.send_video(user_id, video=media['media'])
                    except Exception as er:
                        await logg.get_error(er)
                else:
                    # лист главных новостей по порядку
                    list_not_view = []
                    for not_view in all_main_media:
                        if not_view not in news_in_user:
                            list_not_view.append(not_view)
                    if len(list_not_view) != 0:
                        media = main_mass_media.find_one({'_id': list_not_view[0]})
                        caption = media['caption']
                        try:
                            if str(caption) != 'None':
                                try:
                                    await bot.send_photo(user_id, photo=media['media'], caption=media['caption'])
                                except TelegramBadRequest:
                                    await bot.send_video(user_id, video=media['media'], caption=media['caption'])
                            else:
                                try:
                                    await bot.send_photo(user_id, photo=media['media'])
                                except TelegramBadRequest:
                                    await bot.send_video(user_id, video=media['media'])

                        except Exception as er:
                            await logg.get_error(er)

                        await mongo_update_viewed_news(user_id, list_not_view[0])
                    else:
                        await logg.get_error("Тут ошибка. Лист list_not_view - пустой")

            else:
                #  ждать интервал 15 мин 5 раз и потом скипать чела если не дожлались
                await latecomers_check_user(user_id, news_in_user, all_main_media, date)
    print("Рассылка завершена")


# именно тут может запуститься 100000000 потоков (но вроде нет)
async def latecomers_check_user(user_id, news_in_user, all_main_media, date):
    count = 5
    while count != 0:
        if all_data().get_data_red().get(f"user_last_answer: {user_id}:") != '1':
            await latecomers(user_id, news_in_user, all_main_media, date)
            break
        count -= 1
        await asyncio.sleep(900)


# функция опоздавших
async def latecomers(user_id, news_in_user, all_main_media, date):
    client = all_data().get_mongo()
    database = client['database']
    main_mass_media = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    if len(news_in_user) >= len(all_main_media):
        media = actual_mass_media.find_one({'datetime': {'$eq': date}})
        caption = media['caption']
        try:
            if str(caption) != 'none':
                try:
                    await bot.send_photo(user_id, photo=media['media'], caption=caption)
                except:
                    await bot.send_video(user_id, video=media['media'], caption=caption)
            else:
                try:
                    await bot.send_photo(user_id, photo=media['media'])
                except:
                    await bot.send_video(user_id, video=media['media'])
        except Exception as er:
            await logg.get_error(er)
    else:
        # лист главных новостей по порядку
        list_not_view = []
        for not_view in all_main_media:
            if not_view not in news_in_user:
                list_not_view.append(not_view)
        if len(list_not_view) != 0:
            media = main_mass_media.find_one({'_id': list_not_view[0]})
            caption = media['caption']
            try:
                if str(caption) != 'none':
                    try:
                        await bot.send_photo(user_id, photo=media['media'], caption=media['caption'])
                    except TelegramBadRequest:
                        await bot.send_video(user_id, video=media['media'], caption=media['caption'])
                else:
                    try:
                        await bot.send_photo(user_id, photo=media['media'])
                    except TelegramBadRequest:
                        await bot.send_video(user_id, video=media['media'])

            except Exception as er:
                await logg.get_error(er)

            await mongo_update_viewed_news(user_id, list_not_view[0])
        else:
            await logg.get_error('Тут ошибка. Лист list_not_view - пустой')
