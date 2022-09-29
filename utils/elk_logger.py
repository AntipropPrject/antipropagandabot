import logging
# from logstash_async.handler import AsynchronousLogstashHandler
from aiogram import types, Router
from aiogram.types import update

router = Router()



class Logger():
    def log(log: str):
        host = 'localhost'
        port = 5000
        logger = logging.getLogger('antiprop-logging')
        logger.setLevel(logging.DEBUG)
        # async_handler=AsynchronousLogstashHandler(host,port,database_path=None)
        # logger.addHandler(async_handler)
        return logger.info(log)


@router.message()
@router.callback_query()
@router.poll_answer()
async def logsmth(update: types.Update, state='*'):
    Logger.log("Any info")
