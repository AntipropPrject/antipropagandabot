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