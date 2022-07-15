import asyncio
from datetime import datetime
from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
import bata
from bata import all_data
from day_func import day_count
from export_to_csv.pg_mg import mongo_export_to_file
from handlers import start_hand, anti_prop_hand, smi_hand, donbass_hand, true_resons_hand, putin_hand, stopwar_hand, \
    nazi_hand, preventive_strike, new_admin_hand, welcome_messages, status, main_menu_hand, admin_for_games
from export_to_csv import pg_mg
from handlers.advertising import start_spam
from handlers.other import other_file
from middleware.trottling import ThrottlingMiddleware
from utilts import happy_tester

data = all_data()
bot = data.get_bot()
storage = RedisStorage.from_url(data.redis_url)
dp = Dispatcher(storage)


async def periodic():
    print('periodic function has been started')
    while True:
        c_time = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime('%Y.%m.%d')
        #удаление дневного счетчика
        if c_time == '21:00:01':
            await day_count(count_delete=True)
        if c_time == '07:00:01':
            await mongo_export_to_file()
        if c_time == '08:00:01':
            await start_spam(f'{date} 11:00')
        if c_time == '16:00:01':
            await start_spam(f'{date} 19:00')
        if c_time == '19:00:01':
            await mongo_export_to_file()
        await asyncio.sleep(1)


async def main():
    bot_info = await bot.get_me()
    print(f"Hello, i'm {bot_info.first_name} | {bot_info.username}")

    if bata.Check_tickets is True:
        await happy_tester(bot)
    else:
        print('Tickets checking is disabled, so noone will know...')
    # Технические роутеры
    # TablesCreator.tables_god()
    dp.include_router(pg_mg.router)
    dp.include_router(new_admin_hand.router)
    dp.include_router(admin_for_games.router)

    dp.include_router(status.router)
    dp.include_router(start_hand.router)

    # Начало и антипропаганда
    dp.include_router(welcome_messages.router)
    dp.include_router(anti_prop_hand.router)
    dp.include_router(smi_hand.router)

    # Роутеры причин войны
    dp.include_router(true_resons_hand.router)
    dp.include_router(donbass_hand.router)
    dp.include_router(nazi_hand.router)
    dp.include_router(preventive_strike.router)
    dp.include_router(putin_hand.router)
    dp.include_router(stopwar_hand.router)
    dp.include_router(main_menu_hand.router)

    dp.message.middleware(ThrottlingMiddleware())
    # Роутер для неподошедшего
    dp.include_router(other_file.router)

    session = aiohttp.ClientSession()
    # use the session here

    #periodic function
    asyncio.create_task(periodic())

    await session.close()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

