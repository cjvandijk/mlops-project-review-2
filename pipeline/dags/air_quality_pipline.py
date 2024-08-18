from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from tasks.db_handler import create_tables_if_not_exists
from tasks.extract_data import extract_data_to_postgres
from tasks.transform_data import transform_data
from tasks.train_model import train_model

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

dag = DAG(
    'air_quality_postgres_pipeline',
    default_args=default_args,
    description='ETL + Train Pipeline with Air Quality Dataset using PostgreSQL',
    schedule_interval='@daily',
    max_active_runs=1
)

db_handler_op = PythonOperator(
    task_id='create_tables_if_not_exists',
    python_callable=create_tables_if_not_exists,
    dag=dag,
)

extract_task_op = PythonOperator(
    task_id='extract',
    python_callable=extract_data_to_postgres,
    dag=dag,
)

transform_task_op = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag,
)

train_task_op = PythonOperator(
    task_id='train',
    python_callable=train_model,
    dag=dag,
)

db_handler_op >> extract_task_op >> transform_task_op >> train_task_op