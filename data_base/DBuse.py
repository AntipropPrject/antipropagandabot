from datetime import datetime

import psycopg2
from psycopg2 import sql

from bata import all_data
from data_base.connect_pool import get_cursor
from log import logg

"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^PostgreSQL^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""


async def data_getter(query):
    try:
        with get_cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
        return data
    except psycopg2.Error as error:
        return error


async def safe_data_getter(safe_query, values_dict):
    try:
        with get_cursor() as cur:
            cur.execute(safe_query, values_dict)
            data = cur.fetchall()
        return data
    except psycopg2.Error as error:
        return False


async def sql_delete(table_name, condition_dict):
    try:

        safe_query = sql.SQL("DELETE from {} WHERE {} = {};").format(sql.Identifier(table_name), sql.SQL(', ').join(
            map(sql.Identifier, condition_dict)), sql.SQL(", ").join(map(sql.Placeholder, condition_dict)))

        with get_cursor() as cur:
            cur.execute(safe_query, condition_dict)
    except (psycopg2.Error, IndexError) as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_select(column, table_name, condition_dict):
    try:
        ident_list = list()
        if isinstance(column, list):
            for i in column:
                ident_list.append(sql.Identifier(i))
        elif isinstance(column, str):
            ident_list.append(sql.Identifier(column))
        safe_query = sql.SQL("SELECT {col_names} from {} WHERE {} = {};").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier,
                                   condition_dict)),
            sql.SQL(", ").join(map(sql.Placeholder,
                                   condition_dict)),
            col_names=sql.SQL(',').join(ident_list)
        )
        with get_cursor() as cur:
            cur.execute(safe_query, condition_dict)
            data = cur.fetchall()
        if isinstance(column, list):
            return data[0]
        else:
            return data[0][0]
    except IndexError as err:
        logg.get_info(err)
        return False
    except (psycopg2.Error, IndexError) as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_insert(table_name, values_dict: dict):
    try:
        safe_query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(sql.Identifier(table_name),
                                                                        sql.SQL(', ').join(map(sql.Identifier,
                                                                                               values_dict)),
                                                                        sql.SQL(", ").join(map(sql.Placeholder,
                                                                                               values_dict)))
        with get_cursor() as cur:
            cur.execute(safe_query, values_dict)
    except (psycopg2.Error, IndexError) as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_select_like(column1, column2, table_name, first_condition, second_condition):
    try:
        safe_query = (f"SELECT {column1}"
                      f" from {table_name}"
                      f" WHERE {column2}"
                      f" LIKE '%{first_condition}%'"
                      f" AND {column2}"
                      f" LIKE '%{str(second_condition)[-5:-1].strip()}%'")

        with get_cursor() as cur:
            cur.execute(safe_query)
            data = cur.fetchall()
        return data
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_select_row_like(tablename, rownumber, like_dict: dict):
    try:
        key = list(like_dict.keys())[0]
        q = f"SELECT * FROM (SELECT *, row_number() over (ORDER BY {key}) FROM {tablename} WHERE " \
            f"{key} like '{like_dict[key]}%') AS sub WHERE row_number = {rownumber};"
        with get_cursor() as cur:
            cur.execute(q)
            data = cur.fetchall()
        return data[0]
    except (psycopg2.Error, IndexError) as error:
        return False


