from fastapi import FastAPI
from config.db import Base, engine
from routes import prediction_route
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
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

@app.get("/")
def main():
    return {"message": "Hello World"}