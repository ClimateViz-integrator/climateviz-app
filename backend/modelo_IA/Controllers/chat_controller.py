from fastapi import HTTPException
import os
from pathlib import Path
import csv
import re
import string
from datetime import datetime
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
import google.generativeai as genai
from dotenv import load_dotenv
from config.db import get_db
import unicodedata
import json  # Para manejar JSON

# Cargar variables de entorno
load_dotenv('.env')

# Configurar la API de Google Generative AI
genai.configure(api_key=os.getenv('API_KEY_G'))


class WeatherBot:
    def __init__(self):
        # Rutas de archivos usando pathlib para mejor portabilidad
        self.base_dir = Path(__file__).parent
        self.cities_file = self.base_dir / ".." / "Data" / "cities.txt"
        # Cargar recursos
        self.nlp = spacy.load("es_core_news_sm")
        self.cities = self._load_cities()
        self.matcher = self._setup_phrase_matcher()
        
        # Mapeo de términos a días
        self.day_terms = {
            "hoy": 1, "el día de hoy": 1, "ahora": 1, "actual": 1,
            "mañana": 2, "el día siguiente": 2, "el día de mañana": 2,
            "pasado mañana": 3, "en dos días": 3,
            "en tres días": 3, "en 3 días": 3,
            "en cuatro días": 4, "en 4 días": 4,
            "en cinco días": 5, "en 5 días": 5,
            "en seis días": 6, "en 6 días": 6,
            "en siete días": 7, "en 7 días": 7, "en una semana": 7,
            "próxima semana": 7, "semana que viene": 7
        }
        
        # Palabras clave para clima
        self.weather_keywords = [
            "clima", "tiempo", "temperatura", "lluvia", "pronóstico", 
            "meteorológico", "va a llover", "va a hacer sol", "va a hacer calor",
            "va a hacer frío", "condiciones climáticas", "previsión"
        ]
        
        # Configurar el modelo de Google Generative AI
        self.gen_model = genai.GenerativeModel("gemini-1.5-flash")
    
    def _load_cities(self):
        cities = set()
        try:
            with open(self.cities_file, "r", encoding="utf-8-sig") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # Saltar encabezado
                for row in reader:
                    if len(row) >= 2:
                        # Normalizar texto (quitar acentos y convertir a minúsculas)
                        city_name = self._normalize_text(row[1].strip())
                        cities.add(city_name)
        except Exception as e:
            print(f"Error loading cities: {e}")
        return cities
    
    def _setup_phrase_matcher(self):
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp(city) for city in self.cities]
        matcher.add("CITIES", patterns)
        return matcher
    
    def _normalize_text(self, text):
        """Normaliza el texto quitando acentos y pasando a minúsculas"""
        text = text.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')
    
    def _extract_city(self, text):
        # Primero normalizar el texto
        normalized_text = self._normalize_text(text)
        doc = self.nlp(text)
        matches = self.matcher(doc)

        if matches:
            matches.sort(key=lambda x: len(doc[x[1]:x[2]]), reverse=True)
            match_id, start, end = matches[0]
            matched_city = doc[start:end].text.lower()
            if matched_city in self.cities:
                return matched_city

        # Método 2: (opcional) NO hacer coincidencias parciales para evitar errores
        return None  # No se detectó ciudad explícita

    
    def _extract_days(self, text):
        for term, days in self.day_terms.items():
            if term in text:
                return days
        patterns = [
            r'(\d+)\s*d[ií]as?',
            r'pr[oó]ximos?\s*(\d+)\s*d[ií]as?',
            r'siguientes?\s*(\d+)\s*d[ií]as?',
            r'(\d+)\s*d[ií]as?\s*siguientes?',
            r'en\s*(\d+)\s*d[ií]as?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    continue
        match = re.search(r'\b(\d+)\b', text)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 14:
                return num
        return 0  # Valor predeterminado: hoy
    
    def _has_weather_intent(self, text):
        normalized_text = self._normalize_text(text)
        for keyword in self.weather_keywords:
            if keyword in normalized_text:
                return True
        weather_patterns = [
            r'c[oó]mo est[aá](?:r[aá])?(?:\s+el)?\s+(?:clima|tiempo)',
            r'qu[eé] (?:clima|tiempo) (?:hace|har[aá])',
            r'va (?:a|ha) (?:llover|nevar|hacer\s+(?:fr[ií]o|calor))',
            r'est[aá](?:r[aá])?\s+(?:lloviendo|nevando)',
            r'hay\s+(?:lluvia|sol|nieve|tormenta)'
        ]
        for pattern in weather_patterns:
            if re.search(pattern, normalized_text):
                return True
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "LOC" and self._extract_city(ent.text):
                if re.search(r'\b\d+\b', text):
                    return True
        return False
    
    def _get_time_of_day(self):
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "mañana"
        elif 12 <= hour < 18:
            return "tarde"
        elif 18 <= hour < 22:
            return "noche"
        else:
            return "madrugada"
    
    def _extract_weather_data(self, prediction_data):
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


    
    def _interpret_weather(self, temp, humidity):
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
    
    def generate_response(self, prompt):
        try:
            response = self.gen_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    async def process_message(self, message, controller):
        """
        Procesa el mensaje del usuario:
         - Extrae ciudad y días.
         - Llama al modelo para obtener la predicción (usando la función prediction_weather_future, la cual invoca internamente predict_from_api).
         - Extrae datos del pronóstico recién generado.
         - Genera una respuesta usando Generative AI.
        """
        original_message = message
        message_lower = message.lower()
        message_clean = message_lower.translate(str.maketrans("", "", string.punctuation))
        
        has_weather_intent = self._has_weather_intent(message_clean)
        city = self._extract_city(message_clean)
        days = self._extract_days(message_clean)
        
        print(f"Mensaje: '{original_message}'")
        print(f"Intent clima: {has_weather_intent}, Ciudad: {city}, Días: {days}")
        
        if has_weather_intent:
            if city is None:
                return {"response": "¿Para qué ciudad quieres saber el clima? No pude identificar la ciudad en tu mensaje."}
            if days in (0, None):
                return {"response": f"¿Cuántos días quieres saber el clima? No pude identificar los días en tu mensaje."}
            
            # Si todo está bien, proceder con la predicción
            try:
                db = next(get_db())
                prediction, _ = await controller.predict_from_api(city, days, db)
                
                weather_data = self._extract_weather_data(prediction)
                if weather_data['condition'] == 'No disponible':
                    weather_data['condition'] = self._interpret_weather(
                        weather_data['temp_c'], 
                        weather_data['humidity']
                    )
                
                if days == 1:
                    day_text = "hoy"
                elif days == 2:
                    day_text = "mañana"
                elif days == 3:
                    day_text = "pasado mañana"
                else:
                    day_text = f"los próximos {days} días"

                weather_report = (
                    f"Para {day_text} en {city.capitalize()}, la temperatura será de {weather_data['temp_c']}°C "
                    f"y la humedad es {weather_data['humidity']}. "
                )
                if weather_data['condition'] != 'No disponible':
                    weather_report += f"Se espera un clima {weather_data['condition']}."
                else:
                    weather_report += "."

                db.close()
                time_of_day = self._get_time_of_day()
                prompt = (
                    f"Imagina que eres un experto meteorológico y genera una respuesta cálida, amigable y breve para un usuario "
                    f"que consulta el clima en {city.capitalize()} para {days} días. Es actualmente {time_of_day}. Usa emojis y frases naturales. "
                    f"El pronóstico es:\n{weather_report}\n"
                    f"Genera una respuesta en español que mencione la temperatura de {weather_data['temp_c']}°C y la humedad de {weather_data['humidity']}%."
                )
                response = self.generate_response(prompt)
                return {"response": response}
            except Exception as e:
                print(f"Error en process_message: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error obteniendo la predicción: {str(e)}")

        # No hay intención de clima
        return {"response": "No entendí bien la pregunta. Por ejemplo, pregunta: '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'"}

