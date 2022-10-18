import datetime
import re

import aiohttp
from aiogram.types import User
from pymongo.errors import DuplicateKeyError

from bata import all_data
from data_base.DBuse import mongo_select_info, data_getter, sql_add_value, mongo_user_info, mongo_easy_upsert
from filters.isAdmin import IsAdmin
from log import logg

client = all_data().get_mongo()
database = client.database
collection_stat = database['statistics']
collection_stat_new = database['statistics_new']
collection_stat_all = database['userinfo']


async def mongo_stat(tg_id):
    try:
        user_answer = {'_id': int(tg_id), 'come': 1}
        await collection_stat.insert_one(user_answer)
    except Exception as error:
        print(error)


async def mongo_stat_new(tg_id):
    try:
        user_answer = {'_id': int(tg_id), 'datetime': datetime.datetime.now(), 'come': True}
        await collection_stat_new.insert_one(user_answer)
    except Exception as error:
        print(error)


async def mongo_update_stat_new(tg_id, column, options='$set', value=True):
    try:
        conditions_dict = {'_id': int(tg_id), column: {'$exists': False}}
        if await IsAdmin(level=['Тестирование'], custom_user_id=tg_id)():
            del conditions_dict[column]
        await collection_stat_new.update_one(conditions_dict, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update_stat | {error}", __file__)


async def mongo_update_stat(tg_id, column, options='$set', value=1):
    try:
        await collection_stat.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update_stat | {error}", __file__)


async def mongo_select_stat():
    try:
        count_dict = {'start': int(await collection_stat.count_documents({'start': {'$gte': 1}})),
                      'antiprop': int(await collection_stat.count_documents({'antiprop': {'$gte': 1}})),
                      'donbass': int(await collection_stat.count_documents({'donbass': {'$gte': 1}})),
                      'war_aims': int(await collection_stat.count_documents({'war_aims': {'$gte': 1}})),
                      'putin': int(await collection_stat.count_documents({'putin': {'$gte': 1}})),
                      'end': int(await collection_stat.count_documents({'end': {'$gte': 1}}))}
        return count_dict
    except Exception as error:
        await logg.get_error(f"mongo_select_stat | {error}", __file__)
        return False


async def mongo_select_stat_all_user():
    try:
        lst = []
        async for answer in collection_stat_all.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select_stat_all_user | {error}", __file__)


async def mongo_is_done(p_id):
    try:
        collection = await collection_stat.find_one({'_id': p_id})
        return collection['end']
    except KeyError:
        pass


async def advertising_value(tag, user: User):
    origin = ''
    if re.search("^adv_", tag):
        all_tags = await data_getter("SELECT id FROM dumbstats.advertising")
        for row in all_tags:
            if tag in row:
                await sql_add_value("dumbstats.advertising", "count", {"id": tag})
        origin = 'Internal'
    elif tag.isdigit():
        if int(tag) != user.id:
            origin = 'Referal'
            await mongo_user_info(user.id, user.username)
            await mongo_easy_upsert('database', 'userinfo', {'_id': user.id},
                                    {'ref_parent': tag,  'name_surname': user.full_name})
    else:
        origin = 'Tracker'
        url = f'https://pravdobot.com/cx79l1k.php?cnv_id={tag}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                status = response.status
                print(status)
    await mongo_stat_new(user.id)
    await mongo_update_stat_new(user.id, 'origin', value=origin)
