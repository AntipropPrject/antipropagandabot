from aiogram import Bot
import psycopg2
from redis import from_url


class all_data():
    def __init__(hi):
        hi.redis_url = 'redis://localhost:2342'
        hi.postgres_data = 'dbname=antiprop_db user=postgres password=postgres'
        hi.bot_token = '5412151268:AAFZdBmq7K1D0x_KK6J7yf0PvL8UMM8pODE'
        hi.admins = (5306348087, 5177494340, 5581082758, 5316104187)

    def get_bot(hi):
        return Bot(hi.bot_token, parse_mode="HTML")

    def get_postg(hi):
        return psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost")

    def get_red(hi):
        return from_url(hi.redis_url, decode_responses=True)

    def get_data_red(hi):
        return from_url('redis://localhost:2342/1', decode_responses=True)
