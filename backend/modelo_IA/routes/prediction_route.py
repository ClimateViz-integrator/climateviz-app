import asyncio
from functools import lru_cache
from Controllers.chatController import WeatherBot

from fastapi import APIRouter, Depends, Query
from config.db import get_db
from schemas.chat import ChatRequest
from sqlalchemy.orm import Session
from Controllers.model import ModelIa
import os
from Controllers.export_data import ReportController
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
load_dotenv('.env')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_TRAIN_DIR = os.path.join(BASE_DIR, "..", "Data")  # Subimos un nivel y ubicamos Data/train_model
FILE_TRAIN_DIR = os.path.join(DATA_TRAIN_DIR, "data_train_completo.csv")

TOKEN = os.getenv('TELEGRAM_TOKEN')

router = APIRouter()


model_ia = ModelIa(FILE_TRAIN_DIR)

@lru_cache(maxsize=100)
def cached_prediction(city: str, days: int):
    return model_ia.prediction_weather_future(city, days)
@router.post("/predict_future_weather/",
    summary="Predicción del clima futuro",
    description="Este endpoint permite predecir el clima de una ciudad en un número determinado de días en el futuro. Usa un modelo de IA entrenado para generar las predicciones.",
    responses={
        200: {"description": "Predicción exitosa del clima"},
        400: {"description": "Error en la solicitud. Verifica los parámetros."},
        500: {"description": "Error interno del servidor"}
    }
)
async def predict_future(
    city: str = Query(..., title="Ciudad", description="Nombre de la ciudad para la predicción."),
    days: int = Query(0, title="Días en el futuro", description="Número de días en el futuro para la predicción. 0 significa hoy, máximo 7 días."),
    db: Session = Depends(get_db)
):
    return await model_ia.prediction_weather_future(city, days, db)


@router.get("/report_excel/",
    summary="Generar reporte en Excel",
    description="Genera y exporta un archivo en formato Excel con los datos climáticos almacenados en la base de datos.",
    responses={
        200: {"description": "Reporte generado correctamente"},
        500: {"description": "Error al generar el reporte"}
    }
)
def report_excel(db: Session = Depends(get_db)):
    return ReportController().export_data_excel(db)


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
    response = await weather_bot.process_message(update.message.text, model_ia)
    await update.message.reply_text(response["response"])

# Punto de entrada para la API
async def chat_endpoint(request: ChatRequest):
    return await weather_bot.process_message(request.message, model_ia)

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
    