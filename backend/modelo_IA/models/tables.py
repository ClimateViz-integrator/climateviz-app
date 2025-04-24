# models/tables.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from config.db import Base

class Forecast(Base):
    __tablename__ = 'forecasts'
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    forecast_date = Column(Date, nullable=False)  # Representa el día de predicción
    astro = Column(JSON)  # Datos astronómicos
    location = Column(JSON)  # Información de la localización
    # Relación con la tabla de horas
    hours = relationship("Hour", back_populates="forecast", cascade="all, delete-orphan")

class Hour(Base):
    __tablename__ = 'hours'
    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecasts.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    temp_pred = Column(Float, nullable=False)
    humidity_pred = Column(Float, nullable=False)
    forecast = relationship("Forecast", back_populates="hours")
