import pandas as pd
from utils.db_utils import fetch_data, insert_data

def transform_data():
    df = fetch_data("SELECT * FROM air_quality_data")
    df.replace(-200, pd.NA, inplace=True)
    df = df.dropna()
    df['date'] = df['date'].astype(str)
    df['time'] = df['time'].astype(str)
    df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time']).astype(int) // 10**9
    df = df.drop(columns=['date', 'time'])

    insert_data(df, 'air_quality_data_transformed')
