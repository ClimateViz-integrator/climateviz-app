from fastapi import HTTPException
import os
from pathlib import Path
import csv
import re
import string
from datetime import datetime
import spacy
from spacy.matcher import PhraseMatcher
import google.generativeai as genai
from dotenv import load_dotenv
from config.db import get_db
import unicodedata
import pandas as pd
import numpy as np

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
            "hoy": 0, "el día de hoy": 0, "ahora": 0, "actual": 0,
            "mañana": 1, "el día siguiente": 1, "el día de mañana": 1,
            "pasado mañana": 2, "en dos días": 2,
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
        
        # Generative AI model
        self.gen_model = genai.GenerativeModel("gemini-1.5-flash")
    
    def _load_cities(self):
        cities = set()
        try:
            with open(self.cities_file, "r", encoding="utf-8-sig") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # Skip header
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
        
        # Método 1: Usar el matcher de spaCy
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        if matches:
            # Tomar la coincidencia más larga
            matches.sort(key=lambda x: len(x[1:]), reverse=True)
            match_id, start, end = matches[0]
            return doc[start:end].text.lower()
        
        # Método 2: Buscar coincidencias directas
        words = normalized_text.split()
        for i in range(len(words)):
            for j in range(len(words), i, -1):  # Empezar con frases más largas
                candidate = " ".join(words[i:j])
                if candidate in self.cities:
                    return candidate
        
        # Método 3: Buscar coincidencias parciales (para ciudades con nombres compuestos)
        for city in self.cities:
            if city in normalized_text:
                return city
        
        return None
    
    def _extract_days(self, text):
        # Check for specific day terms
        for term, days in self.day_terms.items():
            if term in text:
                return days
        
        # Check for numeric days with context
        patterns = [
            r'(\d+)\s*d[ií]as?',  # 3 días, 5 dia
            r'pr[oó]ximos?\s*(\d+)\s*d[ií]as?',  # próximos 3 días
            r'siguientes?\s*(\d+)\s*d[ií]as?',  # siguientes 3 días
            r'(\d+)\s*d[ií]as?\s*siguientes?',  # 3 días siguientes
            r'en\s*(\d+)\s*d[ií]as?'  # en 3 días
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    continue
        
        # Si no encuentra coincidencias específicas, buscar cualquier número
        match = re.search(r'\b(\d+)\b', text)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 14:  # Límite razonable para días de pronóstico
                return num
        
        # Valor predeterminado si no se encuentra nada
        return 0  # Hoy por defecto
    
    def _has_weather_intent(self, text):
        """Determina si el mensaje está relacionado con el clima"""
        normalized_text = self._normalize_text(text)
        
        # Verificar palabras clave de clima
        for keyword in self.weather_keywords:
            if keyword in normalized_text:
                return True
        
        # Verificar patrones comunes de preguntas sobre el clima
        weather_patterns = [
            r'c[oó]mo est[aá](?:r[aá])?(?:\s+el)?\s+(?:clima|tiempo)',  # cómo está/estará el clima/tiempo
            r'qu[eé] (?:clima|tiempo) (?:hace|har[aá])',  # qué clima/tiempo hace/hará
            r'va (?:a|ha) (?:llover|nevar|hacer\s+(?:fr[ií]o|calor))',  # va a llover/nevar/hacer frío/calor
            r'est[aá](?:r[aá])?\s+(?:lloviendo|nevando)',  # está/estará lloviendo/nevando
            r'hay\s+(?:lluvia|sol|nieve|tormenta)'  # hay lluvia/sol/nieve/tormenta
        ]
        
        for pattern in weather_patterns:
            if re.search(pattern, normalized_text):
                return True
        
        # Verificar si hay entidades de clima en el texto
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "LOC" and self._extract_city(ent.text):
                # Si hay una ubicación que coincide con nuestras ciudades y
                # hay un número que podría ser días, probablemente es una pregunta de clima
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
        """Extrae datos del clima de la predicción que devuelve prediction_weather_future"""
        result = {
            'temp_c': 'No disponible',
            'humidity': 'No disponible',
            'condition': 'No disponible'
        }
        
        try:
            # Registrar para depuración
            print(f"Tipo de datos de predicción: {type(prediction_data)}")
            
            # Si es un DataFrame o tiene una forma similar a un DataFrame
            if hasattr(prediction_data, 'iloc') and hasattr(prediction_data, 'columns'):
                # Tomamos el primer registro
                if len(prediction_data) > 0:
                    # Verificar columnas disponibles
                    if 'temp_c' in prediction_data.columns:
                        result['temp_c'] = round(float(prediction_data.iloc[0]['temp_c']), 1)
                    if 'humidity' in prediction_data.columns:
                        result['humidity'] = round(float(prediction_data.iloc[0]['humidity']), 1)
            
            # Si es una lista
            elif isinstance(prediction_data, list) and len(prediction_data) > 0:
                first_item = prediction_data[0]
                
                # Si el primer elemento es un DataFrame
                if hasattr(first_item, 'iloc') and hasattr(first_item, 'columns'):
                    if len(first_item) > 0:
                        if 'temp_c' in first_item.columns:
                            result['temp_c'] = round(float(first_item.iloc[0]['temp_c']), 1)
                        if 'humidity' in first_item.columns:
                            result['humidity'] = round(float(first_item.iloc[0]['humidity']), 1)
                
                # Si es un diccionario
                elif isinstance(first_item, dict):
                    result['temp_c'] = round(float(first_item.get('temp_c', result['temp_c'])), 1)
                    result['humidity'] = round(float(first_item.get('humidity', result['humidity'])), 1)
                    result['condition'] = first_item.get('condition', result['condition'])
            
            # Si directamente es un diccionario
            elif isinstance(prediction_data, dict):
                result['temp_c'] = round(float(prediction_data.get('temp_c', result['temp_c'])), 1)
                result['humidity'] = round(float(prediction_data.get('humidity', result['humidity'])), 1)
                result['condition'] = prediction_data.get('condition', result['condition'])
            
            # Asegurarse de que los valores son cadenas de texto
            for key in result:
                if result[key] is not None:
                    result[key] = str(result[key])
                else:
                    result[key] = 'No disponible'
                    
        except Exception as e:
            print(f"Error extrayendo datos del clima: {e}")
        
        return result
    
    def _interpret_weather(self, temp, humidity):
        """Interpreta la temperatura y humedad para dar una descripción del clima"""
        condition = ""
        
        try:
            temp_float = float(temp)
            humidity_float = float(humidity)
            
            # Interpretación de temperatura
            if temp_float < 10:
                condition = "frío"
            elif 10 <= temp_float < 20:
                condition = "templado"
            elif 20 <= temp_float < 30:
                condition = "cálido"
            else:
                condition = "caluroso"
            
            # Añadir información sobre humedad
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
    
    async def process_message(self, message, model):
        original_message = message
        message = message.lower()
        message_clean = message.translate(str.maketrans("", "", string.punctuation))
        
        # Detectar si la consulta está relacionada con el clima
        has_weather_intent = self._has_weather_intent(message_clean)
        
        # Extraer ciudad y días
        city = self._extract_city(message_clean)
        days = self._extract_days(message_clean)
        
        # Logging para debug
        print(f"Mensaje: '{original_message}'")
        print(f"Intent clima: {has_weather_intent}, Ciudad: {city}, Días: {days}")
        
        if has_weather_intent and city is not None:
            try:
                db = next(get_db())
                
                # Si no se especificó días, usar 0 (hoy)
                if days is None:
                    days = 0
                
                # Obtener la predicción
                prediction = await model.prediction_weather_future(city, days, db)
                
                # Registrar la estructura de la predicción para depuración
                print(f"Estructura de prediction: {type(prediction)}")
                
                # Extraer datos del clima de forma segura
                weather_data = self._extract_weather_data(prediction)
                
                # Añadir una interpretación si no hay "condition"
                if weather_data['condition'] == 'No disponible':
                    weather_data['condition'] = self._interpret_weather(
                        weather_data['temp_c'], 
                        weather_data['humidity']
                    )
                
                # Construir el informe meteorológico
                day_text = "hoy" if days == 0 else f"los próximos {days} días"
                weather_report = (
                    f"Para {day_text} en {city.capitalize()}, "
                    f"la temperatura será de {weather_data['temp_c']}°C, "
                    f"la humedad de {weather_data['humidity']}% "
                )
                
                if weather_data['condition'] != 'No disponible':
                    weather_report += f"y las condiciones serán {weather_data['condition']}."
                else:
                    weather_report += "."
                
                db.close()
                
                time_of_day = self._get_time_of_day()
                
                prompt = (
                    f"Imagina que eres un experto meteorológico y quiero que generes una respuesta cálida, amigable, detallada y de forma breve "
                    f"para un usuario que pregunta sobre el clima en {city.capitalize()} para {days} días en adelante. Usa emojis y frases naturales. "
                    f"Es actualmente {time_of_day}, así que ajusta el tono de la respuesta para que sea apropiado. "
                    f"El pronóstico es:\n"
                    f"{weather_report}\n"
                    f"Genera una respuesta natural y atractiva que mencione explícitamente la temperatura de {weather_data['temp_c']}°C y la humedad de {weather_data['humidity']}%. Por favor responde en español solamente."
                )
                response = self.generate_response(prompt)
                return {"response": response}
            except Exception as e:
                print(f"Error en process_message: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error obteniendo la predicción: {str(e)}")
        
        # Si no detectamos intención de clima o falta información crítica
        if has_weather_intent:
            if city is None:
                return {"response": "¿Para qué ciudad quieres saber el clima? No pude identificar la ciudad en tu mensaje."}
            else:
                return {"response": f"Entiendo que quieres saber sobre el clima en {city.capitalize()}, pero necesito más detalles. ¿Para cuántos días quieres el pronóstico?"}
        else:
            return {"response": "No entendí bien la pregunta. Para conocer el clima, pregúntame algo como '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'"}