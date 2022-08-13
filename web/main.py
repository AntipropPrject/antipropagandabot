from datetime import datetime

import psycopg2
import requests
from flask import Flask, request
from werkzeug.utils import redirect

app = Flask(__name__)


def get_postg():
    return psycopg2.connect(database="postgres", user="postgres", password="postgres", host="db",
                            port=5431)


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
    print(utm_source)
    print(date)
    print(just_date)
    print(just_time)
    print(ip)
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="db",
                                  port="5432",
                                  database="postgres")
    cursor = connection.cursor()
    try:
        response = requests.get(f"https://api.iplocation.net/?cmd=ip-country&ip={ip}")
        location = response.json()["country_name"]
        print(location)
        cursor.execute(
        f"insert into utm_table(utm_source,date,time,location) values('{utm_source}','{just_date}','{just_time}','{location}');commit;")
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)


    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        return redirect("https://t.me/Russia_Ukraine_Bot")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
