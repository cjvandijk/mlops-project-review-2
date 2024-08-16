from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.hooks.postgres_hook import PostgresHook
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor   
from sklearn.metrics import mean_squared_error
import pandas as pd

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

dag = DAG(
    'etl_air_quality_postgres_training_pipeline',
    default_args=default_args,
    description='ETL + Train Pipeline with Air Quality Dataset using PostgreSQL',
    schedule_interval='@daily',
    max_active_runs=1
)

def create_table_if_not_exists():
    """
    Creates two PostgreSQL tables: air_quality_data and air_quality_data_transformed.
    If these tables exist, they will be dropped and recreated.

    The air_quality_data table is used for raw data storage, while the
    air_quality_data_transformed table is used to store the cleaned and transformed data.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    pg_hook = PostgresHook(postgres_conn_id='air_quality_airflow_conn')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    DROP TABLE IF EXISTS air_quality_data;
    CREATE TABLE air_quality_data (
        date DATE,
        time TIME,
        CO_GT FLOAT,
        PT08_S1_CO FLOAT,
        NMHC_GT FLOAT,
        C6H6_GT FLOAT,
        PT08_S2_NMHC FLOAT,
        NOx_GT FLOAT,
        PT08_S3_NOx FLOAT,
        NO2_GT FLOAT,
        PT08_S4_NO2 FLOAT,
        PT08_S5_O3 FLOAT,
        T FLOAT,
        RH FLOAT,
        AH FLOAT
    );
    DROP TABLE IF EXISTS air_quality_data_transformed;
    CREATE TABLE air_quality_data_transformed (
        timestamp BIGINT,
        CO_GT FLOAT,
        PT08_S1_CO FLOAT,
        NMHC_GT FLOAT,
        C6H6_GT FLOAT,
        PT08_S2_NMHC FLOAT,
        NOx_GT FLOAT,
        PT08_S3_NOx FLOAT,
        NO2_GT FLOAT,
        PT08_S4_NO2 FLOAT,
        PT08_S5_O3 FLOAT,
        T FLOAT,
        RH FLOAT,
        AH FLOAT
    );               
    """)

    conn.commit()
    cursor.close()
    conn.close()

def extract_data_to_postgres():
    """
    Extracts air quality data from a CSV file and loads it into a PostgreSQL table.

    The function performs the following steps:
    - Reads data from a specified CSV file.
    - Drops rows where the Date or Time is missing.
    - Converts the Date and Time columns to the appropriate datetime format.
    - Renames the columns to match the database schema.
    - Inserts the data into the air_quality_data table in PostgreSQL.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Load the Air Quality dataset
    df = pd.read_csv("https://raw.githubusercontent.com/babaksit/mlops-e2e/develop/data/raw/AirQualityUCI.csv",
                  delimiter=";", decimal=",", usecols=range(15) )
    df = df.dropna(subset=['Date', 'Time'])  # Drop rows where Date or Time is missing

    # Convert Date and Time columns to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.date
    df['Time'] = pd.to_datetime(df['Time'], format='%H.%M.%S').dt.time

    df.columns = ['date', 'time', 'CO_GT', 'PT08_S1_CO', 'NMHC_GT', 'C6H6_GT', 'PT08_S2_NMHC', 'NOx_GT',
                  'PT08_S3_NOx', 'NO2_GT', 'PT08_S4_NO2', 'PT08_S5_O3', 'T', 'RH', 'AH']

    # Insert data into PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='air_quality_airflow_conn')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    for row in df.itertuples(index=False, name=None):
        cursor.execute(
            """
            INSERT INTO air_quality_data (date, time, CO_GT, PT08_S1_CO, NMHC_GT, C6H6_GT, PT08_S2_NMHC, NOx_GT,
            PT08_S3_NOx, NO2_GT, PT08_S4_NO2, PT08_S5_O3, T, RH, AH)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, row
        )
    conn.commit()
    cursor.close()
    conn.close()


def transform():
    """
    Transforms the raw air quality data by cleaning it and creating a timestamp field.

    The function performs the following steps:
    - Fetches raw data from the air_quality_data table in PostgreSQL.
    - Replaces erroneous values (e.g., -200) with NaN and drops any rows containing NaN values.
    - Combines the Date and Time columns into a single timestamp column (in Unix time format).
    - Inserts the cleaned data into the air_quality_data_transformed table.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    pg_hook = PostgresHook(postgres_conn_id='air_quality_airflow_conn')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM air_quality_data")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)

    # Replace -200 values with NaN (as per dataset documentation)
    df.replace(-200, pd.NA, inplace=True) 
    df = df.dropna()   
    # Ensure date and time are strings before concatenation
    df['date'] = df['date'].astype(str)
    df['time'] = df['time'].astype(str)
    # Combine Date and Time into a single datetime and convert to Unix timestamp
    df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y-%m-%d %H:%M:%S').astype(int) // 10**9
    df = df.drop(columns=['date', 'time'])

    # Insert cleaned data into clean_table
    insert_query = """
        INSERT INTO air_quality_data_transformed (timestamp, CO_GT, PT08_S1_CO, NMHC_GT, C6H6_GT, PT08_S2_NMHC, NOx_GT,
            PT08_S3_NOx, NO2_GT, PT08_S4_NO2, PT08_S5_O3, T, RH, AH)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()


def train_model():
    """
    Trains a RandomForestRegressor model on the cleaned air quality data.

    The function performs the following steps:
    - Fetches the cleaned data from the air_quality_data_transformed table in PostgreSQL.
    - Separates the features and target variable (RH).
    - Splits the data into training and testing sets.
    - Trains a RandomForestRegressor model on the training data.
    - Evaluates the model using Mean Squared Error (MSE) on the test data.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    pg_hook = PostgresHook(postgres_conn_id='air_quality_airflow_conn')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM air_quality_data_transformed")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    
    # Separate features and target
    X = df.drop('rh', axis=1)
    y = df['rh']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)

    print(f"Model MSE: {mse}\n")
    
    cursor.close()
    conn.close()

create_table_task = PythonOperator(
    task_id='create_table_if_not_exists',
    python_callable=create_table_if_not_exists,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_to_postgres',
    python_callable=extract_data_to_postgres,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag,
)


train_task = PythonOperator(
    task_id='train',
    python_callable=train_model,
    dag=dag,
)

create_table_task >> extract_task >> transform_task >> train_task  
