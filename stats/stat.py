from bata import all_data
from log import logg


client = all_data().get_mongo()
database = client['database']
collection_stat = database['statistics']
collection_stat_all = database['userinfo']

async def mongo_stat(tg_id):
    try:
        user_answer = {'_id': int(tg_id), 'come': 1,  'start': 0, 'antiprop': 0, 'donbass': 0,
                       'war_aims': 0, 'putin': 0, 'faith': '', 'political_view': '', 'end': 0}
        collection_stat.insert_one(user_answer)
    except Exception as error:
        pass


async def mongo_update_stat(tg_id, column, options='$inc', value=1):
    try:
        collection_stat.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


async def mongo_select_stat():
    try:
        lst=[]
        for answer in collection_stat.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select | {error}", __file__)

async def mongo_select_stat_all_user():
    try:
        lst=[]
        for answer in collection_stat_all.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select | {error}", __file__)

