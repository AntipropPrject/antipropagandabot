# - *- coding: utf- 8 - *-
import logging
from colorama import Fore


def get_info(text):
    file_log = logging.FileHandler('logs.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file_log, console_out), format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)

    logging.info(text)


def get_error(text, file_name=None):
    print(f"{Fore.RED}[ERROR] FILE: {file_name} | " + Fore.WHITE + text)
    logging.basicConfig(
        level=logging.ERROR,
        filename="logs.log",
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )
    logging.error(text)
