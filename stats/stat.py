from bata import all_data
from log import logg


client = all_data().get_mongo()
database = client['database']
collection_stat = database['statistics']
collection_stat_all = database['userinfo']

async def mongo_stat(tg_id):
    try:
        user_answer = {'_id': int(tg_id), 'come': 1,  'start': 0, 'antiprop': 0, 'donbass': 0,
                       'war_aims': 0, 'putin': 0, 'faith': 'none', 'political_view': 'none', 'end': 0,
                       'nazi': 0, 'prevent_strike': 0}
        collection_stat.insert_one(user_answer)
    except Exception as error:
        pass


async def mongo_update_stat(tg_id, column, options='$set', value=1):
    try:
        collection_stat.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update_stat | {error}", __file__)


async def mongo_select_stat():
    try:
        count_dict={}
        count_dict['start'] = int(collection_stat.count_documents({'start': {'$gte':1}}))
        count_dict['antiprop'] = int(collection_stat.count_documents({'antiprop': {'$gte':1}}))
        count_dict['donbass'] = int(collection_stat.count_documents({'donbass': {'$gte':1}}))
        count_dict['war_aims'] = int(collection_stat.count_documents({'war_aims': {'$gte':1}}))
        count_dict['putin'] = int(collection_stat.count_documents({'putin': {'$gte':1}}))
        count_dict['end'] = int(collection_stat.count_documents({'end': {'$gte':1}}))

        count_dict['victim_warsupp']=int(collection_stat.count_documents({'$and': [{'faith': 'victim'}, {'political_view': 'warsupp'}]}))
        count_dict['victim_oppos']=int(collection_stat.count_documents({'$and': [{'faith': 'victim'}, {'political_view': 'oppos'}]}))
        count_dict['victim_apolitical']=int(collection_stat.count_documents({'$and': [{'faith': 'victim'}, {'political_view': 'apolitical'}]}))
        count_dict['kinginfo_warsupp']=int(collection_stat.count_documents({'$and': [{'faith': 'kinginfo'}, {'political_view': 'warsupp'}]}))
        count_dict['kinginfo_oppos']=int(collection_stat.count_documents({'$and': [{'faith': 'kinginfo'}, {'political_view': 'oppos'}]}))
        count_dict['kinginfo_warsupp']=int(collection_stat.count_documents({'$and': [{'faith': 'kinginfo'}, {'political_view': 'warsupp'}]}))
        count_dict['start_warsupp']=int(collection_stat.count_documents({'$and': [{'faith': 'foma'}, {'political_view': 'warsupp'}]}))
        count_dict['start_oppos']=int(collection_stat.count_documents({'$and': [{'faith': 'foma'}, {'political_view': 'oppos'}]}))
        count_dict['start_warsupp']=int(collection_stat.count_documents({'$and': [{'faith': 'foma'}, {'political_view': 'warsupp'}]}))
        return count_dict
    except Exception as error:
        await logg.get_error(f"mongo_select_stat | {error}", __file__)
        return False

async def mongo_select_stat_all_user():
    try:
        lst=[]
        for answer in collection_stat_all.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select_stat_all_user | {error}", __file__)


async def mongo_is_done(p_id):
    try:
        collection = collection_stat.find_one({'_id': p_id})
        return collection['end']
    except Exception as error:
        await logg.get_error(f"mongo_select_stat_all_user | {error}", __file__)
