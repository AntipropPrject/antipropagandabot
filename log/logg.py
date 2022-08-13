import asyncio
import json
import logging
import logging.config
import os
import pathlib
from datetime import datetime

from aiogram import loggers

from bata import all_data

data = all_data()
bot = data.get_bot()


today_for_log = datetime.now().strftime('%Y-%m-%d')
pathlib.Path('statlogs/').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    filename=f'log/logs/Log-{today_for_log}.log',
    format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
    datefmt="%d-%m-%y %H:%M:%S"
)

infolog = loggers.event
infolog.setLevel(logging.INFO)
infolog.addHandler(logging.FileHandler(filename=f"statlogs/{today_for_log}.log", mode='a'))




FOLDER_LOG = "log"
LOGGING_CONFIG_FILE = 'loggers.json'

def create_log_folder(folder=FOLDER_LOG):
    if not os.path.exists(folder):
        os.mkdir(folder)

def get_logger(name, template='default'):
    create_log_folder()
    with open(LOGGING_CONFIG_FILE, "r") as f:
        dict_config = json.load(f)
        dict_config["loggers"][name] = dict_config["loggers"][template]
    logging.config.dictConfig(dict_config)
    return logging.getLogger(name)

def get_default_logger():
    create_log_folder()
    with open(LOGGING_CONFIG_FILE, "r") as f:
        logging.config.dictConfig(json.load(f))

    return logging.getLogger("default")


logger = get_logger('main')
def get_info(text):
    logger.info(text)




async def get_error(text, file_name=None):
    logger.error(text)
    asyncio.create_task(send_to_chat(f"File: {file_name}\n\nError: {text}"))


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


async def send_to_chat(text):
    try:
        bot_info = await bot.get_me()
        await bot.send_message(chat_id='-1001397216477', text=f"Hello, im {bot_info.first_name}\n\n" + text)
    except:
        print("Мне не удалось найти бота в канале для ошибок, сори")



