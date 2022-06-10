import asyncio
import logging
from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from psycopg2 import Error
from bata import all_data
from handlers import admin_hand, start_hand
from handlers.donbass_handlers import select_handler, option_two_hand, option_three_hand, option_four_hand, \
    option_five_hand, option_six_hand, option_seven_hand, option_eight_hand, final_donbass_hand
from handlers.started_message import welcome_messages
log = logging.getLogger(__name__)
log.addHandler(logging.FileHandler('logfile.log'))

try:
    # Подключение к существующей базе данных
    con = all_data().get_postg()

    # Курсор для выполнения операций с базой данных
    cur = con.cursor()
    con.autocommit = True
    # Выполнение SQL-запроса
    cur.execute("SELECT version();")
    # Получить результат
    record = cur.fetchone()
    print("Вы подключены к - ", record, "\n")
    # Удаление таблицы
    cur.execute("DROP TABLE IF EXISTS texts")
    cur.execute("DROP TABLE IF EXISTS assets")
    # Создание таблиц
    cur.execute('''CREATE TABLE IF NOT EXISTS texts(
                name TEXT NOT NULL PRIMARY KEY,
                text TEXT NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS assets(
            t_id TEXT NOT NULL,
            name TEXT NOT NULL PRIMARY KEY
            )''')

    csv_file_name = 'resources/assets.csv'
    sql = "COPY assets FROM STDIN DELIMITER ',' CSV HEADER"
    cur.copy_expert(sql, open(csv_file_name, "r"))

    csv_file_name = 'resources/texts.csv'
    sql = "COPY texts FROM STDIN DELIMITER ',' CSV HEADER"
    cur.copy_expert(sql, open(csv_file_name, "r"))
    con.close()
    cur.close()


except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)


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
