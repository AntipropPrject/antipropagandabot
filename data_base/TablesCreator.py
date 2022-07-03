import psycopg2
from bata import all_data
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

        """# Удаление игровых таблиц
        cur.execute("DROP TABLE IF EXISTS ucraine_or_not_game")
        logg.get_info("Table ucraine_or_not_game has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS normal_game")
        logg.get_info("Table normal_game has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS putin_old_lies")
        logg.get_info("Table putin_old_lies has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS putin_lies")
        logg.get_info("Table putin_lies has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS truthgame")
        logg.get_info("Table truthgame has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS mistakeorlie")
        logg.get_info("Table mistakeorlie has been deleted".upper())

        # Удаление основных таблиц
        cur.execute("DROP TABLE IF EXISTS texts")
        logg.get_info("Table texts has been deleted".upper())
        cur.execute("DROP TABLE IF EXISTS assets")
        logg.get_info("Table assets has been deleted".upper())"""

        # Создание таблиц
        # cur.execute('''CREATE TABLE IF NOT EXISTS texts(
        #             "text" TEXT NOT NULL,
        #             "name" TEXT NOT NULL PRIMARY KEY
        #             )''')
        # logg.get_info("table text is created".upper())
        #
        # cur.execute('''CREATE TABLE IF NOT EXISTS assets(
        #         "t_id" TEXT NOT NULL,
        #         "name" TEXT NOT NULL PRIMARY KEY
        #         )''')
        # logg.get_info("table assets is created".upper())
        #
        # cur.execute('''CREATE TABLE public.truthgame(
        #         "id" int4 NOT NULL,
        #         truth bool NOT NULL,
        #         asset_name varchar NULL,
        #         text_name varchar NULL,
        #         belivers int4 NOT NULL,
        #         nonbelivers int4 NOT NULL,
        #         rebuttal varchar NULL,
        #         reb_asset_name varchar NULL,
        #         CONSTRAINT truthgame_pk PRIMARY KEY (id)
        #        );''')
        #
        # cur.execute('''ALTER TABLE public.truthgame
        #  ADD CONSTRAINT truthgame_fk
        #   FOREIGN KEY (asset_name)
        #    REFERENCES public.assets("name");''')
        # cur.execute('''ALTER TABLE public.truthgame
        #  ADD CONSTRAINT truthgame_fk_1
        #   FOREIGN KEY (text_name)
        #    REFERENCES public.texts("name");''')
        # cur.execute('''ALTER TABLE public.truthgame
        #  ADD CONSTRAINT truthgame_fk_2
        #   FOREIGN KEY (reb_asset_name)
        #    REFERENCES public.assets("name");''')
        # logg.get_info("table Truthgame is created".upper())
        #
        # cur.execute('''CREATE TABLE public.mistakeorlie(
        #                 "id" int4 NOT NULL,
        #                 truth bool NOT NULL,
        #                 asset_name varchar NULL,
        #                 text_name varchar NULL,
        #                 belivers int4 NOT NULL,
        #                 nonbelivers int4 NOT NULL,
        #                 rebuttal varchar NULL,
        #                 CONSTRAINT mistakeorlie_pk PRIMARY KEY (id)
        #                );''')
        #
        # cur.execute('''ALTER TABLE public.mistakeorlie
        #          ADD CONSTRAINT mistakeorlie_fk
        #           FOREIGN KEY (asset_name)
        #            REFERENCES public.assets("name");''')
        # cur.execute('''ALTER TABLE public.mistakeorlie
        #          ADD CONSTRAINT mistakeorlie_fk_1
        #           FOREIGN KEY (text_name)
        #            REFERENCES public.texts("name");''')
        # logg.get_info("mistakeorlie table is created".upper())
        #
        # cur.execute('''CREATE TABLE public.putin_lies (
        #                     id int4 NOT NULL,
        #                     asset_name varchar(50) NULL,
        #                     text_name varchar(50) NULL,
        #                     belivers int4 NULL,
        #                     nonbelivers int4 NULL,
        #                     rebuttal varchar(50) NULL,
        #                     CONSTRAINT putin_lies_pk PRIMARY KEY (id)
        #                 );''')
        #
        # cur.execute('''ALTER TABLE public.putin_lies
        #  ADD CONSTRAINT putin_lies_fk
        #   FOREIGN KEY (text_name)
        #    REFERENCES public.texts("name");''')
        # cur.execute('''ALTER TABLE public.putin_lies
        #  ADD CONSTRAINT putin_lies_fk_1
        #   FOREIGN KEY (asset_name)
        #    REFERENCES public.assets("name");''')
        # logg.get_info("PUTIN LIES".upper())
        #
        # cur.execute('''CREATE TABLE public.putin_old_lies (
        #                     id int4 NOT NULL,
        #                     asset_name varchar(50) NULL,
        #                     text_name varchar(50) NULL,
        #                     belivers int4 NULL,
        #                     nonbelivers int4 NULL,
        #                     rebuttal varchar(50) NULL,
        #                     CONSTRAINT putin_old_lies_pk PRIMARY KEY (id)
        #                 );''')
        #
        # cur.execute('''ALTER TABLE public.putin_old_lies
        #  ADD CONSTRAINT putin_old_lies_fk
        #   FOREIGN KEY (text_name)
        #    REFERENCES public.texts("name");''')
        # cur.execute('''ALTER TABLE public.putin_old_lies
        #  ADD CONSTRAINT putin_old_lies_fk_1
        #   FOREIGN KEY (asset_name)
        #    REFERENCES public.assets("name");''')
        # logg.get_info("Table putin_old_lies is CREATED".upper())
        #
        # cur.execute('''CREATE TABLE public.normal_game (
        #                     id int4 NOT NULL PRIMARY KEY,
        #                     asset_name varchar(50) NULL,
        #                     text_name varchar(50) NULL,
        #                     belivers int4 NULL,
        #                     nonbelivers int4 NULL,
        #                     rebuttal varchar(50) NULL
        #                 );''')
        #
        # cur.execute('''ALTER TABLE public.normal_game
        #  ADD CONSTRAINT normal_game_fk
        #   FOREIGN KEY (text_name)
        #    REFERENCES public.texts("name");''')
        # cur.execute('''ALTER TABLE public.normal_game
        #  ADD CONSTRAINT normal_game_fk_1
        #   FOREIGN KEY (asset_name)
        #    REFERENCES public.assets("name");''')
        # logg.get_info("table normal_game is here".upper())
        #
        # cur.execute('''CREATE TABLE public.ucraine_or_not_game (
        #                     id int4 NOT NULL PRIMARY KEY,
        #                     asset_name varchar(50) NULL,
        #                     text_name varchar(50) NULL,
        #                     belivers int4 NULL,
        #                     nonbelivers int4 NULL,
        #                     rebuttal varchar(50) NULL,
        #                     truth bool NOT NULL
        #                 );''')
        #
        # cur.execute('''ALTER TABLE public.ucraine_or_not_game
        #  ADD CONSTRAINT normal_game_fk
        #   FOREIGN KEY (text_name)
        #    REFERENCES public.texts("name");''')
        # cur.execute('''ALTER TABLE public.ucraine_or_not_game
        #  ADD CONSTRAINT normal_game_fk_1
        #   FOREIGN KEY (asset_name)
        #    REFERENCES public.assets("name");''')
        # logg.get_info("table ucraine_or_not_game is created".upper())

        # MONGODB
        # try:
        #     client = all_data().get_mongo()
        #     # get version
        #     logg.get_info(f"You connect to - server MongoDb version - {client.server_info()['version']} \n".upper())
        #     client.close()
        # except Exception as error:
        #     logg.get_error(f"MongoDB, {error}", __file__)
        #
        # # import CSV
        # try:
        #     csv_file_name = 'resources/assets.csv'
        #     sql = "COPY assets FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        # try:
        #     csv_file_name = 'resources/texts.csv'
        #     sql = "COPY texts FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        # try:
        #     csv_file_name = 'resources/truthgame.csv'
        #     sql = "COPY truthgame FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        # try:
        #     csv_file_name = 'resources/putin_lies.csv'
        #     sql = "COPY putin_lies FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        #
        # try:
        #     csv_file_name = 'resources/mistakeorlie.csv'
        #     sql = "COPY mistakeorlie FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        #
        # try:
        #     csv_file_name = 'resources/putin_old_lies.csv'
        #     sql = "COPY putin_old_lies FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        # try:
        #     csv_file_name = 'resources/normal_game.csv'
        #     sql = "COPY normal_game FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        # try:
        #     csv_file_name = 'resources/ucraine_or_not_game.csv'
        #     sql = "COPY ucraine_or_not_game FROM STDIN DELIMITER ',' CSV HEADER"
        #     cur.copy_expert(sql, open(csv_file_name, "r"))
        # except Exception as error:
        #     logg.get_error(f"{error}", __file__)
        #
        # con.close()
        # cur.close()

    except psycopg2.Error as error:
        logg.get_error(f"PostgreSQL, {error}", __file__)
