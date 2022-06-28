import asyncio
import os
from datetime import datetime
import psycopg2
from aiogram.types import FSInputFile
from bata import all_data
import pandas
from aiogram import Router, F
from aiogram import types

from filters.isAdmin import IsSudo
from log import logg
from middleware import CounterMiddleware

router = Router()
router.message.middleware(CounterMiddleware())


@router.message(IsSudo(), F.text.contains('Экспорт'))
async def mongo_export_to_file(message: types.Message):
    today = datetime.today()
    today = today.strftime("%d-%m-%Y")
    client = all_data().get_mongo()
    database = client['database']
    collection = database['userinfo']
    # make an API call to the MongoDB server
    mongo_docs = collection.find()

    # Convert the mongo docs to a DataFrame
    docs = pandas.DataFrame(mongo_docs)

    # compute the output file directory and name
    output_dir_mongo = os.path.join('export_to_csv', 'backups', 'MongoDB')
    output_file = os.path.join(output_dir_mongo, 'Mongo_user-' + today + '.csv')

    docs.to_csv(output_file, ",", index=False)  # CSV delimited by commas

    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            SQL_texts = "COPY (SELECT * FROM texts) TO STDOUT WITH CSV HEADER"
            SQL_assets = "COPY (SELECT * FROM assets) TO STDOUT WITH CSV HEADER"
            SQL_mistakeorlie = "COPY (SELECT * FROM mistakeorlie) TO STDOUT WITH CSV HEADER"
            SQL_putin_lies = "COPY (SELECT * FROM putin_lies) TO STDOUT WITH CSV HEADER"
            SQL_putin_old_lies = "COPY (SELECT * FROM putin_old_lies) TO STDOUT WITH CSV HEADER"
            SQL_truthgame = "COPY (SELECT * FROM truthgame) TO STDOUT WITH CSV HEADER"
            SQL_ucraine_or_not_game = "COPY (SELECT * FROM ucraine_or_not_game) TO STDOUT WITH CSV HEADER"
            # Set up a variable to store our file path and name.
            t_path_n_texts = f"export_to_csv/backups/PostgreSQL/Texts-{today}.csv"
            t_path_n_assets = f"export_to_csv/backups/PostgreSQL/Assets-{today}.csv"
            t_path_n_mistakeorlie = f"export_to_csv/backups/games/Mistakeorlie-{today}.csv"
            t_path_n_putin_lies = f"export_to_csv/backups/games/Putin_lies-{today}.csv"
            t_path_n_putin_old_lies = f"export_to_csv/backups/games/Putin_old_lies-{today}.csv"
            t_path_n_truthgame = f"export_to_csv/backups/games/Truthgame-{today}.csv"
            t_path_n_ucraine_or_not_game = f"export_to_csv/backups/games/Ucraine_or_not_game-{today}.csv"
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
                with open(t_path_n_ucraine_or_not_game, 'w') as f_output:
                    cur.copy_expert(SQL_ucraine_or_not_game, f_output)
            except psycopg2.Error as er:
                await logg.get_error(er)

    await message.answer_document(FSInputFile(f"export_to_csv/backups/MongoDB/Mongo_user-{today}.csv"), caption="MongoDB info")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/PostgreSQL/Texts-{today}.csv"), caption="Texts")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/PostgreSQL/Assets-{today}.csv"), caption="Assets")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Mistakeorlie-{today}.csv"), caption="Mistakeorlie")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Putin_lies-{today}.csv"), caption="Putin_lies")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Putin_old_lies-{today}.csv"), caption="Putin_old_lies")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Stetements_expusures-{today}.csv"), caption="Stetements_expusures")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Truthgame-{today}.csv"), caption="Truthgame")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f"export_to_csv/backups/games/Ucraine_or_not_game-{today}.csv"), caption="Assets")
    await asyncio.sleep(0.2)
    await message.answer_document(FSInputFile(f'log/logs/Log-{today}.log'), caption="Logs")

