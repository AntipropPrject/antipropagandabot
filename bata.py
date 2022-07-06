from aiogram import Bot
import psycopg2
from redis import from_url
import pymongo


class all_data():
    def __init__(self):
        self.redis_url = 'redis://localhost:2342'
        self.postgres_data = 'dbname=antiprop_db user=postgres password=postgres'
        self.mongodb_data = 'mongodb://localhost:27017'
        self.bot_token = '5480651654:AAHN90GGJui6qFWJUzS6DByNpCPYrsm83AM'
        self.super_admins = [5429649862, 5177494340, 5581082758, 5316104187, 784006905]
        self.THROTTLE_TIME = 0.8
        self.commichannel = -1001704405613

# фывфывфдв
    def get_bot(self):
        return Bot(self.bot_token, parse_mode="HTML")

    def get_postg(self):
        return psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port=5431)

    def get_mongo(self):
        return pymongo.MongoClient(host=self.mongodb_data, username='mongoOTPOR', password='mongoOTPOR')

    def get_red(self):
        return from_url(self.redis_url, decode_responses=True)

    def get_data_red(self):
        return from_url('redis://localhost:2342/1', decode_responses=True)

    def get_THROTTLE_TIME(self):
        return self.THROTTLE_TIME


#Settings:

Check_tickets = False
