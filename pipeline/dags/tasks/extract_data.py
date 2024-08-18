import pandas as pd
from utils.db_utils import insert_data

def extract_data_to_postgres():
    df = pd.read_csv("https://raw.githubusercontent.com/babaksit/mlops-e2e/develop/data/raw/AirQualityUCI.csv",
                     delimiter=";", decimal=",", usecols=range(15))
    df = df.dropna(subset=['Date', 'Time'])
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.date
    df['Time'] = pd.to_datetime(df['Time'], format='%H.%M.%S').dt.time

    df.columns = ['date', 'time', 'CO_GT', 'PT08_S1_CO', 'NMHC_GT', 'C6H6_GT', 'PT08_S2_NMHC', 'NOx_GT',
                  'PT08_S3_NOx', 'NO2_GT', 'PT08_S4_NO2', 'PT08_S5_O3', 'T', 'RH', 'AH']

    insert_data(df, 'air_quality_data')
