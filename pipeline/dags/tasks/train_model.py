from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.sklearn
from utils.db_utils import fetch_data

def train_model():
    mlflow.set_tracking_uri("http://mlflow-release-tracking.default.svc.cluster.local:80")
    mlflow.set_experiment("air_quality_experiment")

    df = fetch_data("SELECT * FROM air_quality_data_transformed")
    X = df.drop('rh', axis=1)
    y = df['rh']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    with mlflow.start_run():
        model = RandomForestRegressor()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_metric("mse", mse)
        mlflow.sklearn.log_model(model, "model", pip_requirements=["scikit-learn==1.5.1"])
