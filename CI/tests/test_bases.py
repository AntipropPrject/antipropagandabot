import unittest

import pytest

from bata import all_data
from data_base.DBuse import data_getter, redis_just_one_write, redis_just_one_read


@pytest.mark.asyncio
class TestBases:

    async def test_postgres_connection(self):
        assert (await data_getter('SELECT 1'))[0][0] == 1

    async def test_redis_connection(self):
        await redis_just_one_write('1', 1)
        assert await redis_just_one_read('1') == '1'

    async def test_mongo_connection(self):
        client = all_data().get_mongo()
        database = client.base
        collection = database['test']
        await collection.insert_one({'1': 1})
        assert (await collection.find_one({'1': 1}))['1'] == 1


if __name__ == '__main__':
    unittest.main()
