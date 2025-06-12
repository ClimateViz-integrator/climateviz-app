import json
import numpy as np

class WeatherDataProcessor:
    def extract_weather_data(self, prediction_data):
        """
        Extrae datos de la predicción.
        Se asume que prediction_data es una lista de objetos ORM (por ejemplo, Forecast).
        Se calcula el promedio de todas las temperaturas y humedades de los registros en el campo 'hours' usando numpy.
        """
        not_available = "No disponible"
        result = {
            'temp_c': not_available,
            'humidity': not_available,
            'condition': not_available
        }
        
        try:
            if not self._is_valid_prediction_data(prediction_data):
                return result
                
            forecast_obj = prediction_data[0]
            hours = self._extract_hours_data(forecast_obj)
            
            if not hours:
                return result
                
            temps, humidities = self._extract_temperature_and_humidity_data(hours)
            self._calculate_averages(temps, humidities, result)
            
        except Exception as e:
            print(f"Error extrayendo datos del clima: {e}")
        
        return result

    def _is_valid_prediction_data(self, prediction_data):
        """Valida que los datos de predicción sean válidos."""
        return isinstance(prediction_data, list) and prediction_data

    def _extract_hours_data(self, forecast_obj):
        """Extrae y procesa los datos de horas del objeto forecast."""
        hours = forecast_obj.hours
        
        if isinstance(hours, str):
            try:
                hours = json.loads(hours)
            except json.JSONDecodeError as e:
                print(f"[LOG] Error parseando JSON de hours: {e}")
                return None
        
        return hours if isinstance(hours, list) and hours else None

    def _extract_temperature_and_humidity_data(self, hours):
        """Extrae datos de temperatura y humedad de las horas."""
        temps = []
        humidities = []
        
        for hour in hours:
            temp, humidity = self._extract_single_hour_data(hour)
            
            if temp is not None:
                temps.append(temp)
            if humidity is not None:
                humidities.append(humidity)
        
        return temps, humidities

    def _extract_single_hour_data(self, hour):
        """Extrae temperatura y humedad de una sola hora."""
        if isinstance(hour, dict):
            return self._extract_from_dict(hour)
        else:
            return self._extract_from_object(hour)

    def _extract_from_dict(self, hour_dict):
        """Extrae datos de temperatura y humedad de un diccionario."""
        temp = self._safe_float_conversion(hour_dict.get('temp_pred'), 'temp_pred')
        humidity = self._safe_float_conversion(hour_dict.get('humidity_pred'), 'humidity_pred')
        return temp, humidity

    def _extract_from_object(self, hour_obj):
        """Extrae datos de temperatura y humedad de un objeto."""
        temp_attr = getattr(hour_obj, 'temp_pred', None)
        humidity_attr = getattr(hour_obj, 'humidity_pred', None)
        
        temp = self._safe_float_conversion(temp_attr, 'temp_pred (object)')
        humidity = self._safe_float_conversion(humidity_attr, 'humidity_pred (object)')
        
        return temp, humidity

    def _safe_float_conversion(self, value, field_name):
        """Convierte un valor a float de forma segura."""
        if value is None:
            return None
            
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            print(f"[LOG] Error convirtiendo {field_name}: {e}")
            return None

    def _calculate_averages(self, temps, humidities, result):
        """Calcula los promedios de temperatura y humedad usando numpy."""
        if temps:
            avg_temp = np.mean(temps)
            result['temp_c'] = str(round(avg_temp, 1))
            
        if humidities:
            avg_humidity = np.mean(humidities)
            result['humidity'] = str(round(avg_humidity, 1))

    
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
