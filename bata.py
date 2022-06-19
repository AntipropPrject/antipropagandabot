from aiogram import Bot
import psycopg2
from redis import from_url
import pymongo


class all_data():
    def __init__(self):
        self.redis_url = 'redis://localhost:2342'
        self.postgres_data = 'dbname=postgres user=postgres password=postgres port=5432'
        self.mongodb_data = 'mongodb://localhost:27017'
        self.bot_token = '5592039815:AAGRRXWh2vNm8T79SOhX1afycZEpRzEVVV4'
        self.admins = (5306348087, 5177494340, 5581082758, 5316104187)


# фывфывфдв
    def get_bot(self):
        return Bot(self.bot_token, parse_mode="HTML")

    def get_postg(self):
        return psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")

    def get_mongo(self):
        return pymongo.MongoClient(host=self.mongodb_data, username='mongoOTPOR', password='mongoOTPOR')

    def get_red(self):
        return from_url(self.redis_url, decode_responses=True)

    def get_data_red(self):
        return from_url('redis://localhost:2342/1', decode_responses=True)
