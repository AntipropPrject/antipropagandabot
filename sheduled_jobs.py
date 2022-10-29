import asyncio
from datetime import datetime

from data_base.DBuse import redis_just_one_read
from day_func import day_count
from export_to_csv.pg_mg import Backup
from handlers.advertising import start_spam, return_spam_send_task
from log.logg import get_logger

logger = get_logger('periodic')


async def return_spam_send():
    asyncio.create_task(return_spam_send_task(datetime.now()))


async def backups():
    print('Backing data')
    backup = Backup()
    datefor_backup = datetime.now().strftime('%Y-%m-%d_%H-%M')
    await backup.dump_all(name=f'DUMP_{datefor_backup}')


async def periodic_advs():
    print("Mailing")
    # Включение/выключение можно попробовать сделать через планировщик
    status_spam = await redis_just_one_read('Usrs: admins: spam: status:')
    if status_spam == '1':
        await start_spam()