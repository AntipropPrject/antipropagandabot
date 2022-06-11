import asyncio
import sys

from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from psycopg2 import Error
from bata import all_data
from handlers import admin_hand, start_hand, anti_prop_hand
from handlers.donbass_handlers import select_handler, option_two_hand, option_three_hand, option_four_hand, \
    option_five_hand, option_six_hand, option_seven_hand, option_eight_hand, final_donbass_hand
from handlers.started_message import welcome_messages
from log import logg

try:
    # Подключение к существующей базе данных
    con = all_data().get_postg()
    # Курсор для выполнения операций с базой данных
    cur = con.cursor()
    con.autocommit = True

    # Выполнение SQL-запроса

    cur.execute("SELECT version();")
    record = cur.fetchone()
    logg.get_info(f"You connect to - {record}, \n")

    # Удаление таблицы

    cur.execute("DROP TABLE IF EXISTS texts")
    logg.get_info("Table is texts has been deleted")
    cur.execute("DROP TABLE IF EXISTS assets")

    logg.get_info("Table is assets has been deleted")

    # Создание таблиц

    cur.execute('''CREATE TABLE IF NOT EXISTS texts(
                name TEXT NOT NULL PRIMARY KEY,
                text TEXT NOT NULL
                )''')
    logg.get_info("Texts table created")

    cur.execute('''CREATE TABLE IF NOT EXISTS assets(
            t_id TEXT NOT NULL,
            name TEXT NOT NULL PRIMARY KEY
            )''')
    logg.get_info("Assets table created")

    try:
        csv_file_name = 'resources/assets.csv'
        sql = "COPY assets FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = 'resources/texts.csv'
        sql = "COPY texts FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        logg.get_error(f"{error}", __file__)

    con.close()
    cur.close()


except (Exception, Error) as error:
    logg.get_error(f"PostgreSQL, {error}", __file__)



async def main():
    data = all_data()
    bot = data.get_bot()
    storage = RedisStorage.from_url(data.redis_url)
    dp = Dispatcher(storage)
    logg.get_info("BOT_STARTED")

    dp.include_router(welcome_messages.router)
    dp.include_router(anti_prop_hand.router)
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
