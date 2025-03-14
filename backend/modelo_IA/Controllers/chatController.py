from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import os
from pathlib import Path
import csv
import re
import string
from datetime import datetime
from schemas.chat import ChatRequest
import spacy
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from Controllers.model import ModelIa
from config.db import get_db

# Cargar variables de entorno
load_dotenv('.env')

# Configurar la API de Google Generative AI
genai.configure(api_key=os.getenv('API_KEY_G'))

# Token del bot de Telegram
TOKEN = os.getenv('TELEGRAM_TOKEN')

class WeatherBot:
    def __init__(self):
        # Rutas de archivos usando pathlib para mejor portabilidad
        self.base_dir = Path(__file__).parent
        self.cities_file = self.base_dir / ".." / "Data" / "cities.txt"
        self.train_file = self.base_dir / ".." / "Data" / "data_train.csv"
        
        # Cargar recursos
        self.nlp = spacy.load("es_core_news_sm")
        self.cities = self._load_cities()
        self.model = ModelIa(str(self.train_file))
        
        # Mapeo de términos a días
        self.day_terms = {
            "hoy": 0, "el día de hoy": 0, "ahora": 0,
            "mañana": 1, "el día siguiente": 1,
            "pasado mañana": 2
        }
        
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
                        cities.add(row[1].strip().lower())
        except Exception as e:
            print(f"Error loading cities: {e}")
        return cities
    
    def _extract_city(self, message_clean):
        words = message_clean.split()
        for i in range(len(words)):
            for j in range(i + 1, len(words) + 1):
                candidate = " ".join(words[i:j])
                if candidate in self.cities:
                    return candidate
        return None
    
    def _extract_days(self, message_clean):
        # Check for specific day terms
        for term, days in self.day_terms.items():
            if term in message_clean:
                return days
        
        # Check for numeric days
        match = re.search(r'\d+', message_clean)
        if match:
            return int(match.group())
        
        return None
    
    def _get_time_of_day(self):
        hour = datetime.now().hour
        return "día" if 6 <= hour < 18 else "noche"
    
    def generate_response(self, prompt):
        try:
            response = self.gen_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    async def process_message(self, message):
        message = message.lower()
        message_clean = message.translate(str.maketrans("", "", string.punctuation))
        
        city = self._extract_city(message_clean)
        days = self._extract_days(message_clean)
        
        if "clima" in message_clean and days is not None and city is not None:
            try:
                db = next(get_db())
                
                report = []
                for day in range(days + 1):
                    prediction = await self.model.prediction_weather_future(city, day, db)
                    temp = getattr(prediction, 'temp_c', 'No disponible')
                    humidity = getattr(prediction, 'humidity', 'No disponible')
                    report.append(f"Para el día {day}, la temperatura será de {temp}°C y la humedad de {humidity}%.")
                
                db.close()
                
                time_of_day = self._get_time_of_day()
                
                prompt = (
                    f"Imagina que eres un experto meteorológico y quiero que generes una respuesta cálida, amigable, detallada y de forma breve "
                    f"para un usuario que pregunta sobre el clima en los próximos {days} días. Usa emojis y frases naturales. "
                    f"Es actualmente {time_of_day}, así que ajusta el tono de la respuesta para que sea apropiado. "
                    f"La ciudad consultada es {city.capitalize()} y el pronóstico es:\n"
                    f"{' '.join(report)}\n"
                    f"Genera una respuesta natural y atractiva."
                )
                response = self.generate_response(prompt)
                return {"response": response}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error obteniendo la predicción: {str(e)}")
        
        return {"response": "No entendí bien la pregunta. Asegúrate de mencionar 'clima', una ciudad y un número de días."}

# Instancia global del bot
weather_bot = WeatherBot()

# Handlers de Telegram
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Pregúntame por el clima de una ciudad en los próximos días.")

async def get_prediction(update: Update, context: CallbackContext) -> None:
    response = await weather_bot.process_message(update.message.text)
    await update.message.reply_text(response["response"])

# Punto de entrada para la API
async def chat_endpoint(request: ChatRequest):
    return await weather_bot.process_message(request.message)

# Función principal para ejecutar el bot
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_prediction))
    print("Bot de Telegram iniciado...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Future()
