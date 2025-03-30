
import pandas as pd
import pytz
import requests
import numpy as np
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env")

# Tu API Key de WeatherAPI
API_KEY = os.getenv("API_KEY")


def get_data(city: str):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=yes"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        datos_api = np.array(
            [
                [
                    data["location"]["lat"],
                    data["location"]["lon"],
                    data["current"]["wind_kph"],
                    data["current"]["wind_degree"],
                    data["current"]["pressure_mb"],
                    data["current"]["precip_mm"],
                    data["current"]["cloud"],
                    data["current"]["feelslike_c"],
                    data["current"]["vis_km"],
                    data["current"]["uv"],
                    data["current"]["humidity"],
                    data["current"]["air_quality"].get("co", np.nan),
                    data["current"]["air_quality"].get("o3", np.nan),
                    data["current"]["air_quality"].get("no2", np.nan),
                    data["current"]["air_quality"].get("so2", np.nan),
                    data["current"]["air_quality"].get("pm2_5", np.nan),
                    data["current"]["air_quality"].get("pm10", np.nan),
                    data["current"]["air_quality"].get("us-epa-index", np.nan),
                    data["current"]["air_quality"].get("gb-defra-index", np.nan),
                    # Obtenemos los demas valores
                    data["location"]["name"],  # 19
                    data["location"]["region"],
                    data["location"]["country"],
                    data["location"]["localtime"],
                    
                ]
            ]
        )
        return datos_api
    else:
        return None

def get_data_history(city: str, num_days: int):
    colombia_tz = pytz.timezone("America/Bogota")
    current_time = datetime.now(colombia_tz)
    current_hour = current_time.strftime("%H")
    
    all_data = []
    
    if num_days == 0:
        date = current_time.strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=yes"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            record = [
                data["location"]["lat"],
                data["location"]["lon"],
                data["current"]["wind_kph"],
                data["current"]["wind_degree"],
                data["current"]["pressure_mb"],
                data["current"]["precip_mm"],
                data["current"]["cloud"],
                data["current"]["feelslike_c"],
                data["current"]["vis_km"],
                data["current"]["uv"],
                data["current"]["humidity"],
            ]
            all_data.append(record)
    else:
        for i in range(num_days+1):
            date = (current_time - pd.DateOffset(days=i)).strftime("%Y-%m-%d")
            url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}&aqi=yes"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                forecast_data = data["forecast"]["forecastday"][0]["hour"]
                
                current_hour_data = [hour for hour in forecast_data if hour["time"][-5:-3] == current_hour]
                
                for hour in current_hour_data:
                    record = [
                        data["location"]["lat"],
                        data["location"]["lon"],
                        hour["wind_kph"],
                        hour["wind_degree"],
                        hour["pressure_mb"],
                        hour["precip_mm"],
                        hour["cloud"],
                        hour["feelslike_c"],
                        hour["vis_km"],
                        hour["uv"],
                        hour["humidity"],
                    ]
                    all_data.append(record)
    
    return np.array(all_data) if all_data else None
