import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Date, Float, String
from sqlalchemy.orm import relationship
from config.db import Base


class Input_data(Base):
    __tablename__ = 'inputs'
    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    wind_kph = Column(Float)
    wind_degree = Column(Float)
    pressure_mb = Column(Float)
    precip_mm = Column(Float)
    cloud = Column(Float)
    feelslike_c = Column(Float)
    vis_km = Column(Float)
    uv = Column(Float)
    predictions = relationship('Predictions', back_populates='input')


class Predictions(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    city = Column(String(255))
    region = Column(String(255))
    country = Column(String(255))
    lat = Column(Float)
    lon = Column(Float)
    temp_c = Column(Float)
    localtime = Column(DateTime)
    localtime_future = Column(DateTime, default=datetime.datetime.now())
    wind_mph = Column(Float)
    wind_degree = Column(Float)
    pressure_mb = Column(Float)
    precip_mm = Column(Float)
    humidity = Column(Float)
    cloud = Column(Float)
    feelslike_c = Column(Float)
    vis_km = Column(Float)
    uv = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    pm2_5 = Column(Float)
    pm10 = Column(Float)
    us_epa_index = Column(Integer)
    gb_defra_index = Column(Integer)
    input_id = Column(Integer, ForeignKey('inputs.id'))

    input = relationship('Input_data', back_populates='predictions') 




