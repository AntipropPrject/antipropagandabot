# - *- coding: utf- 8 - *-
import logging
from colorama import init, Fore
from colorama import Back
from colorama import Style

def get_info(text):
    print(f"{Fore.GREEN}[INFO] | " + Fore.WHITE + text)
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.log",
        format=u'[%(levelname)s] [%(asctime)s] | %(message)s',
        datefmt="%d-%b-%y %H:%M:%S"
    )
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
