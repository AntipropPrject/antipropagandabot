import os
from datetime import datetime
import psycopg2
from aiogram.types import FSInputFile
from bata import all_data
import pandas
from aiogram import Router
from aiogram import types
from log import logg
from middleware import CounterMiddleware

router = Router()
router.message.middleware(CounterMiddleware())


@router.message(commands=["export"])
async def mongo_export_to_file(message: types.Message):
    today = datetime.today()
    today = today.strftime("%m-%d-%Y")
    client = all_data().get_mongo()
    database = client['database']
    collection = database['userinfo']
    # make an API call to the MongoDB server
    mongo_docs = collection.find()

    # Convert the mongo docs to a DataFrame
    docs = pandas.DataFrame(mongo_docs)

    # compute the output file directory and name
    output_dir_mongo = os.path.join('export_to_csv', 'backups', 'MongoDB')
    output_file = os.path.join(output_dir_mongo, today +'.csv')

    docs.to_csv(output_file, ",", index=False)  # CSV delimited by commas

    conn = all_data().get_postg()
    with conn:
        with conn.cursor() as cur:
            SQL_texts = "COPY (SELECT * FROM texts) TO STDOUT WITH CSV HEADER"
            SQL_assets = "COPY (SELECT * FROM assets) TO STDOUT WITH CSV HEADER"
            # Set up a variable to store our file path and name.
            t_path_n_texts = f"export_to_csv/backups/PostgreSQL/{today}-texts.csv"
            t_path_n_assets = f"export_to_csv/backups/PostgreSQL/{today}-assets.csv"
            # Trap errors for opening the file
            try:
                with open(t_path_n_texts, 'w') as f_output:
                    cur.copy_expert(SQL_texts, f_output)
            except psycopg2.Error as er:
                logg.get_error(er)
            try:
                with open(t_path_n_assets, 'w') as f_output:
                    cur.copy_expert(SQL_assets, f_output)
            except psycopg2.Error as er:
                logg.get_error(er)

    await message.answer_document(FSInputFile(f"export_to_csv/backups/MongoDB/{today}.csv"), caption="MongoDB_info")
    await message.answer_document(FSInputFile(f"export_to_csv/backups/PostgreSQL/{today}-texts.csv"), caption="Texts")
    await message.answer_document(FSInputFile(f"export_to_csv/backups/PostgreSQL/{today}-assets.csv"), caption="Assets")