import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


# MySQL connection
def mysql_connection():
    """
    Create and return a MySQL database connection.

    This function loads the database credentials from environment variables
    and establishes a connection to MySQL. After connecting, it executes a
    test query to retrieve the MySQL server version and verify that the
    connection was established successfully.

    Returns:
        mysql.connector.connection.MySQLConnection | None:
            An active MySQL connection object if the connection succeeds;
            otherwise, None.

    Environment Variables:
        DB2_HOST (str):
            MySQL server host or IP address.

        DB2_USER (str):
            Username used to authenticate with MySQL.

        DB2_PASSWORD (str):
            Password used to authenticate with MySQL.

        DB2_DATABASE (str):
            Name of the MySQL database to connect to.

    Example:
        >>> conn = mysql_connection()
        >>> if conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM table")
        ...     results = cursor.fetchall()
        ...     cursor.close()
        ...     conn.close()

    Notes:
        - Environment variables are loaded from the `.env` file.
        - The function executes `SELECT VERSION()` to test the connection.
        - The test cursor is closed before returning the connection.
        - The returned connection should be closed with `conn.close()` after use.
        - Connection errors are handled internally and result in None being
          returned.
    """

    try:
        # Create the MySQL connection
        mysql_conn = mysql.connector.connect(
            host=os.getenv("DB2_HOST"),
            user=os.getenv("DB2_USER"),
            password=os.getenv("DB2_PASSWORD"),
            database=os.getenv("DB2_DATABASE")
        )

        # Create a cursor to execute SQL statements
        mysql_cursor = mysql_conn.cursor()

        # Test the connection by retrieving the MySQL server version
        mysql_cursor.execute("SELECT VERSION()")
        mysql_result = mysql_cursor.fetchone()

        print("Connected!")
        print(f"MySQL version: {mysql_result[0]}")

        # Close the test cursor
        mysql_cursor.close()

        # Return the active MySQL connection
        return mysql_conn

    except Exception as e:
        print("MySQL connection error!")
        print(e)

        return None