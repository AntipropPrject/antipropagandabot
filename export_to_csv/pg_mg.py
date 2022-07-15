import asyncio
import os
from datetime import datetime
import psycopg2
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
import pandas
from aiogram import Router, F
from aiogram import types
import zipfile
from filters.isAdmin import IsSudo
from log import logg
from log.logg import get_error
from states.admin_states import admin

router = Router()



@router.message(IsSudo(), F.text.contains('Экспорт') | F.text.contains('Создать копию'))
async def export(message: types.Message, state: FSMContext):
    await mongo_export_to_file()
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    current_datetime = datetime.now()
    ch = current_datetime.hour
    mn = current_datetime.minute
    try:
        await message.answer_document(FSInputFile(f"export_to_csv/backups/backup-{today}-{ch}-{mn}.zip"),
                                      caption=f"Type: backup base\n\n"
                                              f"Date: {today}\n"
                                              f"Time: {ch}:{mn} (UTC)")
        await asyncio.sleep(0.1)
        await message.answer_document(FSInputFile(f'log/logs/Log-{today}.log'), caption=f"Type: logs\n\n"
                                                                                        f"Date: {today}\n"
                                                                                        f"Time: {ch}:{mn} (UTC)")

        if message.text == 'Создать копию':
            nmarkup = ReplyKeyboardBuilder()
            nmarkup.row(types.KeyboardButton(text="Назад"))
            await message.answer("Теперь вы можете продолжить восстановление\n\n"
                                 "Отправьте мне backup архив для восстановления базы.",
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
            await state.set_state(admin.import_csv)
    except:
        await message.answer("Файл не успел отправиться, возможно стоит доработать эту функцию")




async def mongo_export_to_file():
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    current_datetime = datetime.now()
    ch = current_datetime.hour
    mn = current_datetime.minute
    client = all_data().get_mongo()
    database = client['database']
    collection_1 = database['userinfo']
    collection_2 = database['statistics']
    collection_3 = database['admins']
    collection_4 = database['spam_actual_news']
    collection_5 = database['spam_news_main']
    collection_6 = database['user_games']
    collection_7 = database['useranswer']
    # make an API call to the MongoDB server
    mongo_docs_1 = collection_1.find()
    mongo_docs_2 = collection_2.find()
    mongo_docs_3 = collection_3.find()
    mongo_docs_4 = collection_4.find()
    mongo_docs_5 = collection_5.find()
    mongo_docs_6 = collection_6.find()
    mongo_docs_7 = collection_7.find()
    # Convert the mongo docs to a DataFrame
    docs_1 = pandas.DataFrame(mongo_docs_1)
    docs_2 = pandas.DataFrame(mongo_docs_2)
    docs_3 = pandas.DataFrame(mongo_docs_3)
    docs_4 = pandas.DataFrame(mongo_docs_4)
    docs_5 = pandas.DataFrame(mongo_docs_5)
    docs_6 = pandas.DataFrame(mongo_docs_6)
    docs_7 = pandas.DataFrame(mongo_docs_7)

    path = 'export_to_csv/backups'
    path_mongo = 'export_to_csv/backups/MongoDB'
    path_pg = 'export_to_csv/backups/PostgreSQL'
    path_games = 'export_to_csv/backups/games'
    try:
        if not os.path.exists(path): os.makedirs(path)
        if not os.path.exists(path_mongo): os.makedirs(path_mongo)
        if not os.path.exists(path_pg): os.makedirs(path_pg)
        if not os.path.exists(path_games): os.makedirs(path_games)
    except OSError:
        await get_error("Создать директорию %s не удалось" % path)
    try:
        export_zip = zipfile.ZipFile(rf'export_to_csv/backups/backup-{today}-{ch}-{mn}.zip', 'w')
    except Exception as er:
        await logg.get_error(er)
    # compute the output file directory and name
    output_dir_mongo = os.path.join('export_to_csv', 'backups', 'MongoDB')
    output_file_1 = os.path.join(output_dir_mongo, 'Mongo_user-' + today + '.csv')
    output_file_2 = os.path.join(output_dir_mongo, 'Mongo_statistics-' + today + '.csv')
    output_file_3 = os.path.join(output_dir_mongo, 'Mongo_admins-' + today + '.csv')
    output_file_4 = os.path.join(output_dir_mongo, 'Mongo_spam_actual_news-' + today + '.csv')
    output_file_5 = os.path.join(output_dir_mongo, 'Mongo_spam_news_main-' + today + '.csv')
    output_file_6 = os.path.join(output_dir_mongo, 'Mongo_user_games-' + today + '.csv')
    output_file_7 = os.path.join(output_dir_mongo, 'Mongo_useranswer-' + today + '.csv')

    docs_1.to_csv(output_file_1, ",", index=False)
    export_zip.write(output_file_1)
    docs_2.to_csv(output_file_2, ",", index=False)
    export_zip.write(output_file_2)
    docs_3.to_csv(output_file_3, ",", index=False)
    export_zip.write(output_file_3)
    docs_4.to_csv(output_file_4, ",", index=False)
    export_zip.write(output_file_4)
    docs_5.to_csv(output_file_5, ",", index=False)
    export_zip.write(output_file_5)
    docs_6.to_csv(output_file_6, ",", index=False)
    export_zip.write(output_file_6)
    docs_7.to_csv(output_file_7, ",", index=False)
    export_zip.write(output_file_7)

    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            SQL_texts = "COPY (SELECT * FROM texts) TO STDOUT WITH CSV HEADER"
            SQL_assets = "COPY (SELECT * FROM assets) TO STDOUT WITH CSV HEADER"
            SQL_putin_lies = "COPY (SELECT * FROM putin_lies) TO STDOUT WITH CSV HEADER"
            SQL_putin_old_lies = "COPY (SELECT * FROM putin_old_lies) TO STDOUT WITH CSV HEADER"
            SQL_truthgame = "COPY (SELECT * FROM truthgame) TO STDOUT WITH CSV HEADER"
            SQL_normal_game = "COPY (SELECT * FROM normal_game) TO STDOUT WITH CSV HEADER"
            SQL_mistakeorlie = "COPY (SELECT * FROM mistakeorlie) TO STDOUT WITH CSV HEADER"
            SQL_ucraine_or_not_game = "COPY (SELECT * FROM ucraine_or_not_game) TO STDOUT WITH CSV HEADER"
            # Set up a variable to store our file path and name.
            t_path_n_texts = rf"export_to_csv/backups/PostgreSQL/texts.csv"
            t_path_n_assets = rf"export_to_csv/backups/PostgreSQL/assets.csv"
            t_path_n_mistakeorlie = rf"export_to_csv/backups/games/mistakeorlie.csv"
            t_path_n_putin_lies = rf"export_to_csv/backups/games/putin_lies.csv"
            t_path_n_putin_old_lies = rf"export_to_csv/backups/games/putin_old_lies.csv"
            t_path_n_normal_game = rf"export_to_csv/backups/games/normal_game.csv"
            t_path_n_truthgame = rf"export_to_csv/backups/games/truthgame.csv"
            t_path_n_ucraine_or_not_game = rf"export_to_csv/backups/games/ucraine_or_not_game.csv"
            # Trap errors for opening the file
            try:
                with open(t_path_n_texts, 'w') as f_output:
                    cur.copy_expert(SQL_texts, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_assets, 'w') as f_output:
                    cur.copy_expert(SQL_assets, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_mistakeorlie, 'w') as f_output:
                    cur.copy_expert(SQL_mistakeorlie, f_output)

            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_putin_lies, 'w') as f_output:
                    cur.copy_expert(SQL_putin_lies, f_output)

            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_putin_old_lies, 'w') as f_output:
                    cur.copy_expert(SQL_putin_old_lies, f_output)

            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_truthgame, 'w') as f_output:
                    cur.copy_expert(SQL_truthgame, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)

            try:
                with open(t_path_n_normal_game, 'w') as f_output:
                    cur.copy_expert(SQL_normal_game, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)
            try:
                with open(t_path_n_ucraine_or_not_game, 'w') as f_output:
                    cur.copy_expert(SQL_ucraine_or_not_game, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)
    try:
        export_zip.write(t_path_n_texts)
        export_zip.write(t_path_n_assets)
        export_zip.write(t_path_n_mistakeorlie)
        export_zip.write(t_path_n_putin_lies)
        export_zip.write(t_path_n_putin_old_lies)
        export_zip.write(t_path_n_truthgame)
        export_zip.write(t_path_n_normal_game)
        export_zip.write(t_path_n_ucraine_or_not_game)
        mydir_games = 'export_to_csv/backups/games'
        mydir_MongoDB = 'export_to_csv/backups/MongoDB'
        mydir_PostgreSQL = 'export_to_csv/backups/PostgreSQL'
        filelist = [f for f in os.listdir(mydir_games) if f.endswith(".csv")]
        for f in filelist:
            os.remove(os.path.join(mydir_games, f))
        filelist = [f for f in os.listdir(mydir_MongoDB) if f.endswith(".csv")]
        for f in filelist:
            os.remove(os.path.join(mydir_MongoDB, f))
        filelist = [f for f in os.listdir(mydir_PostgreSQL) if f.endswith(".csv")]
        for f in filelist:
            os.remove(os.path.join(mydir_PostgreSQL, f))
    except Exception as er:
        await logg.get_error(f"ЭКСПОРТ: {er}")
    export_zip.close()


