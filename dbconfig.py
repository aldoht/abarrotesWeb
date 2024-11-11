import pymysql
from dbinfo import user, password

def get_db_connection():
    try:
        connection = pymysql.connect(
        host='localhost',
        user=user,
        password=password,
        database='abarrotesWeb'
    )
    except pymysql.Error as e:
        print(f'ERROR: {e}')
        return None

    return connection