async def sql_games_row_selecter(tablename: str, row: int):
    try:
        if tablename == 'truthgame':
            data = (await data_getter(f"""SELECT * FROM (Select truth, a.t_id as plot_media, t.text as plot_text, 
                                             belivers, nonbelivers,
                                             t2.text as rebb_text, a2.t_id as rebb_media,
                                             ROW_NUMBER () OVER (ORDER BY id), id FROM public.{tablename}
                                             left outer join assets a on a.name = {tablename}.asset_name
                                             left outer join assets a2 on a2.name = {tablename}.reb_asset_name
                                             left outer join texts t on {tablename}.text_name = t.name
                                             left outer join texts t2 on {tablename}.rebuttal = t2.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = (
                'truth', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'rebb_text', 'rebb_media', 'ROW_NUMBER',
                'id')
        elif tablename == 'normal_game':
            data = (await data_getter(f"""SELECT * FROM (Select id, assets.t_id as plot_media, texts.text as plot_text, 
                                             belivers, nonbelivers,
                                             ROW_NUMBER () OVER (ORDER BY id) FROM public.{tablename}
                                             left outer join assets on assets.name = {tablename}.asset_name
                                             left outer join texts on {tablename}.text_name = texts.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = ('id', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'ROW_NUMBER')
        elif tablename == 'ucraine_or_not_game':
            data = (await data_getter(f"""SELECT * FROM (Select id, truth, assets.t_id as plot_media, texts.text as
                                            plot_text, belivers, nonbelivers,
                                             ROW_NUMBER () OVER (ORDER BY id) FROM public.{tablename}
                                             left outer join assets on assets.name = {tablename}.asset_name
                                             left outer join texts on {tablename}.text_name = texts.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = ('id', 'truth', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'ROW_NUMBER')
        elif tablename == 'putin_lies':
            data = (await data_getter(f"""SELECT * FROM (Select id, assets.t_id as plot_media, texts.text as plot_text, 
                                             belivers, nonbelivers,
                                             ROW_NUMBER () OVER (ORDER BY id) FROM public.{tablename}
                                             left outer join assets on assets.name = {tablename}.asset_name
                                             left outer join texts on {tablename}.text_name = texts.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = ('id', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'ROW_NUMBER')
        elif tablename == 'mistakeorlie':
            data = (await data_getter(f"""SELECT * FROM (Select id, truth, assets.t_id as plot_media, texts.text as
                                            plot_text, belivers, nonbelivers,
                                             ROW_NUMBER () OVER (ORDER BY id) FROM public.{tablename}
                                             left outer join assets on assets.name = {tablename}.asset_name
                                             left outer join texts on {tablename}.text_name = texts.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = ('id', 'truth', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'ROW_NUMBER')
        elif tablename == 'putin_old_lies':
            data = (await data_getter(f"""SELECT * FROM (Select id, assets.t_id as plot_media, texts.text as plot_text, 
                                             belivers, nonbelivers,
                                             ROW_NUMBER () OVER (ORDER BY id) FROM public.{tablename}
                                             left outer join assets on assets.name = {tablename}.asset_name
                                             left outer join texts on {tablename}.text_name = texts.name)
                                             AS sub WHERE row_number = {row}"""))[0]
            keys = ('id', 'plot_media', 'plot_text', 'belivers', 'nonbelivers', 'ROW_NUMBER')
        datadict = dict(zip(keys, data))
        return datadict
    except IndexError:
        return False
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_add_value(table_name, column, cond_dict):
    que = ''
    for key in cond_dict:
        if isinstance(cond_dict[key], int):
            que = f'UPDATE {table_name} set {column} = {column} + 1 where {key} = {cond_dict[key]} RETURNING {column};'
        elif isinstance(cond_dict[key], str):
            que = f"UPDATE {table_name} set {column} = {column} + 1 where" \
                  f" {key} = '{cond_dict[key]}' RETURNING {column};"
    a = await data_getter(que)


async def poll_delete_value(key, value):
    try:
        return all_data().get_data_red().delete(value)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def sql_safe_insert(schema, table_name, data_dict):
    try:
        safe_query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({});").format(sql.Identifier(schema),
                                                                           sql.Identifier(table_name),
                                                                           sql.SQL(', ').join(
                                                                               map(sql.Identifier, data_dict)),
                                                                           sql.SQL(", ").join(
                                                                               map(sql.Placeholder, data_dict)), )
        with get_cursor() as cur:
            cur.execute(safe_query, data_dict)
        # postgresql_csv_dump(table_name)
        return True
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_update(table_name, data_dict, condition_dict):
    try:
        assert data_dict != {}, 'You have empty datadict in updater'
        assert data_dict != {}, 'You have empty conditiondict in updater'
        where = list(condition_dict.keys())[0]
        equals = condition_dict[where]
        safe_query = sql.SQL("UPDATE {} SET {} = {} WHERE {} = {};").format(sql.Identifier(table_name),
                                                                            sql.SQL(', ').join(
                                                                                map(sql.Identifier, data_dict)),
                                                                            sql.SQL(", ").join(
                                                                                map(sql.Placeholder, data_dict)),
                                                                            sql.Identifier(where), sql.Literal(equals))

        with get_cursor() as cur:
            cur.execute(safe_query, data_dict)
        # postgresql_csv_dump(table_name)
        return "Complete"
    except AssertionError as error:
        logg.get_info(f"{error}")
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)


"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^MongoDB^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""


async def mongo_add_news(list_media: str, caption: str, datetime=None, coll=None):
    try:
        client = all_data().get_mongo()
        database = client['database']

        if coll == 'add_main_news':
            collection = database['spam_news_main']
            spam_list = {'media': list_media, 'caption': caption}
            await collection.insert_one(spam_list)
        elif coll == 'add_actual_news':
            collection = database['spam_actual_news']
            spam_list = {'media': list_media, 'caption': caption, 'datetime': datetime}
            await collection.insert_one(spam_list)
    except Exception as error:
        await logg.get_error(error)


async def mongo_select_news(coll=None) -> [list, bool]:
    try:

        client = all_data().get_mongo()
        database = client.database
        spam_list = []
        if coll == 'main':
            collection = database['spam_news_main']
            async for spam in collection.find():
                spam_list.append(spam)
        elif coll == 'actu':
            collection = database['spam_actual_news']
            async for spam in collection.find():
                spam_list.append(spam)
        return spam_list

    except Exception as error:
        await logg.get_error(f"mongo_select_info | {error}", __file__)
        return False


async def check_avtual_news(date) -> dict:
    client = all_data().get_mongo()
    database = client.database
    date_time_1 = datetime.strptime(date + ' 11:00', '%Y.%m.%d %H:%M')
    date_time_2 = datetime.strptime(date + ' 19:00', '%Y.%m.%d %H:%M')
    collection = database['spam_actual_news']
    try:
        count_news_on_date = dict()
        count_news_on_date['news_11:00'] = int(await collection.count_documents({'datetime': date_time_1}))
        count_news_on_date['news_19:00'] = int(await collection.count_documents({'datetime': date_time_2}))
        return count_news_on_date
    except Exception as e:
        print(e)


async def mongo_pop_news(m_id: str, coll=None):
    try:

        client = all_data().get_mongo()
        database = client.database
        if 'main' in coll:
            collection = database['spam_news_main']
            await collection.delete_one({'media': {'$regex': m_id}})
        elif 'actu' in coll:
            collection = database['spam_actual_news']
            await collection.delete_one({'media': {'$regex': m_id}})
        return
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


async def mongo_update_news(m_id: str, new_m_id: str, new_caption: str, coll=None):
    try:

        client = all_data().get_mongo()
        database = client.database
        if 'main' in coll:
            collection = database['spam_news_main']
            await collection.replace_one({'media': {'$regex': m_id}}, {"media": str(new_m_id), "caption": new_caption},
                                         True)
        elif 'actu' in coll:
            collection = database['spam_actual_news']
            await collection.replace_one({'media': {'$regex': m_id}}, {"media": str(new_m_id), "caption": new_caption},
                                         True)
        print('Update')
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


async def mongo_user_info(tg_id, username):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    time = datetime.now().strftime("%H:%M")
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['userinfo']
        user_answer = {'_id': int(tg_id), 'username': str(username), 'datetime': f'{today}_{time}',
                       'datetime_end': None, 'viewed_news': []}
        await collection.insert_one(user_answer)
    except Exception as error:
        pass


async def mongo_select_info(tg_id):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database.userinfo
        try:
            x = await collection.find_one({"_id": int(tg_id)})
        except:
            x = await collection.find_one({"username": str(tg_id)})
        return x
    except Exception as error:
        await logg.get_error(f"mongo_select_info | {error}", __file__)
        return False


async def mongo_add(tg_id, answers):
    try:
        answer_list = []
        for answer in answers:
            answer_list.append(answer)
        client = all_data().get_mongo()
        database = client.database
        collection = database['useranswer']
        user_answer = {'_id': int(tg_id), 'answers_1': str(answer_list[0]), 'answers_2': (answer_list[1]),
                       'answers_3': str(answer_list[2]), 'answers_4': (answer_list[3]), 'answers_5': (answer_list[4]),
                       'other_answer': []}
        await collection.insert_one(user_answer)
    except Exception as error:
        await logg.get_error(f"mongo_add | {error}", __file__)


async def mongo_select(tg_id):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['useranswer']
        myquery = {"_id": int(tg_id)}
        async for answer in collection.find(myquery):
            return answer
    except Exception as error:
        await logg.get_error(f"mongo_select | {error}", __file__)


async def mongo_update_viewed_news(tg_id, value):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['userinfo']
        await collection.update_one({'_id': int(tg_id)}, {"$push": {"viewed_news": value}}, True)
    except Exception as error:
        await logg.get_error(f"mongo update news | {error}", __file__)


async def mongo_update(tg_id, collections: str, column, options='$set', value=True):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database[collections]
        await collection.update_one({'_id': int(tg_id)}, {options: {column: value}})
    except Exception as error:
        await logg.get_error(f"mongo_update | {error}", __file__)


async def mongo_update_end(tg_id):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['userinfo']
        await collection.update_one({'_id': int(tg_id)}, {'$set': {'datetime_end': datetime.utcnow()}}, True)
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


async def mongo_pop(tg_id, value_dict):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['useranswer']
        await collection.update({'_id': int(tg_id)}, {'$pull': {'other_answer': value_dict}})
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


# admin
async def mongo_add_admin(tg_id, level: str):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['admins']
        insert_dict = {'_id': int(tg_id), 'access': [level]}
        await collection.insert_one(insert_dict)
    except Exception as error:
        await logg.get_error(f"mongo_add_admin | {error}", __file__)


async def mongo_edit_admin(tg_id, level: str):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['admins']
        await collection.update_one({'_id': int(tg_id)}, {'$addToSet': {'access': level}})
    except Exception as error:
        await logg.get_error(f"mongo_EDIT_admin | {error}", __file__)


async def mongo_all_admins():
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['admins']
        lst = []
        async for answer in collection.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select_admins | {error}", __file__)


async def mongo_select_admin_levels(tg_id: int):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['admins']
        admin_info = await collection.find_one({'_id': int(tg_id)})
        if admin_info is not None:
            levels = admin_info['access']
            return levels
        else:
            return False
    except Exception as error:
        return False


async def mongo_pop_admin_level(tg_id, level):
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['admins']
        if len(await mongo_select_admin_levels(tg_id)) <= 1:
            await collection.delete_one({'_id': int(tg_id)})
            return 'Was deleted'
        else:
            await collection.update_one({'_id': int(tg_id)}, {'$pull': {'access': level}})
            return 'Still admin'
    except Exception as error:
        await logg.get_error(f"mongo_pop_admin | {error}", __file__)


async def mongo_game_answer(user_id, game, number, answer_group, condict):
    client = all_data().get_mongo()
    database = client.database
    collection = database['user_games']
    data = await collection.find_one({'_id': user_id})
    if data is None:
        await collection.insert_one({'_id': user_id, game: [number]})
        await sql_add_value(game, answer_group, condict)
    elif game not in data or number not in data[game]:
        await collection.update_one({'_id': user_id}, {'$push': {game: number}})
        await sql_add_value(game, answer_group, condict)
    else:
        pass


async def mongo_count_docs(database: str, collection: str, conditions: dict | list, hard_link: bool = False):
    client = all_data().get_mongo()
    database = client[database]
    collection = database[collection]
    if isinstance(conditions, list) and hard_link:
        return await collection.count_documents({"$and": conditions})
    elif isinstance(conditions, list) and not hard_link:
        a = 0
        for d in conditions:
            a += await collection.count_documents(d)
        return a
    elif isinstance(conditions, dict):
        return await collection.count_documents(conditions)


async def mongo_easy_upsert(database: str, collection: str, condition_dict: dict, main_dict: dict):
    """Use this function if you need to update or insert something and you not sure if it exists.\n\n
    Condition dict will be inserted too."""
    try:
        client = all_data().get_mongo()
        database = client[database]
        collection = database[collection]
        await collection.update_one(condition_dict, {"$set": main_dict}, upsert=True)
    except Exception as ex:
        await logg.get_error(f"Mongo easy upsert is failed\n\n{ex}", __file__)


async def mongo_ez_find_one(database: str, collection: str, condition_dict: dict):
    """One select to rule them all. Just use it please."""
    try:
        client = all_data().get_mongo()
        database = client[database]
        collection = database[collection]
        return await collection.find_one(condition_dict)
    except Exception as ex:
        await logg.get_error(f"Mongo easy select is failed\n\n{ex}", __file__)


"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^CSV_UPDATE^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""

'''def pandas_csv_add(table_name, new_values_dict):
    try:
        dtframe = DataFrame([new_values_dict.values()], columns=new_values_dict.keys())
        if not os.path.isfile(f'resources/{table_name}.csv'):
            dtframe.to_csv(f'resources/{table_name}.csv', header=True, index=False)
        else:
            dtframe.to_csv(f'resources/{table_name}.csv', mode='a', header=False, index=False)
    except Exception as error:
        logg.get_error(f"{error}", __file__)'''


def postgresql_csv_dump(table_name):
    conn = all_data().get_postg()
    query = f"COPY (SELECT * FROM {table_name}) TO STDOUT WITH CSV HEADER"
    path = f'resources/{table_name}.csv'
    try:
        with open(path, 'w') as file, conn.cursor() as cur:
            cur.copy_expert(query, file)
            conn.close()
    except psycopg2.Error as error:
        pass


# update_csv
'''def pandas_csv_update(table_name, new_values_dict, condition_dict):
    try:
        data = read_csv(f'resources/{table_name}.csv', header=0)
        df = DataFrame(data)
        for value in new_values_dict:
            for condition in condition_dict:
                df.loc[df[condition] == condition_dict[condition], value] = new_values_dict[value]
        df.to_csv(f'resources/{table_name}.csv', header=True, index=False)
    except Exception as error:
        logg.get_error(f"{error}", __file__)'''

"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^DATA_REDIS^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""


async def poll_get(key):
    try:
        return all_data().get_data_red().lrange(key, 0, -1)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_delete_from_list(key, item):
    try:
        all_data().get_data_red().lrem(key, 0, item)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


# Одинаковая функция, лол
async def del_key(key):
    try:
        all_data().get_data_red().delete(key)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_pop(key):
    try:
        all_data().get_data_red().lpop(key)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def poll_write(key, value):
    try:
        all_data().get_data_red().rpush(key, value)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_lpush(key, value):
    try:
        all_data().get_data_red().lpush(key, value)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_key_exists(key):
    try:
        all_data().get_data_red().info(key)

    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_delete_first_item(key):
    try:
        all_data().get_data_red().lpop(key)
    except Exception as error:
        await logg.get_error(f"redis del item | {error}", __file__)


async def redis_write(key, value):
    try:
        all_data().get_data_red().lpush(key, value)

    except Exception as error:
        await logg.get_error(f"redis write | {error}", __file__)


async def redis_media_counter_get(user_id):
    try:
        return all_data().get_data_red().lrange(f'Media_counter: Smi: {user_id}', 0, -1)
    except Exception as error:
        await logg.get_error(f"redis get | {error}", __file__)


async def redis_just_one_write(key, value, ttl: int = None):
    try:
        all_data().get_data_red().set(key, value, ex=ttl)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_just_one_read(key):
    try:
        return all_data().get_data_red().get(key)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_check(key):
    try:
        return all_data().get_data_red().exists(key)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
