import asyncio
from datetime import datetime, timedelta
from typing import List, Union
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bata import all_data
from data_base.DBuse import poll_get, redis_just_one_read, mongo_update_viewed_news
from data_base.DBuse import sql_safe_select, data_getter, sql_safe_update
from filters.MapFilters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter, PoliticsFilter
from handlers import true_resons_hand
from keyboards.map_keys import antip_why_kb, antip_killme_kb
from resources.all_polls import web_prop
from resources.all_polls import channels
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_update_stat
from utilts import simple_media
from log import logg

router=Router()
data = all_data()
bot = data.get_bot()




async def start_spam(date):
    client = all_data().get_mongo()
    database = client['database']
    actual_collection = database['userinfo']
    all_mass_media_main = database['spam_news_main']
    all_main_media = []  # список всех новостей
    list_for_spam = []  # Лист для рассылки

    # все главные новости
    for media in all_mass_media_main.find():
        all_main_media.append(media['_id'])

    # все у кого прошло 24ч после окончания прохождения
    for i in actual_collection.find({'datetime': {'$lt': datetime.utcnow()-timedelta(days=1)}}):
        list_for_spam.append({i['_id']: i['viewed_news']})

    datet = datetime.strptime(date, '%Y.%m.%d %H:%M')
    #date = datetime.strptime('2022.07.12 11:00', '%Y.%m.%d %H:%M')
    await send_spam( all_main_media, list_for_spam, datet)




async def send_spam(all_main_media, list_for_spam, date):
    client = all_data().get_mongo()
    database = client['database']
    main_mass_media = database['spam_news_main']
    actual_mass_media = database['spam_actual_news']
    for user_for_spam in list_for_spam:
        for news_in_user in user_for_spam.values():
            #  если юзер посмотрел все главные новости
            if len(news_in_user) == len(all_main_media):
                await bot.send_message(list(user_for_spam.keys())[0], 'SPAM XA-XA-XA')
                media = actual_mass_media.find_one({'datetime': {'$eq': date}})
                try:
                    try:
                        await bot.send_photo(list(user_for_spam.keys())[0], photo=media['media'], caption=media['caption'])
                    except:
                        await bot.send_video(list(user_for_spam.keys())[0], photo=media['media'], caption=media['caption'])
                except Exception as er:
                    print(er)

            else:
                print(news_in_user)
                print(all_main_media)
                list_not_view = []
                for not_view in all_main_media:
                    if not_view not in news_in_user:
                        list_not_view.append(not_view)
                        print("Новость не просмотрена")
                print(list_not_view)
                if len(list_not_view) != 0:
                    media = main_mass_media.find_one({'_id': list_not_view[0]})
                    try:
                        try:
                            await bot.send_photo(list(user_for_spam.keys())[0], photo=media['media'], caption=media['caption'])
                        except:
                            await bot.send_video(list(user_for_spam.keys())[0], photo=media['media'], caption=media['caption'])
                    except Exception as er:
                        print(er)

                    await mongo_update_viewed_news(list(user_for_spam.keys())[0], list_not_view[0])
                else:
                    print("Тут ошибка. Лист list_not_view - пустой")

    print("Рассылка завершена")

async def latecomers(latecomers_list):
    pass




# {main_spam_1:[media:[], texts:[]]}, {main_spam_2:[media:[], texts:[]]}
# {topical_spam_1:[media:[], texts:[]]}, {topical_spam_2:[media:[], texts:[]]}
