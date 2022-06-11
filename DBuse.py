from psycopg2 import sql
from bata import all_data
import os
from pandas import DataFrame
from log import logg


# postgresSQL
def data_getter(query):
    try:
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
        conn.close()
        return data
    except Exception as error:
        logg.get_error(f"{error}", __file__)


def safe_data_getter(safe_query, values_dict):
    try:
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, values_dict)
                data = cur.fetchall()
        conn.close()
        return data
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def sql_safe_select(column, table_name, condition_dict):
    try:
        safe_query = sql.SQL("SELECT {} from {} WHERE {} = {};").format(sql.Identifier(column),
                sql.Identifier(table_name), sql.SQL(', ').join(map(sql.Identifier, condition_dict)),
                sql.SQL(", ").join(map(sql.Placeholder, condition_dict)), )
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, condition_dict)
                data = cur.fetchall()
        conn.close()
        return data[0][0]
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def sql_safe_insert(table_name, data_dict):
    try:
        safe_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) Returning name;").format(sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, data_dict)),
                sql.SQL(", ").join(map(sql.Placeholder, data_dict)), )
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, data_dict)
        conn.close()
        pandas_csv_add(table_name, data_dict)
        return "Complete"
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def sql_safe_update(table_name, data_dict, condition_dict):
    try:
        where = list(condition_dict.keys())[0]
        equals = condition_dict[where]
        safe_query = sql.SQL("UPDATE {} SET {} = {} WHERE {} = '{}';").format(sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, data_dict)), sql.SQL(", ").join(map(sql.Placeholder, data_dict)),
                sql.Identifier(where), sql.Identifier(equals), )
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, data_dict)
        conn.close()
        pandas_csv_add(table_name, data_dict)
        return "Complete"
    except Exception as error:
        logg.get_error(f"{error}", __file__)


# add_to_csv
def pandas_csv_add(table_name, new_values_dict):
    try:
        dtframe = DataFrame([new_values_dict.values()], columns=new_values_dict.keys())
        print(dtframe)
        if not os.path.isfile(f'resources/{table_name}.csv'):
            dtframe.to_csv(f'resources/{table_name}.csv', header=True, index=False)
        else:
            dtframe.to_csv(f'resources/{table_name}.csv', mode='a', header=False, index=False)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


# redis
async def poll_get(key):
    try:
        return all_data().get_data_red().lrange(key, 0, -1)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def redis_pop(key):
    try:
        all_data().get_data_red().lpop(key)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def poll_write(key, value):
    try:
        all_data().get_data_red().rpush(key, value)
    except Exception as error:
        logg.get_error(f"{error}", __file__)
