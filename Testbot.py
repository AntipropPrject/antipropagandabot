import asyncio
from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import bata
from bata import all_data
from export_to_csv import pg_mg
from handlers import start_hand, shop
from handlers.admin_handlers import admin_factory, marketing, admin_for_games, new_admin_hand
from handlers.other import status, other_file, reports
from handlers.story import preventive_strike, true_resons_hand, welcome_messages, nazi_hand, \
    donbass_hand, main_menu_hand, anti_prop_hand, putin_hand, smi_hand, stopwar_hand, welcome_stories, true_goals_hand, \
    power_change_hand, nato_hand, mob_hand
from middleware.trottling import ThrottlingMiddleware
from periodic_func import periodic
from utilts import happy_tester

data = all_data()
bot = data.get_bot()
storage = RedisStorage.from_url(data.redis_url)
dp = Dispatcher(storage)


async def on_startup(dispatcher: Dispatcher) -> None:
    asyncio.create_task(periodic())
    webhook = await bot.get_webhook_info()
    if webhook is not None:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook("https://kamaga777123.xyz/")
    else:
        await bot.set_webhook("https://kamaga777123.xyz/")

    webhook = await bot.get_webhook_info()

    print(webhook)
    print(webhook)
    print(webhook)

    print("🚀 Bot launched as Hoook!")
    print(f"webhook: https://kamaga777123.xyz/")


async def main():
    bot_info = await bot.get_me()

    print(f"Hello, i'm {bot_info.first_name} | {bot_info.username}")

    if bata.Check_tickets is True:
        await happy_tester(bot)
    else:
        print('Tickets checking is disabled, so noone will know...')


async def on_shutdown(dispatcher: Dispatcher) -> None:
    print("😴 Bot shutdown...")

    await bot.delete_webhook()
    await dispatcher.storage.close()


def configure_app(dp, bot) -> web.Application:
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="")
    setup_application(app, dp, bot=bot)
    return app


def main():
    # Технические роутеры
    # TablesCreator.tables_god()
    dp.include_router(reports.router)
    dp.include_router(pg_mg.router)
    dp.include_router(new_admin_hand.router)
    dp.include_router(admin_factory.router)
    dp.include_router(marketing.router)
    dp.include_router(admin_for_games.router)

    dp.include_router(status.router)
    dp.include_router(start_hand.router)

    # Начало и антипропаганда
    dp.include_router(welcome_stories.router)
    dp.include_router(welcome_messages.router)
    dp.include_router(anti_prop_hand.router)
    dp.include_router(smi_hand.router)

    # Роутеры причин войны
    dp.include_router(true_goals_hand.router)
    dp.include_router(power_change_hand.router)
    dp.include_router(nato_hand.router)
    dp.include_router(shop.router)
    dp.include_router(true_resons_hand.router)
    dp.include_router(donbass_hand.router)
    dp.include_router(nazi_hand.router)
    dp.include_router(preventive_strike.router)
    dp.include_router(putin_hand.router)
    dp.include_router(stopwar_hand.router)
    dp.include_router(mob_hand.router)
    dp.include_router(main_menu_hand.router)


    dp.message.middleware(ThrottlingMiddleware())
    # Роутер для неподошедшего

    dp.include_router(other_file.router)

    # session = aiohttp.ClientSession()
    # use the session here

    # periodic function

    # await session.close()
    # await dp.start_polling(bot)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    app = configure_app(dp, bot)
    web.run_app(app, host="0.0.0.0", port=1443)


if __name__ == "__main__":
    main()
