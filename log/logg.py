# - *- coding: utf- 8 - *-
import logging
from datetime import datetime

from colorama import Fore


def get_info(text):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    file_log = logging.FileHandler(f'Log/logs/log-{today}.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file_log, console_out), format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)

    logging.info(text)


def get_error(text, file_name=None):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    print(f"{Fore.RED}[ERROR] FILE: {file_name} | " + Fore.WHITE + text)
    logging.basicConfig(
        level=logging.ERROR,
        filename=f'Log/logs/log-{today}.log',
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )
    logging.error(text)
