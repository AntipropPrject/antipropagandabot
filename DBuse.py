from psycopg2 import sql
from bata import all_data
import os
from pandas import DataFrame, read_csv
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
    except Exception as error:
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
        safe_query = sql.SQL("SELECT {col_names} from {} WHERE {} = {};").format(
            sql.Identifier(table_name), sql.SQL(', ').join(map(sql.Identifier, condition_dict)),
            sql.SQL(", ").join(map(sql.Placeholder, condition_dict)),
            col_names=sql.SQL(',').join(ident_list)
        )
        conn = all_data().get_postg()
        print(safe_query.as_string(conn))
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, condition_dict)
                data = cur.fetchall()
        conn.close()
        if isinstance(column, list):
            return data[0]
        else:
            return data[0][0]
    except Exception as error:
        logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_select_like(column1, column2,  table_name, first_condition, second_condition):
    try:
        safe_query = (
            f"SELECT {column1} from {table_name} WHERE {column2} LIKE '%{first_condition}%' AND {column2} LIKE '%{str(second_condition)[-5:-1].strip()}%'")

        print(safe_query)
        conn = all_data().get_postg()
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query)
                data = cur.fetchall()
        conn.close()
        return data
    except Exception as error:
        logg.get_error(f"{error}", __file__)
        return False


async def poll_delete_value(key, value):
    try:
        return all_data().get_data_red().delete(value)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def sql_safe_insert(table_name, data_dict):
    try:
        safe_query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(sql.Identifier(table_name),
                                                                        sql.SQL(', ').join(
                                                                            map(sql.Identifier, data_dict)),
                                                                        sql.SQL(", ").join(
                                                                            map(sql.Placeholder, data_dict)), )
        conn = all_data().get_postg()
        print(safe_query.as_string(conn))
        with conn:
            with conn.cursor() as cur:
                cur.execute(safe_query, data_dict)
        conn.close()
        pandas_csv_add(table_name, data_dict)
        return True
    except Exception as error:
        logg.get_error(f"{error}", __file__)
        return False


async def sql_safe_update(table_name, data_dict, condition_dict):
    try:
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
    except Exception as error:
        logg.get_error(f"{error}", __file__)


# add_to_csv
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
    data = read_csv(f'resources/{table_name}.csv', header=0)
    df = DataFrame(data)
    for value in new_values_dict:
        for condition in condition_dict:
            print(value, new_values_dict[value])
            df.loc[df[condition] == condition_dict[condition], value] = new_values_dict[value]
    df.to_csv(f'resources/{table_name}.csv', header=True, index=False)


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


async def redis_key_exists(key):
    try:
        all_data().get_data_red().info(key)

    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def redis_delete_first_item(key):
    try:
        all_data().get_data_red().lpop(key)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def redis_media_counter_write(user_id, value):
    try:
        all_data().get_data_red().rpush(f'Media_counter: Smi: {user_id}', value)
    except Exception as error:
        logg.get_error(f"{error}", __file__)


async def redis_media_counter_get(user_id):
    try:
        return all_data().get_data_red().lrange(f'Media_counter: Smi: {user_id}', 0, -1)
    except Exception as error:
        logg.get_error(f"{error}", __file__)
