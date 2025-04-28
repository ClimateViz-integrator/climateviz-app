from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ForecastCreate(BaseModel):
    city: str
    forecast_date: date
    astro: dict
    day: dict
    location: dict