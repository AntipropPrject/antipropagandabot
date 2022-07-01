import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# from app.config_reader import config


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook("https://ip-172-31-43-167.eu-north-1.compute.internal")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook()


def configure_app(dp, bot) -> web.Application:
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook.path)
    setup_application(app, dp, bot=bot)
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=config.bot_token, parse_mode="html")
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    app = configure_app(dp, bot)
    web.run_app(app, host=config.webapp.host, port=config.webapp.port)


if __name__ == '__main__':
    main()