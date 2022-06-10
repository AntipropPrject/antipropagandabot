import asyncio
import logging
import pandas as pd
from sqlalchemy import create_engine
from time import sleep

import psycopg2
from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from psycopg2 import Error

import bata
from bata import all_data
from handlers import admin_hand, start_hand
from handlers.donbass_handlers import select_handler, option_two_hand, option_three_hand, option_four_hand, \
    option_five_hand, option_six_hand, option_seven_hand, option_eight_hand, final_donbass_hand
from handlers.started_message import welcome_messages
log = logging.getLogger(__name__)
log.addHandler(logging.FileHandler('logfile.log'))

try:
    con = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost")
    con.autocommit = True
    cursor = con.cursor()
    cursor.execute("DROP TABLE if exists texts")
    cursor.execute("DROP TABLE if exists assets")
    cursor.close()
    con.close()
    df1 = pd.read_csv('resources/texts.csv')
    df2 = pd.read_csv('resources/assets.csv')
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    df1.to_sql("texts", engine)
    df2.to_sql("assets", engine)
except (Exception, Error) as error:
    print("SQL EXEPTION ", error)
else:
    print("Database base created!")


async def main():
    data = all_data()
    bot = data.get_bot()
    storage = RedisStorage.from_url(data.redis_url)
    dp = Dispatcher(storage)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    log.error("Starting bot")

    dp.include_router(welcome_messages.router)
    dp.include_router(start_hand.router)
    dp.include_router(admin_hand.router)
    dp.include_router(select_handler.router)
    dp.include_router(option_two_hand.router)
    dp.include_router(option_three_hand.router)
    dp.include_router(option_four_hand.router)
    dp.include_router(option_five_hand.router)
    dp.include_router(option_six_hand.router)
    dp.include_router(option_seven_hand.router)
    dp.include_router(option_eight_hand.router)
    dp.include_router(final_donbass_hand.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
