# routes/routes.py
import os
import asyncio
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

from Controllers.prediction_controller import PredictionController
from Controllers.report.export_data import ReportController
from schemas.chatRequest import ChatRequest
from schemas.forecastSchema import ForecastSchema
from config.db import get_db
from Controllers.chatbot.weather_bot import WeatherBot
from Controllers.userController import exist_user

from dotenv import load_dotenv

# Configuración
load_dotenv(".env")
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Instancias globales
controller = PredictionController()
weather_bot = WeatherBot()
router = APIRouter()
reportController = ReportController()


@router.post(
    "/predict_future_weather/",
    response_model=List[ForecastSchema],
    summary="Predicción del clima futuro",
    description="Predice el clima de una ciudad en un número determinado de días en el futuro usando un modelo de IA previamente entrenado.",
    responses={
        200: {"description": "Predicción exitosa del clima"},
        400: {"description": "Error en la solicitud. Verifica los parámetros."},
        500: {"description": "Error interno del servidor"},
    },
)
async def predict(
    city: str = Query(
        ..., title="Ciudad", description="Nombre de la ciudad para la predicción."
    ),
    days: int = Query(
        ...,
        title="Días en el futuro",
        description="Selecciona entre 1 y 7.",
        enum=[1, 2, 3, 4, 5, 6, 7],
    ),
    user_id: Optional[int] = Query(
        None,
        title="ID de Usuario",
        description="ID del usuario que realiza la solicitud.",
    ),
    db: Session = Depends(get_db),
):
    # Validación de parámetros
    if not city or city.strip() == "":
        raise HTTPException(
            status_code=400, detail="El nombre de la ciudad no puede estar vacío."
        )

    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", city):
        raise HTTPException(
            status_code=400,
            detail="El nombre de la ciudad solo puede contener letras y espacios.",
        )

    if not isinstance(days, int):
        raise HTTPException(
            status_code=400, detail="El valor de días debe ser un número entero."
        )

    if not days:
        raise HTTPException(
            status_code=400, detail="El número de días no puede estar vacio."
        )

    if not city and not days:
        raise HTTPException(
            status_code=400, detail="Verifica los parámetros de la solicitud."
        )
    
    if not exist_user(user_id, db):
        raise HTTPException(
            status_code=401,
            detail="Debe estar autenticado para interactuar con el chatbot. Por favor, inicie sesión o regístrese. 🔐"
        )

    try:
        forecasts, _ = await controller.predict_from_api(city, days, db, user_id)

        return forecasts
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error interno del servidor: " + str(e)
        )


@router.post(
    "/chat_bot/",
    summary="Interacción con el chatbot de clima",
    description="Interactúa con un chatbot que proporciona información sobre el clima basado en IA.",
    responses={
        200: {"description": "Respuesta generada por el chatbot"},
        400: {"description": "Error en la solicitud"},
    },
)
async def chat_endpoint(
    request: ChatRequest,
    user_id: Optional[int] = Query(
        None,
        title="ID de Usuario",
        description="ID del usuario que realiza la solicitud.",
    ),
    db: Session = Depends(get_db),
    
):
    try:
        if not exist_user(user_id, db):
            raise HTTPException(
                status_code=401,
                detail="Debe estar autenticado para interactuar con el chatbot. Por favor, inicie sesión o regístrese. 🔐"
            )
        context_id = "global_context"
        result = await weather_bot.process_message(
            context_id, request.message, controller, db, user_id
        )    

        # Si hay un reporte disponible, retornarlo directamente
        if (
            isinstance(result, dict)
            and result.get("download_available")
            and "report" in result
        ):
            return result["report"]  # Esto retorna el FileResponse directamente

        # Para respuestas normales, retornar solo el texto
        if isinstance(result, dict):
            return {"response": result.get("response", ""), "download_available": False}

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error interno del servidor: " + str(e)
        )


@router.get(
    "/report_excel/",
    summary="Generar reporte en Excel",
    description="Genera y exporta un archivo en formato Excel con los datos climáticos almacenados en la base de datos.",
    responses={
        200: {"description": "Reporte generado correctamente"},
        500: {"description": "Error al generar el reporte"},
    },
)
def report_excel(user_id: int, db: Session = Depends(get_db)):
    return reportController.export_data_excel(db, user_id)

