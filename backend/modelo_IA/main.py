# main.py
import set_tf_env
import asyncio
import threading
from fastapi import FastAPI
from routes import prediction_route
from config.db import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Crear las tablas en la BD si no existen
Base.metadata.create_all(bind=engine)

description = """
🧠 **ClimateViz API**

ClimateViz API es una interfaz RESTful desarrollada con FastAPI que permite acceder a datos meteorológicos
y realizar predicciones avanzadas usando inteligencia artificial. Está diseñada para integrarse en
aplicaciones web, móviles o de escritorio que requieren predicción de variables climáticas como:

- 🌡️ Temperatura  
- 💧 Humedad  

---

🔧 **Funcionalidades disponibles:**

- 🔍 Predicción del clima mediante modelos entrenados (LSTM, Random Forest, etc.)
- ☁️ Integración con WeatherAPI para datos en tiempo real
- 🤖 Chatbot inteligente con IA (Gemini + Spacy + Telegram)
- 💬 Procesamiento de lenguaje natural para solicitudes del usuario
- 📈 Predicciones desde datos históricos o en vivo
- 📡 Middleware CORS habilitado para conexión desde frontend web

---
"""

app = FastAPI(title="ClimateViz", description=description, version="0.1.0")

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Incluir rutas
app.include_router(prediction_route.router, tags=["Predictions"])


@app.get("/")
def main():
    return {"message": "Hello World"}

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(prediction_route.run_bot())

bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

print("FastAPI está corriendo en paralelo con el bot de Telegram...")
