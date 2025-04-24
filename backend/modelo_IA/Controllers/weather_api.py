import requests
import pandas as pd
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv('.env')
# Cargar la variable de entorno desde el archivo .env

# API_KEY = "5a6375bbfb4f4df984d21001252802" #Ucaldas

API_KEY = os.getenv('API_KEY')

def get_data(city: str, days: int):
    tz = pytz.timezone("America/Bogota")
    date_current = datetime.now(tz).strftime("%Y-%m-%d")

    all_data = []

    if days == 0:
        # Obtener solo la fecha actual
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date_current}&aqi=yes"
        response = requests.get(url)
        if response.status_code == 200:
            all_data.append(response.json())
        else:
            print(f"Error en la solicitud para la fecha actual: {response.status_code}")
    else:
        for i in range(1, days+1):
            date = (pd.to_datetime(date_current) - pd.DateOffset(days=i)).strftime("%Y-%m-%d")
            url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}&aqi=yes"
            response = requests.get(url)
            if response.status_code == 200:
                all_data.append(response.json())
            else:
                print(f"Error en la solicitud para la fecha {date}: {response.status_code}")

    return all_data


def extract_hourly_data(json_data_list):
    registros = []
    for dia in json_data_list:
        horas = dia['forecast']['forecastday'][0]['hour']
        for h in horas:
            registro = {
                "datetime": h['time'],
                "pressure_mb": h['pressure_mb'],
                "temp_c": h['temp_c'],
                "dewpoint_c": h['dewpoint_c'],
                "humidity": h['humidity'],
                "wind_kph": (h['wind_kph'] * 1000)/3600,
                "wind_degree": h['wind_degree']
            }
            registros.append(registro)

    df = pd.DataFrame(registros)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index('datetime', inplace=True)
    return df

def extract_additional_info(json_data_list):
    """
    Extrae la información adicional contenida en la respuesta de la API.
    Se incluye la fecha para poder identificar cada bloque (forecastday).
    """
    additional_info = []
    for data in json_data_list:
        forecastday_info = data.get('forecast', {}).get('forecastday', [{}])[0]
        info = {
            "location": data.get("location", {}),
            "forecast_day": forecastday_info.get("day", {}),
            "astro": forecastday_info.get("astro", {}),
            "date": forecastday_info.get("date", "")
        }
        additional_info.append(info)
    return additional_info