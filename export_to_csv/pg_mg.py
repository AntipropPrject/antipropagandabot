import asyncio
import os
import shutil
from datetime import datetime
import bson
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo.errors import BulkWriteError

from bata import all_data
from aiogram import Router, F
from aiogram import types
import zipfile

from data_base.connect_pool import get_cursor
from filters.isAdmin import IsSudo
from log import logg
from states.admin_states import admin

router = Router()


@router.message(IsSudo(), F.text.contains('Экспорт') | F.text.contains('Создать копию'))
async def export(message: types.Message, state: FSMContext):
    print(1)
    backup = Backup()
    today = datetime.now().strftime('%Y-%m-%d_%H-%M')
    await backup.dump_all(name=f'DUMP_{today}')
    print(f"export_to_csv/backups/DUMP_{today}.zip")
    try:
        await message.answer_document(FSInputFile(f"export_to_csv/backups/DUMP_{today}.zip"),
                                      caption=f"Type: backup base\n\n"
                                              f"Date: {today} (UTC)")
        if message.text == 'Создать копию':
            nmarkup = ReplyKeyboardBuilder()
            nmarkup.row(types.KeyboardButton(text="Назад"))
            await message.answer("Теперь вы можете продолжить восстановление\n\n"
                                 "Отправьте мне backup архив для восстановления базы.",
                                 reply_markup=nmarkup.as_markup(resize_keyboard=True))
            await state.set_state(admin.import_csv)
    except Exception as e:
        print(e)
        await message.answer("Файл не успел отправиться, возможно стоит доработать эту функцию")


class Backup:
    def __init__(self):
        self._db_name = 'database'
        self.db = all_data().get_mongo()[self._db_name]
        self.dump_name = 'dump'
        self.path_to_zip = 'export_to_csv/backups/'
        self.path_files = 'export_to_csv/data_/'
        self.datetime = datetime.now().strftime('%Y-%m-%d_%H-%M')
        self.create_directory()

    def create_directory(self):
        if not os.path.isdir(self.path_files):
            os.mkdir(self.path_files)
        if not os.path.isdir(self.path_to_zip):
            os.mkdir(self.path_to_zip)

    async def dump_all(self, name):
        try:
            await self.dump_mongo()
        except Exception as e:
            await logg.get_error(e)
        try:
            await self.dump_postgres()
        except Exception as e:
            await logg.get_error(e)
        await self.zip(name)
        asyncio.create_task(self.delete_files())

    async def restore_all(self, name=None):
        print('start')
        if name is None:
            ValueError(await logg.get_error('Restore mongo: File for restore not found'))
        await self.unzip(name=name)
        file_list = os.listdir(self.path_files+self.path_files)
        if len([type_f for type_f in file_list if ".csv" in type_f]) != 0:
            await self.restore_postgres()
        if len([type_f for type_f in file_list if ".bson" in type_f]) != 0:
            await self.restore_mongo()

    async def restore_mongo(self):
        conn = all_data().get_mongo()
        db_name = self._db_name
        db = conn[db_name]
        # read zip_file
        for coll in os.listdir(self.path_files+self.path_files):
            if '.bson' in coll:
                print(coll.split('.')[0])
                with open(os.path.join(self.path_files+self.path_files, coll), 'rb+') as f:
                    try:
                        await db[coll.split('.')[0]].drop()
                        await db[coll.split('.')[0]].insert_many(bson.decode_all(f.read()))
                    except BulkWriteError as e:
                        print(e)
                        return
        print('restore_mongo DONE')
        return True

    async def dump_mongo(self):
        collections = await self.db.list_collection_names()
        for coll in collections:
            with open(os.path.join(self.path_files, f'{coll}.bson'), 'wb+') as file:
                async for doc in self.db[coll].find():
                    file.write(bson.BSON.encode(doc))
        return True

    async def dump_postgres(self):
        with get_cursor() as cur:
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            cur.execute(sql)
            tables = cur.fetchall()
            for table_name in tables:
                t_path_n_texts = self.path_files + f"{table_name[0]}.csv"
                SQL = f"COPY (SELECT * FROM {table_name[0]}) TO STDOUT WITH CSV HEADER"
                try:
                    with open(t_path_n_texts, 'w') as f_output:
                        cur.copy_expert(SQL, f_output)
                except Exception as e:
                    await logg.get_error(e)

    async def zip(self, name: str):
        with zipfile.ZipFile(self.path_to_zip + name + '.zip', 'w') as zip_file:
            file_list = os.listdir(self.path_files)
            for file in file_list:
                zip_file.write(self.path_files + file)
        print('saved successfully')

    async def unzip(self, name):
        with zipfile.ZipFile(self.path_to_zip+name, 'r') as zip_file:
            zip_file.extractall(self.path_files)

    async def delete_files(self):
        await asyncio.sleep(3)
        if os.path.isdir(self.path_files):
            shutil.rmtree(self.path_files)

    async def restore_postgres(self):
        with get_cursor() as cur:
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            cur.execute(sql)
            tables = cur.fetchall()
        con = all_data().get_postg()
        cur = con.cursor()
        con.autocommit = True
        main_tables = ['texts', 'assets']
        for table in tables:
            if table[0] not in main_tables:
                cur.execute("DROP TABLE IF EXISTS {}".format(table[0]))
                logg.get_info(f"Table {table[0]} has been deleted".upper())
        for table in main_tables:
            cur.execute("DROP TABLE IF EXISTS {}".format(table))
            logg.get_info(f"Table {table[0]} has been deleted".upper())

        # Создание таблиц
        cur.execute('''CREATE TABLE IF NOT EXISTS public.texts(
                            "text" TEXT NOT NULL,
                            "name" TEXT NOT NULL PRIMARY KEY
                            )''')
        logg.get_info("table text is created".upper())

        cur.execute('''CREATE TABLE IF NOT EXISTS public.assets(
                        "t_id" TEXT NOT NULL,
                        "name" TEXT NOT NULL PRIMARY KEY
                        )''')
        logg.get_info("table assets is created".upper())

        cur.execute('''create table public.truthgame
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
        logg.get_info("table Truthgame is created".upper())

        cur.execute('''CREATE TABLE public.mistakeorlie(
                                "id" int4 NULL,
                                asset_name varchar NULL,
                                belivers int4 NOT NULL,
                                nonbelivers int4 NOT NULL,
                                rebuttal varchar NULL,
                                text_name varchar NULL,
                                truth boolean NULL
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
        path_in = self.path_files+self.path_files
        for table in main_tables:
            try:
                csv_file_name = path_in + f'{table}.csv'
                sql = f"COPY {table} FROM STDIN DELIMITER ',' CSV HEADER"
                cur.copy_expert(sql, open(csv_file_name, "r"))
            except Exception as error:
                await logg.get_error(f"{error}", __file__)
        print(list(set(tables) - set(main_tables)))
        for table in list(set(tables) - set(main_tables)):
            try:
                csv_file_name = path_in + f'{table[0]}.csv'
                sql = f"COPY {table[0]} FROM STDIN DELIMITER ',' CSV HEADER"
                cur.copy_expert(sql, open(csv_file_name, "r"))
            except Exception as error:
                await logg.get_error(f"{error}", __file__)
        return True

