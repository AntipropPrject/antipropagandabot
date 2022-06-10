from psycopg2 import sql

from bata import all_data




def data_getter(query):
    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
    conn.close()
    return data

def safe_data_getter(safe_query, values_dict):
    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            cur.execute(safe_query, values_dict)
            data = cur.fetchall()
    conn.close()
    return data


async def sql_safe_select(column, table_name, condition_dict):
    safe_query = sql.SQL("SELECT {} from {} WHERE {} = {};").format(
        sql.Identifier(column),
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, condition_dict)),
        sql.SQL(", ").join(map(sql.Placeholder, condition_dict)),
    )
    conn = all_data().get_postg()
    print(safe_query.as_string(conn))
    with conn:
        with conn.cursor() as cur:
            cur.execute(safe_query, condition_dict)
            data = cur.fetchall()
    conn.close()
    return data[0][0]


async def sql_safe_insert(table_name, data_dict):
    safe_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) Returning name;").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, data_dict)),
        sql.SQL(", ").join(map(sql.Placeholder, data_dict)),
    )
    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            cur.execute(safe_query, data_dict)
    conn.close()
    return "Complete"


async def sql_safe_update(table_name, data_dict, condition_dict):
    where = list(condition_dict.keys())[0]
    equals = condition_dict[where]
    safe_query = sql.SQL("UPDATE {} SET {} = {} WHERE {} = '{}';").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, data_dict)),
        sql.SQL(", ").join(map(sql.Placeholder, data_dict)),
        sql.Identifier(where),
        sql.Identifier(equals),
    )
    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            cur.execute(safe_query, data_dict)
    conn.close()
    return "Complete"


async def poll_get(key):
    redis = all_data().get_data_red()
    R = redis.lrange(key, 0, -1)
    return R

async def redis_pop(key):
    redis = all_data().get_data_red()
    R = redis.lpop(key)

async def poll_write(user_id, poll_name, tag):
    redis = all_data().get_data_red()
    redis.rpush(f'Poll_answers: {poll_name}: {user_id}', tag)