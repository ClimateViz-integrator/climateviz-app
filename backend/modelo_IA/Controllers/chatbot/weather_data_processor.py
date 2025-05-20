import json
import numpy as np

class WeatherDataProcessor:
    def extract_weather_data(self, prediction_data):
        """
        Extrae datos de la predicción.
        Se asume que prediction_data es una lista de objetos ORM (por ejemplo, Forecast).
        Se calcula el promedio de todas las temperaturas y humedades de los registros en el campo 'hours' usando numpy.
        """
        result = {
            'temp_c': 'No disponible',
            'humidity': 'No disponible',
            'condition': 'No disponible'
        }
        
        try:
            if isinstance(prediction_data, list) and prediction_data:
                forecast_obj = prediction_data[0]
                # Se asume que el campo 'hours' puede ser un JSON guardado como cadena o directamente una lista
                hours = forecast_obj.hours
                if isinstance(hours, str):
                    hours = json.loads(hours)
                
                if isinstance(hours, list) and hours:
                    temps = []
                    humidities = []
                    
                    for hour in hours:
                        # Si es un diccionario
                        if isinstance(hour, dict):
                            if 'temp_pred' in hour:
                                try:
                                    temps.append(float(hour['temp_pred']))
                                except Exception as e:
                                    print(f"[LOG] Error convirtiendo temp_pred: {e}")
                            if 'humidity_pred' in hour:
                                try:
                                    humidities.append(float(hour['humidity_pred']))
                                except Exception as e:
                                    print(f"[LOG] Error convirtiendo humidity: {e}")
                        else:
                            # Si es un objeto, se accede mediante getattr
                            temp = getattr(hour, 'temp_pred', None)
                            if temp is not None:
                                try:
                                    temps.append(float(temp))
                                except Exception as e:
                                    print(f"[LOG] Error accediendo a temp_pred: {e}")
                            h = getattr(hour, 'humidity_pred', None)
                            if h is not None:
                                try:
                                    humidities.append(float(h))
                                except Exception as e:
                                    print(f"[LOG] Error accediendo a humidity: {e}")
                    
                    # Calcular el promedio usando numpy, si se tienen datos
                    if temps:
                        avg_temp = np.mean(temps)
                        result['temp_c'] = str(round(avg_temp, 1))
                    if humidities:
                        avg_humidity = np.mean(humidities)
                        result['humidity'] = str(round(avg_humidity, 1))
        except Exception as e:
            print(f"Error extrayendo datos del clima: {e}")
        
        return result
    
    def interpret_weather(self, temp, humidity):
        condition = ""
        try:
            temp_float = float(temp)
            humidity_float = float(humidity)
            
            if temp_float < 10:
                condition = "frío"
            elif 10 <= temp_float < 20:
                condition = "templado"
            elif 20 <= temp_float < 30:
                condition = "cálido"
            else:
                condition = "caluroso"
            
            if humidity_float < 30:
                condition += " y seco"
            elif 30 <= humidity_float < 60:
                condition += " con humedad moderada"
            else:
                condition += " y húmedo"
        except (ValueError, TypeError):
            condition = "variable"
        
        return condition
