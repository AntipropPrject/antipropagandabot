import asyncio
import time
from asyncio import events
from datetime import datetime

from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

import bata
from bata import all_data
from day_func import day_count
from handlers import start_hand, anti_prop_hand, smi_hand, donbass_hand, true_resons_hand, putin_hand, stopwar_hand, \
    nazi_hand, preventive_strike, new_admin_hand, welcome_messages, status, main_menu_hand, admin_for_games, advertising
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
        time = datetime.now().strftime("%H:%M:%S")
        #удаление дневного счетчика
        if time == '19:00:01':
            await day_count(count_delete=True)
        if time == '14:03:01':
            await start_spam('2022.07.12 14:10')
        if time == '14:05:01':
            await start_spam('2022.07.12 14:20')
        if time == '14:10:01':
            await start_spam('2022.07.12 14:30')
        if time == '14:15:01':
            await start_spam('2022.07.12 14:40')
        if time == '14:20:01':
            await start_spam('2022.07.12 14:50')
        if time == '15:25:01':
            await start_spam('2022.07.12 15:00')
        if time == '15:30:01':
            await start_spam('2022.07.12 15:10')
        if time == '15:35:01':
            await start_spam('2022.07.12 15:20')
        if time == '15:40:01':
            await start_spam('2022.07.12 15:30')
        if time == '15:45:01':
            await start_spam('2022.07.12 15:40')
        if time == '15:50:01':
            await start_spam('2022.07.12 15:50')
        if time == '16:55:01':
            await start_spam('2022.07.12 16:00')
        if time == '17:00:01':
            await start_spam('2022.07.12 16:10')
        if time == '17:05:01':
            await start_spam('2022.07.12 16:20')
        if time == '17:10:01':
            await start_spam('2022.07.12 16:30')
        if time == '17:20:01':
            await start_spam('2022.07.12 16:40')
        if time == '17:30:01':
            await start_spam('2022.07.12 16:50')
        if time == '17:40:01':
            await start_spam('2022.07.12 17:00')
        if time == '17:50:01':
            await start_spam('2022.07.12 17:10')
        await asyncio.sleep(0.5)



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
    dp.include_router(advertising.router)
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

