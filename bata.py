from aiogram import Bot
from psycopg2 import connect
from redis import from_url

redis_url = 'redis://username:password@127.0.0.1:6379/db'
postgres_data = 'dbname=dbname user=user password=password'
bot_token = 'BOT_TOKEN'
admins = (5306348087, 5177494340, 5581082758)

def get_bot(hi):
    return Bot(bot_token)

def get_postg(hi):
    return connect(postgres_data)

def get_red(hi):
    return from_url(redis_url, decode_responses=True)

def get_data_red(hi):
    return from_url('redis://username:password@127.0.0.1:6379/1', decode_responses=True)
