# routes/routes.py
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from typing import List
from Controllers.chat_controller import WeatherBot
from Controllers.prediction_controller import PredictionController
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.chatRequest import ChatRequest
from sqlalchemy.orm import Session
from config.db import get_db
from models.tables import Forecast
from schemas.forecastSchema import ForecastSchema
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv('.env')

controller = PredictionController()

router = APIRouter()
TOKEN = os.getenv('TELEGRAM_TOKEN')

from functools import lru_cache
from typing import Tuple

@lru_cache(maxsize=128)
def cached_prediction(city: str, days: int) -> Tuple:
    # Solo datos simples aquí (usa hashing si pasas objetos)
    return asyncio.run(controller.predict_from_api(city, days))

# @router.get("/predict/", response_model=List[ForecastSchema])
@router.post("/predict_future_weather/",response_model=List[ForecastSchema],
    summary="Predicción del clima futuro",
    description="Este endpoint permite predecir el clima de una ciudad en un número determinado de días en el futuro. Usa un modelo de IA entrenado para generar las predicciones.",
    responses={
        200: {"description": "Predicción exitosa del clima"},
        400: {"description": "Error en la solicitud. Verifica los parámetros."},
        500: {"description": "Error interno del servidor"}
    }
)
async def predict(
    city: str = Query(..., title="Ciudad", description="Nombre de la ciudad para la predicción."),
    days: int = Query(title="Días en el futuro",
    description="Número de días en el futuro para la predicción. Selecciona entre 1 y 7.",
    enum=[1, 2, 3, 4, 5, 6, 7]),
    db: Session = Depends(get_db)
):
    
    try:
        inserted_forecasts, _ = await controller.predict_from_api(city=city, days=days, db=db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return inserted_forecasts


@router.post("/chat_bot/",
    summary="Interacción con el chatbot de clima",
    description="Este endpoint permite interactuar con un chatbot que proporciona información sobre el clima basado en IA.",
    responses={
        200: {"description": "Respuesta generada por el chatbot"},
        400: {"description": "Error en la solicitud"}
    }
)
async def chat_endpoint_salida(request: ChatRequest):
    return await chat_endpoint(request)



# ------------------------------
# Instancia global del bot
weather_bot = WeatherBot()

# Handlers de Telegram
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Pregúntame por el clima de una ciudad en los próximos días.")

async def get_prediction(update: Update, context: CallbackContext) -> None:
    response = await weather_bot.process_message(update.message.text, controller)
    await update.message.reply_text(response["response"])

# Punto de entrada para la API
async def chat_endpoint(request: ChatRequest):
    return await weather_bot.process_message(request.message, controller)

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
    