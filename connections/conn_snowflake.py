import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()


# Snowflake connection
def snowflake_connection():
    """
    Create and return a Snowflake database connection.

    This function loads Snowflake credentials and connection parameters from
    environment variables and establishes a connection to Snowflake. After
    connecting, it executes a test query to retrieve the Snowflake server
    version and verify that the connection was established successfully.

    Returns:
        snowflake.connector.connection.SnowflakeConnection | None:
            An active Snowflake connection object if the connection succeeds;
            otherwise, None.

    Environment Variables:
        DB1_USER (str):
            Snowflake username.

        DB1_AUTHENTICATOR (str):
            Authentication method used to connect to Snowflake.
            Examples: 'snowflake', 'externalbrowser', or 'oauth'.

        DB1_ACCOUNT (str):
            Snowflake account identifier.
            Example: 'xy12345.us-east-1'.

        DB1_ROLE (str):
            Snowflake role used for the connection.

        DB1_WAREHOUSE (str):
            Snowflake warehouse used to execute queries.

        DB1_DATABASE (str):
            Default Snowflake database.

        DB1_SCHEMA (str):
            Default Snowflake schema.

    Example:
        >>> conn = snowflake_connection()
        >>> if conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT CURRENT_VERSION()")
        ...     result = cursor.fetchone()
        ...     cursor.close()
        ...     conn.close()

    Notes:
        - Environment variables are loaded from the `.env` file.
        - The function executes `SELECT CURRENT_VERSION()` to test the
          connection.
        - The test cursor is closed before returning the connection.
        - The returned connection should be closed with `conn.close()`
          after use.
        - Connection errors are handled internally and result in None
          being returned.
    """

    try:
        # Create the Snowflake connection
        snowflake_conn = snowflake.connector.connect(
            user=os.getenv("DB1_USER"),
            authenticator=os.getenv("DB1_AUTHENTICATOR"),
            account=os.getenv("DB1_ACCOUNT"),
            role=os.getenv("DB1_ROLE"),
            warehouse=os.getenv("DB1_WAREHOUSE"),
            database=os.getenv("DB1_DATABASE"),
            schema=os.getenv("DB1_SCHEMA")
        )

        # Create a cursor to execute SQL statements
        snowflake_cursor = snowflake_conn.cursor()

        # Test the connection by retrieving the Snowflake version
        snowflake_cursor.execute("SELECT CURRENT_VERSION()")
        snowflake_result = snowflake_cursor.fetchone()

        print("Connected!")
        print(f"Snowflake version: {snowflake_result[0]}")

        # Close the test cursor
        snowflake_cursor.close()

        # Return the active Snowflake connection
        return snowflake_conn

    except Exception as e:
        print("Snowflake connection error!")
        print(e)

        return None