import time
from datetime import datetime

import psycopg2
from flask import Flask, request
from werkzeug.utils import redirect

from connect_pool import get_cursor

app = Flask(__name__)


async def data_getter(query):
    try:
        with get_cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
        return data
    except psycopg2.Error as error:
        return error


# @app.before_request
# def before_request():
#     Flask.custom_profiler = {"start": time.time()}


@app.route("/asd")
async def index():
    utm_source = request.args.get('utm_source')
    date = datetime.now()
    just_date = str(date)[:10].strip()
    just_time = str(date)[10:].strip()
    ip = request.remote_addr

    await data_getter(
        f"insert into utm_table(utm_name,date,time,location) values('{utm_source}','{just_date}','{just_time}','{ip}');commit;")
    print(utm_source)
    print(date)
    print(just_date)
    print(just_time)
    print(ip)
    return redirect("https://t.me/Russia_Ukraine_Bot")



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
