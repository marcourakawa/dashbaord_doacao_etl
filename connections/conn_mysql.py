import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def mysql_connection(
    host=None,
    user=None,
    password=None,
    database=None,
):
    """
    Create and return a MySQL database connection.

    Credentials can be passed directly or loaded from environment
    variables for local development and ETL execution.
    """

    try:
        host = host or os.getenv("DB2_HOST")
        user = user or os.getenv("DB2_USER")
        password = password or os.getenv("DB2_PASSWORD")
        database = database or os.getenv("DB2_DATABASE")

        mysql_conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )

        mysql_cursor = mysql_conn.cursor()

        mysql_cursor.execute("SELECT VERSION()")
        mysql_result = mysql_cursor.fetchone()

        print("Connected!")
        print(f"MySQL version: {mysql_result[0]}")

        mysql_cursor.close()

        return mysql_conn

    except Exception as e:
        print("MySQL connection error!")
        print(e)

        return None