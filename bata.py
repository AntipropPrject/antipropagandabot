from aiogram import Bot
from psycopg2 import connect
from redis import from_url


class all_data():
    def __init__(hi):
        hi.redis_url = 'redis://username:password@127.0.0.1:6379/db'
        hi.postgres_data = 'dbname=dbname user=user password=password'
        hi.bot_token = 'BOT_TOKEN'
        hi.admins = (5306348087, 5177494340, 5581082758)

    def get_bot(hi):
        return Bot(hi.bot_token)

    def get_postg(hi):
        return connect(hi.postgres_data)

    def get_red(hi):
        return from_url(hi.redis_url, decode_responses=True)

    def get_data_red(hi):
        return from_url('redis://username:password@127.0.0.1:6379/1', decode_responses=True)
