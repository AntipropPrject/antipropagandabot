import os
from contextlib import contextmanager

import psycopg2.extras
import psycopg2.pool

POOL = None
CONF = {
    "db.poolmin": "3",
    "db.poolmax": "200",
    "db.host": os.getenv('POSTGRES_HOST'),
    "db.port": os.getenv('POSTGRES_PORT'),
    "db.name": os.getenv('POSTGRES_BASE'),
    "db.user": os.getenv('POSTGRES_USER'),
    "db.password": os.getenv('POSTGRES_PASSWORD'),
}


def _get_pool():
    global POOL
    if not POOL:
        POOL = psycopg2.pool.ThreadedConnectionPool(
            int(CONF.get("db.poolmin")),
            int(CONF.get("db.poolmax")),
            host=CONF.get("db.host"),
            port=int(CONF.get("db.port")),
            database=CONF.get("db.name"),
            user=CONF.get("db.user"),
            password=CONF.get("db.password"))
    return POOL


@contextmanager
def get_conn():
    conn = _get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        POOL.putconn(conn)


@contextmanager
def get_cursor():
    with get_conn() as conn:
        yield conn.cursor()



