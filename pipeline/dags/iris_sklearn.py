from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 13),
    'retries': 1,
}

# Instantiate the DAG
dag = DAG(
    'iris_scikit_learn',
    default_args=default_args,
    description='A simple DAG to train a model using scikit-learn',
    schedule_interval='@daily',
)


def load_dataset():
    """Loads a dataset with ground truth"""
    # Example using a built-in dataset from scikit-learn
    from sklearn.datasets import load_iris
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    return df


def preprocess_data(**kwargs):
    """Preprocess the data"""
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='load_data')
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    return X_train, X_test, y_train, y_test


def train_model(**kwargs):
    """Train a RandomForest model"""
    ti = kwargs['ti']
    X_train, X_test, y_train, y_test = ti.xcom_pull(task_ids='preprocess_data')

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy


def store_results(**kwargs):
    """Store the accuracy score"""
    ti = kwargs['ti']
    accuracy = ti.xcom_pull(task_ids='train_model')
    print(f"Model accuracy: {accuracy}")


# Define the tasks
load_data = PythonOperator(
    task_id='load_data',
    python_callable=load_dataset,
    dag=dag,
)

preprocess_data = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

store_results = PythonOperator(
    task_id='store_results',
    python_callable=store_results,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
load_data >> preprocess_data >> train_model >> store_results
