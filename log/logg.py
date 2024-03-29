from datetime import datetime
from colorama import Fore
import logging
from bata import all_data

data = all_data()
bot = data.get_bot()


def get_info(text):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    file_log = logging.FileHandler(f'log/logs/Log-{today}.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file_log, console_out), format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)

    logging.info(text)


async def get_error(text, file_name=None):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")

    print(f"{Fore.RED}[ERROR] FILE: {file_name} | " + Fore.WHITE + text)
    logging.basicConfig(
        level=logging.ERROR,
        filename=f'log/logs/Log-{today}.log',
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )

    await bot.send_message(chat_id='-1001397216477', text=f"ОШИБКА\n\n"
                                                          f"___________\n"
                                                          f"{text}")



