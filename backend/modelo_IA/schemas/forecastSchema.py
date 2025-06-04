from pydantic import BaseModel
from typing import List
from datetime import date
from schemas.hourSchema import HourSchema


class ForecastSchema(BaseModel):
    city: str
    forecast_date: date
    astro: dict
    location: dict
    day: dict
    hours: List[HourSchema] = []

    class Config:
        from_attributes = True
