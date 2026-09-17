from connections.conn_mysql import mysql_connection
from connections.conn_snowflake import snowflake_connection


BATCH_SIZE = 1000

def main():
    
    snowflake_conn = None
    snowflake_cursor  = None
    mysql_conn = None
    mysql_cursor = None
    
    try:
        # 1. Snowflake Connection
        
        print("Conneting to Snowflake")
        
        snowflake_conn = snowflake_connection()
        snowflake_cursor = snowflake_conn.cursor()
        
        print("Connected to Snowflake")

        # 2. Snowflake query
     
        snowflake_cursor.execute(
            """
            SELECT

                CASE
                    WHEN B."SIGLA_LOJA" = 'BRTJ-RJ' THEN 'AMRC-RJ'
                    ELSE B."SIGLA_LOJA"
                END AS "SIGLA_LOJA",
                
                C.COD_BARRAS,

                REPLACE(A."CHAVE_PRODUTO", '|', '') AS "CODIGO",
            

                C."PRODUTO",
                
                C."CATEGORIA_MODULAR",

                ROUND(A."VALOR_PERDA_ANO_ATU", 2) AS "VALOR_PERDA",

                FLOOR(A."QTDE_PERDA_ANO_ATU") AS "QTDE_PERDA",
                
                TO_DATE(A."CHAVE_DATA_BANCO"::VARCHAR, 'YYYYMMDD') AS CHAVE_DATA_BANCO

            FROM CENTRAL_DATA_REFINED.SUPPLY.FATO_PERDA A

            LEFT JOIN CENTRAL_DATA_REFINED.SALES.DIM_LOJA B
                ON TRIM(A."CHAVE_LOJA") = TRIM(B."CHAVE_LOJA")

            LEFT JOIN CENTRAL_DATA_REFINED.SUPPLY.DIM_PRODUTO C
                ON TRIM(A."CHAVE_PRODUTO") = TRIM(C."CHAVE_PRODUTO")

            WHERE
                
                YEAR(TO_DATE(A."CHAVE_DATA_BANCO", 'YYYYMMDD')) = YEAR(CURRENT_DATE())

                AND A."CHAVE_PERDA" <> '|50000'

                AND B."SIGLA_LOJA" <> 'CDEM-SP'

                AND A."CHAVE_PERDA" = '|70000';
            """
        )

        # 3. Loads Snowflake results
        
        snowflake_results = snowflake_cursor.fetchall()
        
        total_registers = len(snowflake_results)
        
        print(
            f"Registers obtained from Snowflake: {total_registers}"
        )
        
        # 4. Closes Snowflake
        
        snowflake_cursor.close()
        snowflake_cursor = None
        
        snowflake_conn.close()
        snowflake_conn = None
        
        print("Snowflake connection closed.")
        
        # 5. Maria DB connection
        
        print("Connectiong to Maria DB")
        
        mysql_conn = mysql_connection()
        mysql_cursor = mysql_conn.cursor()
        
        print("MariaDB Connected")
        
        # 6. Remove the actual year registers
        
        print(
            "Removing the registers"
        )
        
        mysql_cursor.execute(
            """
            TRUNCATE TABLE `dw_doacao`
            """
        )
        
        removed_registers = mysql_cursor.rowcount
        
        mysql_conn.commit()
        
        print(
            f"Removed registers: {removed_registers}"
        )
        
        # 7. SQL insert
        
        insert_sql = """
        insert into `dw_doacao` (
            `sigla_loja`
            ,`codbar`
            ,`codtotvs`
            ,`produto`
            ,`categoria_modular`
            ,`valor_perda`
            ,`quantidade`
            ,`data_perda`
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """
        # 8. Insert 
        
        batch = []
        total_inserted = 0
        
        
        for row in snowflake_results:
            
            batch.append((
                row[0], # sigla_loja
                row[1], # codbar
                row[2], # codtotvs
                row[3], # produto
                row[4], # categoria_modular
                row[5], # valor_perda
                row[6], # quantidade
                row[7], # data_perda
            ))
            
            # When reaches 1000
            if len(batch) == BATCH_SIZE:
                
                mysql_cursor.executemany(
                    insert_sql,
                    batch
                )
                
                mysql_conn.commit()
                
                total_inserted += len(batch)
                
                print(
                    f"Inserted rigister: "
                    f"`{total_inserted}/{total_registers}"
                )

                batch = []
                
        
        # 9. Insert the last batch
        
        if batch:
            
            mysql_cursor.executemany(
                insert_sql,
                batch
            )
            
            mysql_conn.commit()
            
            total_inserted += len(batch)
            
            print(
                f"Inserted registers:"
                f"{total_inserted}/{total_registers}"
            )
            
        # 10. ending
        
        print()
        print("=" * 10)
        print("ETL Completelly successfully!")
        print("=" * 10)
        print(f"Removed registers: {removed_registers}")
        print(f"Inserted registers: {total_inserted}")
        print("Table: dw_doacao")
        print("=" * 10)
        
    except Exception as e:
        print()
        print("=" * 10)
        print("Error during ETL")
        print("=" * 10)
        print(e)
        print("e" * 10)
        
        # If there is an open transation
        # Try to undo the pending changes
        if mysql_conn is not None:
            try:
                mysql_conn.rollback()
                print("Rollback realized at MariaDB.")
            except Exception as e:
                pass
            
        raise
    
    finally:
        
        # 11. Close the cursors and connections
        
        if snowflake_cursor is not None:
            try:
                snowflake_cursor.close()
            except Exception:
                pass
            
        if snowflake_conn is not None:
            try:
                snowflake_conn.close()
            except Exception:
                pass
            
        if mysql_cursor is not None:
            try:
                mysql_cursor.close()
            except Exception:
                pass
            
        if mysql_conn is not None:
            try:
                mysql_conn.close()
            except Exception:
                pass
            
        print("Connections closed.")    
        
            
            
if __name__ == "__main__":
    main()