async def backin():
    con = all_data().get_postg()
    # Курсор для выполнения операций с базой данных
    cur = con.cursor()
    con.autocommit = True
    # Удаление игровых таблиц
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
    logg.get_info("Table assets has been deleted".upper())

    # Создание таблиц
    cur.execute('''CREATE TABLE IF NOT EXISTS texts(
                        "text" TEXT NOT NULL,
                        "name" TEXT NOT NULL PRIMARY KEY
                        )''')
    logg.get_info("table text is created".upper())

    cur.execute('''CREATE TABLE IF NOT EXISTS assets(
                    "t_id" TEXT NOT NULL,
                    "name" TEXT NOT NULL PRIMARY KEY
                    )''')
    logg.get_info("table assets is created".upper())

    cur.execute('''create table truthgame
                (
                    id             integer not null
                        constraint truthgame_pk
                            primary key,
                    truth          boolean not null,
                    asset_name     varchar
                        constraint truthgame_fk
                            references assets,
                    text_name      varchar
                        constraint truthgame_fk_1
                            references texts,
                    belivers       integer not null,
                    nonbelivers    integer not null,
                    rebuttal       varchar
                        constraint "Text_rebbuttal"
                            references texts,
                    reb_asset_name varchar
                        constraint truthgame_fk_2
                            references assets
                );
                ''')


    cur.execute('''CREATE TABLE public.mistakeorlie(
                            "id" int4 NOT NULL,
                            asset_name varchar NULL,
                            belivers int4 NOT NULL,
                            nonbelivers int4 NOT NULL,
                            rebuttal varchar NULL,
                            text_name varchar NULL,
                            truth boolean NULL,
                            CONSTRAINT mistakeorlie_pk PRIMARY KEY (id)
                           );''')

    cur.execute('''ALTER TABLE public.mistakeorlie
                     ADD CONSTRAINT mistakeorlie_fk
                      FOREIGN KEY (asset_name)
                       REFERENCES public.assets("name");''')
    cur.execute('''ALTER TABLE public.mistakeorlie
                     ADD CONSTRAINT mistakeorlie_fk_1
                      FOREIGN KEY (text_name)
                       REFERENCES public.texts("name");''')
    logg.get_info("mistakeorlie table is created".upper())

    cur.execute('''CREATE TABLE public.putin_lies (
                                id int4 NOT NULL,
                                asset_name varchar(50) NULL,
                                text_name varchar(50) NULL,
                                belivers int4 NULL,
                                nonbelivers int4 NULL,
                                rebuttal varchar(50) NULL,
                                CONSTRAINT putin_lies_pk PRIMARY KEY (id)
                            );''')

    cur.execute('''ALTER TABLE public.putin_lies
             ADD CONSTRAINT putin_lies_fk
              FOREIGN KEY (text_name)
               REFERENCES public.texts("name");''')
    cur.execute('''ALTER TABLE public.putin_lies
             ADD CONSTRAINT putin_lies_fk_1
              FOREIGN KEY (asset_name)
               REFERENCES public.assets("name");''')
    logg.get_info("PUTIN LIES".upper())

    cur.execute('''CREATE TABLE public.putin_old_lies (
                                id int4 NOT NULL,
                                asset_name varchar(50) NULL,
                                text_name varchar(50) NULL,
                                belivers int4 NULL,
                                nonbelivers int4 NULL,
                                rebuttal varchar(50) NULL,
                                CONSTRAINT putin_old_lies_pk PRIMARY KEY (id)
                            );''')

    cur.execute('''ALTER TABLE public.putin_old_lies
             ADD CONSTRAINT putin_old_lies_fk
              FOREIGN KEY (text_name)
               REFERENCES public.texts("name");''')
    cur.execute('''ALTER TABLE public.putin_old_lies
             ADD CONSTRAINT putin_old_lies_fk_1
              FOREIGN KEY (asset_name)
               REFERENCES public.assets("name");''')
    logg.get_info("Table putin_old_lies is CREATED".upper())

    cur.execute('''CREATE TABLE public.normal_game (
                                id int4 NOT NULL PRIMARY KEY,
                                asset_name varchar(50) NULL,
                                text_name varchar(50) NULL,
                                belivers int4 NULL,
                                nonbelivers int4 NULL,
                                rebuttal varchar(50) NULL
                            );''')

    cur.execute('''ALTER TABLE public.normal_game
             ADD CONSTRAINT normal_game_fk
              FOREIGN KEY (text_name)
               REFERENCES public.texts("name");''')
    cur.execute('''ALTER TABLE public.normal_game
             ADD CONSTRAINT normal_game_fk_1
              FOREIGN KEY (asset_name)
               REFERENCES public.assets("name");''')
    logg.get_info("table normal_game is here".upper())

    cur.execute('''CREATE TABLE public.ucraine_or_not_game (
                                id int4 NOT NULL PRIMARY KEY,
                                asset_name varchar(50) NULL,
                                text_name varchar(50) NULL,
                                belivers int4 NULL,
                                nonbelivers int4 NULL,
                                rebuttal varchar(50) NULL,
                                truth bool NOT NULL
                            );''')

    cur.execute('''ALTER TABLE public.ucraine_or_not_game
             ADD CONSTRAINT normal_game_fk
              FOREIGN KEY (text_name)
               REFERENCES public.texts("name");''')
    cur.execute('''ALTER TABLE public.ucraine_or_not_game
             ADD CONSTRAINT normal_game_fk_1
              FOREIGN KEY (asset_name)
               REFERENCES public.assets("name");''')
    logg.get_info("table ucraine_or_not_game is created".upper())

    path_in = "export_to_csv/backin/export_to_csv/backups/"
    # backin CSV
    try:
        csv_file_name = path_in + 'PostgreSQL/assets.csv'
        sql = "COPY assets FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'PostgreSQL/texts.csv'
        sql = "COPY texts FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/truthgame.csv'
        sql = "COPY truthgame FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/putin_lies.csv'
        sql = "COPY putin_lies FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/mistakeorlie.csv'
        sql = "COPY mistakeorlie FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/putin_old_lies.csv'
        sql = "COPY putin_old_lies FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/normal_game.csv'
        sql = "COPY normal_game FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    try:
        csv_file_name = path_in + 'games/ucraine_or_not_game.csv'
        sql = "COPY ucraine_or_not_game FROM STDIN DELIMITER ',' CSV HEADER"
        cur.copy_expert(sql, open(csv_file_name, "r"))
    except Exception as error:
        await logg.get_error(f"{error}", __file__)
    return True

