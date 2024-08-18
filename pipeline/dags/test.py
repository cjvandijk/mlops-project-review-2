import requests
import pandas as pd
url = 'https://github.com/asharvi1/UCI-Air-Quality-Data/blob/b2f7177dec8e2131df77f45c7726678afe46cf1c/AirQualityUCI.csv'
r = requests.get(url)

with open('/tmp/AirQualityUCI.csv', 'wb') as file:
    file.write(r.content)

# Load the Air Quality dataset
df = pd.read_csv('/home/bsi/Downloads/AirQualityUCI.csv', sep=';', decimal=',')  # Adjust the path accordingly
df = df.dropna(subset=['Date', 'Time'])  # Drop rows where Date or Time is missing