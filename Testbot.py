import asyncio
from aiogram import Dispatcher, __all__
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiohttp import web

import logging
from urllib.parse import urljoin

from aiogram import Bot, Dispatcher, executor, types


from bata import all_data
from handlers import start_hand, anti_prop_hand, smi_hand, donbass_hand, true_resons_hand, putin_hand, \
    stopwar_hand, nazi_hand, preventive_strike, new_admin_hand, welcome_messages
from export_to_csv import pg_mg
from handlers.other import other_file
from data_base import TablesCreator

WEBHOOK_HOST = "https://ec2-16-170-206-95.eu-north-1.compute.amazonaws.com/"
WEBHOOK_PATH = "Testbot.py"
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_PATH)

TablesCreator.tables_god()

data = all_data()
bot = data.get_bot()
storage = RedisStorage.from_url(data.redis_url)
dp = Dispatcher(storage)

async def on_startup(dispatcher: Dispatcher) -> None:

    logging.info("🚀 Bot launched as Serverless!")
    logging.info(f"webhook: {WEBHOOK_URL}")

    webhook = await bot.get_webhook_info()

    if webhook.url:
        await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dispatcher: Dispatcher) -> None:
    logging.warning("😴 Bot shutdown...")

    await bot.delete_webhook()
    await dispatcher.storage.close()


def bot_register():

    # Технические роутеры

    dp.include_router(pg_mg.router)
    dp.include_router(new_admin_hand.router)
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

    # Роутер для неподошедшего
    dp.include_router(other_file.router)

    bot.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port="8080",
    )

    # await bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot)



