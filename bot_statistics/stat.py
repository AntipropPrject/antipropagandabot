import datetime

import motor.motor_asyncio

from bata import all_data
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
        pass

async def mongo_stat_new(tg_id):
    try:
        user_answer = {'_id': int(tg_id), 'datetime': datetime.datetime.now(), 'come': True}
        await collection_stat_new.insert_one(user_answer)
    except Exception as error:
        pass


async def mongo_update_stat_new(tg_id, column, options='$set', value=True):
    try:
        await collection_stat_new.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update_stat | {error}", __file__)

async def mongo_update_stat(tg_id, column, options='$set', value=1):
    try:
        await collection_stat.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update_stat | {error}", __file__)


async def mongo_select_stat():
    try:
        count_dict={}
        count_dict['start'] = int(await collection_stat.count_documents({'start': {'$gte':1}}))
        count_dict['antiprop'] = int(await collection_stat.count_documents({'antiprop': {'$gte':1}}))
        count_dict['donbass'] = int(await collection_stat.count_documents({'donbass': {'$gte':1}}))
        count_dict['war_aims'] = int(await collection_stat.count_documents({'war_aims': {'$gte':1}}))
        count_dict['putin'] = int(await collection_stat.count_documents({'putin': {'$gte':1}}))
        count_dict['end'] = int(await collection_stat.count_documents({'end': {'$gte':1}}))

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
        document = await collection_stat.find_one({'_id': p_id})
        return document
    except Exception as error:
        await logg.get_error(f"MONGO MENU | {error}", __file__)
    try:
        collection = await collection_stat.find_one({'_id': p_id})
        return collection['end']
    except Exception as error:
        await logg.get_error(f"mongo_is_done | {error}", __file__)

