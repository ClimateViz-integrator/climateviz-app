from fastapi import FastAPI
from config.db import Base, engine
from routes import prediction_route, chat_route
from fastapi.middleware.cors import CORSMiddleware
import threading
import asyncio
from Controllers.chatController import run_bot


#Base.metadata.create_all(bind=engine)
app = FastAPI(title="Weather API", description="API para predecir el clima", version="0.1.0")

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_route.router, tags=["Prediction"])
app.include_router(chat_route.router, tags=["Chat"])

@app.get("/")
def main():
    return {"message": "Hello World"}

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

print("FastAPI está corriendo en paralelo con el bot de Telegram...")