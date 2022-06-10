import psycopg2
from psycopg2 import Error
from psycopg2 import sql

try:
    # Подключение базе данных
    con = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1")

    cur = con.cursor()
    con.autocommit=True

    cur.execute("SELECT version();")

    record = cur.fetchone()
    print("Вы подключены к - ", record, "\n")

    cur.execute('''CREATE TABLE IF NOT EXISTS texts(
                text_tag = BIGINT,
                text = BIGINT
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS assets(
            asset_tag = BIGINT,
            asset_id = BIGINT
            )''')


    async def sql_add_text(text_tag, text):
        cur = con.cursor()
        cur.execute('INSERT INTO texts VALUES (%(text_tag)s, %(text)s', {'text_tag': text_tag, 'text': text})

    async def sql_read_text(text_tag):
        cur = con.cursor()
        cur.execute("SELECT * FROM texts WHERE text_tag = %(tag)s", {'tag': text_tag})
        return cur.fetchone()

    async def sql_add_asset(asset_tag, asset_id):
        cur = con.cursor()
        cur.execute('INSERT INTO assets VALUES (%(asset_tag)s, %(asset_id)s', {'asset_tag': asset_tag, 'asset_id': asset_id})


    async def sql_read_asset(asset_tag):
        cur = con.cursor()
        cur.execute("SELECT * FROM assets WHERE asset_tag = %(tag)s", {'tag': asset_tag})
        return cur.fetchone()


    async def sql_safe_update(table_name, data_dict, condition_dict):
        where = list(condition_dict.keys())[0]
        equals = condition_dict[where]
        sql_query = sql.SQL("UPDATE {} SET {} = {} WHERE {} = '{}';").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, data_dict)),
            sql.SQL(", ").join(map(sql.Placeholder, data_dict)),
            sql.Identifier(where),
            sql.Identifier(equals),
        )
        cur = con.cursor()
        cur.execute(sql_query, data_dict)
        return "Comlete"

except (Exception, Error) as error:
    print("[ERROR]", error)

















