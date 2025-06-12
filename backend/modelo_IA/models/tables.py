# models/tables.py
from sqlalchemy import Boolean, Column, Integer, String, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from config.db import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    forecast_date = Column(Date, nullable=False)  # Representa el día de predicción
    astro = Column(JSON)  # Datos astronómicos
    location = Column(JSON)  # Información de la localización
    day = Column(JSON)  # Información del día
    # Relación con la tabla de horas
    hours = relationship(
        "Hour", back_populates="forecast", cascade="all, delete-orphan"
    )


class Hour(Base):
    __tablename__ = "hours"
    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecasts.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    wind_kph = Column(Float, nullable=True)
    cloud = Column(Float, nullable=True)
    uv = Column(Float, nullable=True)
    temp_pred = Column(Float, nullable=False)
    humidity_pred = Column(Float, nullable=False)
    forecast = relationship("Forecast", back_populates="hours")

    predictions = relationship("PredictionsUser", back_populates="hour")

class PredictionsUser(Base):
    __tablename__ = "predictions_user"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    hour_id = Column(Integer, ForeignKey("hours.id", ondelete="CASCADE"), nullable=False)

    hour = relationship("Hour", back_populates="predictions")
    user = relationship("User", back_populates="predictions")  # Relación con User



class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    verification_code = Column(String(64))
    enabled = Column(Boolean, default=False)
    password_reset_token = Column(String(64))
    token_creation_date = Column(DateTime)

    predictions = relationship("PredictionsUser", back_populates="user")