from bata import all_data
import asyncio
import sys

from aiogram import Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from psycopg2 import Error
from bata import all_data
from handlers import admin_hand, start_hand, anti_prop_hand, smi_hand, donbass_hand, true_resons_hand
from handlers.started_message import welcome_messages
from handlers.other import other_file
from log import logg


def tables_god():
    try:
        # Подключение к существующей базе данных
        con = all_data().get_postg()
        # Курсор для выполнения операций с базой данных
        cur = con.cursor()
        con.autocommit = True

        # Выполнение SQL-запроса

        cur.execute("SELECT version();")
        record = cur.fetchone()
        logg.get_info(f"You connect to - {record}, \n")

        # Удаление таблицы

        cur.execute("DROP TABLE IF EXISTS putin_lies")
        logg.get_info("Table putin_lies has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS truthgame")
        logg.get_info("Table truthgame has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS texts")
        logg.get_info("Table texts has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS assets")
        logg.get_info("Table assets has been deleted".upper())

        # Создание таблиц

        cur.execute('''CREATE TABLE IF NOT EXISTS texts(
                    "text" TEXT NOT NULL,
                    "name" TEXT NOT NULL PRIMARY KEY
                    )''')
        logg.get_info("Texts table created".upper())

        cur.execute('''CREATE TABLE IF NOT EXISTS assets(
                "t_id" TEXT NOT NULL,
                "name" TEXT NOT NULL PRIMARY KEY
                )''')
        logg.get_info("Assets table created".upper())

        cur.execute('''CREATE TABLE public.truthgame (
    	            "id" int4 NOT NULL,
    	            truth bool NOT NULL,
    	            asset_name varchar NULL,
    	            text_name varchar NULL,
    	            belivers int4 NOT NULL,
    	            nonbelivers int4 NOT NULL,
    	            rebuttal varchar NULL,
    	            CONSTRAINT truthgame_pk PRIMARY KEY (id));''')

        cur.execute(
            'ALTER TABLE public.truthgame ADD CONSTRAINT truthgame_fk FOREIGN KEY (asset_name) REFERENCES public.assets("name");')
        cur.execute(
            'ALTER TABLE public.truthgame ADD CONSTRAINT truthgame_fk_1 FOREIGN KEY (text_name) REFERENCES public.texts("name");')

        logg.get_info("Truthgame table is created".upper())

        cur.execute('''CREATE TABLE public.putin_lies (
                            id int4 NOT NULL,
                            asset_name varchar(50) NULL,
                            text_name varchar(50) NULL,
                            belivers int4 NULL,
                            nonbelivers int4 NULL,
                            rebuttal varchar(50) NULL,
                            CONSTRAINT putin_lies_pk PRIMARY KEY (id)
                        );''')

        cur.execute(
            'ALTER TABLE public.putin_lies ADD CONSTRAINT putin_lies_fk FOREIGN KEY (text_name) REFERENCES public.texts("name");')
        cur.execute(
            'ALTER TABLE public.putin_lies ADD CONSTRAINT putin_lies_fk_1 FOREIGN KEY (asset_name) REFERENCES public.assets("name");')

        logg.get_info("PUTIN LIES".upper())

        try:
            csv_file_name = 'resources/assets.csv'
            sql = "COPY assets FROM STDIN DELIMITER ',' CSV HEADER"
            cur.copy_expert(sql, open(csv_file_name, "r"))
        except Exception as error:
            logg.get_error(f"{error}", __file__)
        try:
            csv_file_name = 'resources/texts.csv'
            sql = "COPY texts FROM STDIN DELIMITER ',' CSV HEADER"
            cur.copy_expert(sql, open(csv_file_name, "r"))
        except Exception as error:
            logg.get_error(f"{error}", __file__)
        try:
            csv_file_name = 'resources/truthgame.csv'
            sql = "COPY truthgame FROM STDIN DELIMITER ',' CSV HEADER"
            cur.copy_expert(sql, open(csv_file_name, "r"))
        except Exception as error:
            logg.get_error(f"{error}", __file__)
        try:
            csv_file_name = 'resources/putin_lies.csv'
            sql = "COPY putin_lies FROM STDIN DELIMITER ',' CSV HEADER"
            cur.copy_expert(sql, open(csv_file_name, "r"))
        except Exception as error:
            logg.get_error(f"{error}", __file__)

        con.close()
        cur.close()


    except (Exception, Error) as error:
        logg.get_error(f"PostgreSQL, {error}", __file__)
