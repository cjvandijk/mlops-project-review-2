from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("http://10.100.181.117:80")
mlflow.set_experiment("iris_sklearn_experiment")


# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 12),
    'retries': 1,
}

# Instantiate the DAG
dag = DAG(
    'iris_scikit',
    default_args=default_args,
    description='iris sklearn',
    schedule_interval='@daily',
    max_active_runs=1 
)

def load_dataset():
    """Loads a dataset with ground truth and saves it to a file"""
    from sklearn.datasets import load_iris
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    df.to_csv('/tmp/iris_dataset.csv', index=False)

def preprocess_data():
    """Preprocess the data and save it to files"""
    df = pd.read_csv('/tmp/iris_dataset.csv')
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    X_train.to_csv('/tmp/X_train.csv', index=False)
    X_test.to_csv('/tmp/X_test.csv', index=False)
    y_train.to_csv('/tmp/y_train.csv', index=False)
    y_test.to_csv('/tmp/y_test.csv', index=False)

def train_model():
    """Train a RandomForest model using the preprocessed data and save the result"""
    X_train = pd.read_csv('/tmp/X_train.csv')
    X_test = pd.read_csv('/tmp/X_test.csv')
    y_train = pd.read_csv('/tmp/y_train.csv')
    y_test = pd.read_csv('/tmp/y_test.csv')

    # Start MLflow run
    with mlflow.start_run():
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train.values.ravel())
        y_pred = model.predict(X_test)

        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)

        # Log the model and metrics with MLflow
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "model")

        with open('/tmp/model_accuracy.txt', 'w') as f:
            f.write(str(accuracy))

def store_results():
    """Load and print the accuracy score"""
    with open('/tmp/model_accuracy.txt', 'r') as f:
        accuracy = f.read()
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
    dag=dag,
)

train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

store_results = PythonOperator(
    task_id='store_results',
    python_callable=store_results,
    dag=dag,
)

# Set task dependencies
load_data >> preprocess_data >> train_model >> store_results