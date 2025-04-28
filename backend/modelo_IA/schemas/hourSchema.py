from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class HourSchema(BaseModel):
    date_time: datetime
    wind_kph: float
    cloud: float
    uv: float
    temp_pred: float
    humidity_pred: float

    class Config:
        from_attributes = True