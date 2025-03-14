from functools import lru_cache
from Controllers.chatController import chat_endpoint
from fastapi import APIRouter, Depends
from config.db import get_db
from schemas.chat import ChatRequest
from sqlalchemy.orm import Session
from Controllers.model import ModelIa
import os
from Controllers.export_data import ReportController

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_TRAIN_DIR = os.path.join(BASE_DIR, "..", "Data")  # Subimos un nivel y ubicamos Data/train_model
FILE_TRAIN_DIR = os.path.join(DATA_TRAIN_DIR, "data_train.csv")


router = APIRouter()
# @router.post("/new_predict/")
# def new_predict(city: str, db: Session = Depends(get_db)):
#     model_ia = ModelIa(FILE_TRAIN_DIR)
#     return model_ia.prediction_weather(city, db)
model_ia = ModelIa(FILE_TRAIN_DIR)

@lru_cache(maxsize=100)
def cached_prediction(city: str, days: int):
    return model_ia.prediction_weather_future(city, days)
@router.post("/predict_future_weather/")
async def predict_future(city: str, days: int = 0, db: Session = Depends(get_db)):
    #model_ia.plot_training_results()
    return await model_ia.prediction_weather_future(city, days, db)

@router.get("/report_excel/")
def report_excel(db: Session = Depends(get_db)):
    """
    Genera y guarda el reporte en formato CSV en la ruta especificada por el usuario
    """
    report_controller = ReportController()
    return report_controller.export_data_excel(db)

@router.post("/chat_bot/")
async def chat_endpoint_salida(request: ChatRequest):
    return await chat_endpoint(request, )



    

