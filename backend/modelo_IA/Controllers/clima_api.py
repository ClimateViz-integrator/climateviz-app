import requests
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv('.env')

# Tu API Key de WeatherAPI
API_KEY = os.getenv('API_KEY')

def get_data(city:str):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=yes"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        datos_api = np.array([[
        data['location']['lat'],
        data['location']['lon'],
        data['current']['wind_kph'],
        data['current']['wind_degree'],
        data['current']['pressure_mb'],
        data['current']['precip_mm'],
        data['current']['humidity'],
        data['current']['cloud'],
        data['current']['feelslike_c'],
        data['current']['vis_km'],
        data['current']['uv'],
        data['current']['air_quality'].get('co', np.nan),
        data['current']['air_quality'].get('o3', np.nan),
        data['current']['air_quality'].get('no2', np.nan),
        data['current']['air_quality'].get('so2', np.nan),
        data['current']['air_quality'].get('pm2_5', np.nan),
        data['current']['air_quality'].get('pm10', np.nan),
        data['current']['air_quality'].get('us-epa-index', np.nan),
        data['current']['air_quality'].get('gb-defra-index', np.nan),

        # Obtenemos los demas valores
        data['location']['name'], # 19
        data['location']['region'],
        data['location']['country'],
        data['location']['localtime'],

        ]])
        return datos_api
    else:
        return None


