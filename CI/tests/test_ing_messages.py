import asyncio
import os
import unittest

import pytest
from aiogram import Bot, Dispatcher

from Testbot import main
from CI.tests import test_hand
from CI.tests.updates_for_bot import test_message


@pytest.mark.asyncio
class TestMessages:

    async def test_smoke(self):
        bot = Bot(os.getenv('BOT_TOKEN'))
        print((await bot.get_me()).first_name)
        dp = Dispatcher()
        dp.include_router(test_hand.router)
        result = await dp.feed_update(bot, test_message)
        assert result == 'Smoketesting was succчessfull'

    async def test_bot_door(self):
        try:
            await asyncio.wait_for(main(), 5)
        except asyncio.exceptions.TimeoutError:
            pass


if __name__ == '__main__':
    unittest.main()
