import asyncio
from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from bata import all_data
from handlers import admin_hand, start_hand, anti_prop_hand,\
    smi_hand, donbass_hand, true_resons_hand, putin_hand, stopwar_hand, nazi_hand, preventive_strike, su_admin
from handlers.started_message import welcome_messages
from handlers.other import other_file
from data_base import TablesCreator


TablesCreator.tables_god()

data = all_data()
bot = data.get_bot()
storage = RedisStorage.from_url(data.redis_url)
dp = Dispatcher(storage)


async def main():
    # Технические роутеры
    dp.include_router(su_admin.router)
    dp.include_router(admin_hand.router)
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

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

