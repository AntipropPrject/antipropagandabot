from aiogram import Bot
import psycopg2
from redis import from_url
import motor.motor_asyncio
import os
import pymongo


class all_data():
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL')
        self.bot_token = os.getenv('BOT_TOKEN')
        self.pg_db = os.getenv('POSTGRES_BASE')
        self.pg_user = os.getenv('POSTGRES_USER')
        self.pg_pswd = os.getenv('POSTGRES_PASSWORD')
        self.pg_host = os.getenv('POSTGRES_HOST')
        self.pg_port = os.getenv('POSTGRES_PORT')
        self.mg_user = os.getenv('MONGO_USER')
        self.mg_pswd = os.getenv('MONGO_PASSWORD')
        self.mg_host = os.getenv('MONGO_HOST')
        self.mg_port = os.getenv('MONGO_PORT')
        self.super_admins = os.getenv('SU_ADMINS')
        self.THROTTLE_TIME = os.getenv('THROTTLE_TIME')
        self.commichannel = os.getenv('COMMIT_CH')
        self.masterchannel = os.getenv('MASTER_CH')
# фывфывфдв
    def get_bot(self):
        return Bot(self.bot_token, parse_mode="HTML")

    def get_postg(self):
        return psycopg2.connect(database=self.pg_db, user=self.pg_user, password=self.pg_pswd, host=self.pg_host, port=int(self.pg_port))

    def get_mongo(self):
        return motor.motor_asyncio.AsyncIOMotorClient(username=self.mg_user, password=self.mg_pswd, host=self.mg_host, port=int(self.mg_port))

    def get_red(self):
        return from_url(self.redis_url, decode_responses=True)

    def get_data_red(self):
        return from_url('redis://localhost:2342/1', decode_responses=True)

    def get_THROTTLE_TIME(self):
        return self.THROTTLE_TIME


#Settings:

Check_tickets = True
