import pandas as pd

from connections.conn_mysql import mysql_connection
from dashboard.queries import DONATION_QUERY

def get_donation_data():
    conn = mysql_connection()
    
    try:
        df = pd.read_sql(DONATION_QUERY, conn)
        return df

    except Exception as e:
        print(e)
        
    finally:
        conn.close()    