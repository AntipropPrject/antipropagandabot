import asyncio
from datetime import datetime

from data_base.DBuse import redis_just_one_read
from day_func import day_count
from export_to_csv.pg_mg import Backup
from handlers.advertising import start_spam
from log.logg import get_logger

logger = get_logger('periodic')

async def periodic():
    print('periodic function has been started')
    backup = Backup()
    while True:
        status_spam = await redis_just_one_read('Usrs: admins: spam: status:')
        datefor_backup = datetime.now().strftime('%Y-%m-%d_%H-%M')
        c_time = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime('%Y.%m.%d')

        if c_time == '21:00:01':
            logger.info(f'Обнуление дневного счетчика')
            await day_count(count_delete=True)
        if c_time == '07:00:01':
            logger.info(f'Время {c_time}-- Запуск дампа баз')
            await backup.dump_all(name=f'DUMP_{datefor_backup}')
        if status_spam == '1':
            if c_time == '08:00:01':
                logger.info(f'Время {c_time}-- РАССЫЛКИ')
                await start_spam(f'{date} 11:00')
            if c_time == '16:00:01':
                logger.info(f'Время {c_time}-- РАССЫЛКИ')
                await start_spam(f'{date} 19:00')
        if c_time == '19:00:01':
            logger.info(f'Время {c_time}-- Запуск дампа баз')
            await backup.dump_all(name=f'DUMP_{datefor_backup}')
        await asyncio.sleep(1)
