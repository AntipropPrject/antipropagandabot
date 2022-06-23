import psycopg2
from psycopg2 import sql
from bata import all_data
import os
from pandas import DataFrame, read_csv

from log import logg

"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^PostgreSQL^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""


def data_getter(query):
    try:
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
        conn.close()
        return data
    except psycopg2.Error as error:
        logg.get_error(f"{error}", __file__)
        return error


def safe_data_getter(safe_query, values_dict):
    try:
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, values_dict)
                data = cur.fetchall()
        conn.close()
        return data
    except psycopg2.Error as error:
        logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_select(column, table_name, condition_dict):
    try:
        ident_list = list()
        if isinstance(column, list):
            for i in column:
                ident_list.append(sql.Identifier(i))
        elif isinstance(column, str):
            ident_list.append(sql.Identifier(column))
        safe_query = sql.SQL("SELECT {col_names} from {} WHERE {} = {};").format(sql.Identifier(table_name),
                                                                                 sql.SQL(', ').join(map(sql.Identifier,
                                                                                                        condition_dict)),
                                                                                 sql.SQL(", ").join(map(sql.Placeholder,
                                                                                                        condition_dict)),
                                                                                 col_names=sql.SQL(',').join(
                                                                                     ident_list))
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, condition_dict)
                data = cur.fetchall()
        conn.close()
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


async def sql_safe_select_like(column1, column2, table_name, first_condition, second_condition):
    try:
        safe_query = (f"SELECT {column1}"
                      f" from {table_name}"
                      f" WHERE {column2}"
                      f" LIKE '%{first_condition}%'"
                      f" AND {column2}"
                      f" LIKE '%{str(second_condition)[-5:-1].strip()}%'")
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query)
                data = cur.fetchall()
        conn.close()
        return data
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)
        return False


async def poll_delete_value(key, value):
    try:
        return all_data().get_data_red().delete(value)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def sql_safe_insert(table_name, data_dict):
    try:
        safe_query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(sql.Identifier(table_name), sql.SQL(', ').join(
                map(sql.Identifier, data_dict)), sql.SQL(", ").join(map(sql.Placeholder, data_dict)), )
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, data_dict)
        conn.close()
        pandas_csv_add(table_name, data_dict)
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

        conn = all_data().get_postg()
        print(safe_query.as_string(conn))
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, data_dict)
        conn.close()
        pandas_csv_update(table_name, data_dict, condition_dict)
        return "Complete"
    except AssertionError as error:
        logg.get_info(f"{error}")
    except psycopg2.Error as error:
        await logg.get_error(f"{error}", __file__)


"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^MongoDB^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""
async def mongo_user_info(tg_id, username):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['userinfo']
        user_answer = {'_id': int(tg_id), 'username': str(username)}
        collection.insert_one(user_answer)
    except Exception as error:
        pass

async def mongo_select_info(tg_id):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['userinfo']

        try:
            x = collection.find_one({"_id": int(tg_id)})
            print(x)
        except:
            x = collection.find_one({"username": str(tg_id)})
            print(x)
        return x

    except Exception as error:
        await logg.get_error(f"mongo_select_info | {error}", __file__)

async def mongo_add(tg_id, answers):
    try:
        answer_list = []
        for answer in answers:
            answer_list.append(answer)
        client = all_data().get_mongo()
        database = client['database']
        collection = database['useranswer']
        user_answer = {'_id': int(tg_id), 'answers_1': str(answer_list[0]), 'answers_2': (answer_list[1]),
                       'answers_3': str(answer_list[2]), 'answers_4': (answer_list[3]), 'answers_5': (answer_list[4]),
                       'other_answer': []}
        collection.insert_one(user_answer)
    except Exception as error:
        await logg.get_error(f"mongo_add | {error}", __file__)


async def mongo_select(tg_id):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['useranswer']
        myquery = {"_id": int(tg_id)}
        for answer in collection.find(myquery):
            return answer
    except Exception as error:
        await logg.get_error(f"mongo_select | {error}", __file__)


async def mongo_update(tg_id, value_dict):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['useranswer']
        collection.update_one({'_id': int(tg_id)}, {"$push": {"other_answer": value_dict}}, True)
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


async def mongo_pop(tg_id, value_dict):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['useranswer']
        collection.update({'_id': int(tg_id)}, {'$pull': {'other_answer': value_dict}})
    except Exception as error:
        await logg.get_error(f"mongo update | {error}", __file__)


# admin
async def mongo_add_admin(tg_id):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['admins']
        user_answer = {'_id': int(tg_id)}
        collection.insert_one(user_answer)
    except Exception as error:
        await logg.get_error(f"mongo_add_admin | {error}", __file__)


async def mongo_select_admins():
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['admins']
        lst = []
        for answer in collection.find():
            lst.append(answer)
        return lst
    except Exception as error:
        await logg.get_error(f"mongo_select_admins | {error}", __file__)

async def mongo_pop_admin(tg_id):
    try:
        client = all_data().get_mongo()
        database = client['database']
        collection = database['admins']
        collection.delete_one({'_id': int(tg_id)})
    except Exception as error:
        await logg.get_error(f"mongo_pop_admin | {error}", __file__)


"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^CSV_UPDATE^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""


def pandas_csv_add(table_name, new_values_dict):
    try:
        dtframe = DataFrame([new_values_dict.values()], columns=new_values_dict.keys())
        if not os.path.isfile(f'resources/{table_name}.csv'):
            dtframe.to_csv(f'resources/{table_name}.csv', header=True, index=False)
        else:
            dtframe.to_csv(f'resources/{table_name}.csv', mode='a', header=False, index=False)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


# update_csv
def pandas_csv_update(table_name, new_values_dict, condition_dict):
    try:
        data = read_csv(f'resources/{table_name}.csv', header=0)
        df = DataFrame(data)
        for value in new_values_dict:
            for condition in condition_dict:
                df.loc[df[condition] == condition_dict[condition], value] = new_values_dict[value]
        df.to_csv(f'resources/{table_name}.csv', header=True, index=False)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


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


#Одинаковая функция, лол
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


async def redis_just_one_write(key, value):
    try:
        all_data().get_data_red().set(key, value)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)


async def redis_just_one_read(key):
    try:
        return all_data().get_data_red().get(key)
    except Exception as error:
        await logg.get_error(f"{error}", __file__)