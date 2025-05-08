# routes/routes.py
import os
import asyncio
from typing import List, Tuple, Dict, Any
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from Controllers.chat_controller import WeatherBot
from Controllers.prediction_controller import PredictionController
from schemas.chatRequest import ChatRequest
from schemas.forecastSchema import ForecastSchema
from config.db import get_db

from dotenv import load_dotenv

# Configuración
load_dotenv('.env')
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Instancias globales
controller = PredictionController()
weather_bot = WeatherBot()
router = APIRouter()

# Cache para predicciones
# Usamos un diccionario simple como caché para funciones asíncronas
prediction_cache: Dict[Tuple[str, int], Tuple[Any, Any]] = {}
CACHE_TTL = 3600  # Tiempo de vida del caché en segundos (1 hora)
cache_timestamps: Dict[Tuple[str, int], float] = {}

async def get_cached_prediction(city: str, days: int, db: Session) -> Tuple[Any, Any]:
    """Obtiene predicción del caché o la genera y almacena"""
    cache_key = (city.lower(), days)
    current_time = asyncio.get_event_loop().time()
    
    # Verificar si está en caché y no ha expirado
    if cache_key in prediction_cache and (current_time - cache_timestamps.get(cache_key, 0)) < CACHE_TTL:
        print(f"Usando caché para {city}, {days} días")
        return prediction_cache[cache_key]
    
    # Si no está en caché o expiró, obtener nueva predicción
    print(f"Generando nueva predicción para {city}, {days} días")
    result = await controller.predict_from_api(city=city, days=days, db=db)
    
    # Almacenar en caché
    prediction_cache[cache_key] = result
    cache_timestamps[cache_key] = current_time
    
    return result

@router.post(
    "/predict_future_weather/",
    response_model=List[ForecastSchema],
    summary="Predicción del clima futuro",
    description="Predice el clima de una ciudad en un número determinado de días en el futuro usando IA.",
    responses={
        200: {"description": "Predicción exitosa del clima"},
        400: {"description": "Error en la solicitud. Verifica los parámetros."},
        500: {"description": "Error interno del servidor"}
    }
)
async def predict(
    city: str = Query(..., title="Ciudad", description="Nombre de la ciudad para la predicción."),
    days: int = Query(..., title="Días en el futuro", description="Selecciona entre 1 y 7.", enum=[1,2,3,4,5,6,7]),
    db: Session = Depends(get_db)
):
    # Validación de parámetros
    if not city or city.strip() == "":
        raise HTTPException(status_code=400, detail="El nombre de la ciudad no puede estar vacío.")
    
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", city):
        raise HTTPException(status_code=400, detail="El nombre de la ciudad solo puede contener letras y espacios.")
    
    if not isinstance(days, int):
        raise HTTPException(status_code=400, detail="El valor de días debe ser un número entero.")

    if not days:
        raise HTTPException(status_code=400, detail="El número de días no puede estar vacio.")
    
    if not city and not days:
        raise HTTPException(status_code=400, detail="Verifica los parámetros de la solicitud.")

    try:
        forecasts, _ = await get_cached_prediction(city.strip(), days, db)
        return forecasts
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor: " + str(e))

@router.post(
    "/chat_bot/",
    summary="Interacción con el chatbot de clima",
    description="Interactúa con un chatbot que proporciona información sobre el clima basado en IA.",
    responses={
        200: {"description": "Respuesta generada por el chatbot"},
        400: {"description": "Error en la solicitud"}
    }
)
async def chat_endpoint(request: ChatRequest):
    return await weather_bot.process_message(request.message, controller)

# Handlers de Telegram
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Pregúntame por el clima de una ciudad en los próximos días.")

async def get_prediction(update: Update, context: CallbackContext) -> None:
    response = await weather_bot.process_message(update.message.text, controller)
    await update.message.reply_text(response["response"])

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
