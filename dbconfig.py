import pymysql
from dbinfo import user, password

def get_db_connection():
    connection = pymysql.connect(
        host='mysql',
        user=user,
        password=password,
        database='abarrotesWeb')

    return connection