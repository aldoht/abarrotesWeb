import pymysql
from dbinfo import user, password
import os

def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv('DATABASE_HOST', 'mysql'),  # Use the service name 'mysql'
        user=user,
        password=password,
        database='abarrotesWeb',
        port=3306
    )
    return connection