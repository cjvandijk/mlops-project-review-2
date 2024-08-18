from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd

postgres_conn_id = "postgres_air_quality"

def execute_sql(query):
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def fetch_data(query):
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame(data, columns=columns)

def insert_data(df, table_name):
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    for row in df.itertuples(index=False, name=None):
        placeholders = ", ".join(["%s"] * len(row))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.execute(query, row)
    conn.commit()
    cursor.close()
    conn.close()