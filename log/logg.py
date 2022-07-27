import os
from datetime import datetime

from aiogram import loggers
from colorama import Fore
import logging
from bata import all_data
import pathlib

data = all_data()
bot = data.get_bot()

today = datetime.today().strftime("%d-%m-%Y")

pathlib.Path('statlogs/').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    filename=f'log/logs/Log-{today}.log',
    format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
    datefmt="%d-%m-%y %H:%M:%S"
)

infolog = loggers.event
infolog.setLevel(logging.INFO)
infolog.addHandler(logging.FileHandler(filename=f"statlogs/{today}.log", mode='a'))



def get_info(text):
    today_for_log = datetime.now().strftime('%Y-%m-%d')
    logging.basicConfig(
        level=logging.ERROR,
        filename=f'log/logs/Log-{today_for_log}.log',
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )

    # await bot.send_message(chat_id='-1001397216477', text=f"ОШИБКА\n\n"
    #                                                      f"___________\n"
    #                                                      f"{text}")
    logger = logging.getLogger()
    logger.info(text)


async def get_error(text, file_name=None):
    today_for_log = datetime.now().strftime('%Y-%m-%d')
    print(f"{Fore.RED}[ERROR] FILE: {file_name} | " + Fore.WHITE + text)
    logging.basicConfig(
        level=logging.ERROR,
        filename=f'log/logs/Log-{today_for_log}.log',
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )

    # await bot.send_message(chat_id='-1001397216477', text=f"ОШИБКА\n\n"
    #                                                      f"___________\n"
    #                                                      f"{text}")
    logger = logging.getLogger()
    logger.error(text)


async def admin_logs(id, name, text):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    current_datetime = datetime.now()
    ch = current_datetime.hour
    mn = current_datetime.minute
    path = 'log/admin_logs'
    file_path = str(id)
    log_text = f"[USER: {name} | ID: {id} | DT: {today}_{ch}:{mn}]: {text}"
    try:
        if not os.path.exists(path): os.makedirs(path)
    except OSError:
        await get_error("Создать директорию %s не удалось" % path)
    with open(f"{path}/{file_path}", 'a') as file:
        file.write(log_text+'\n')



