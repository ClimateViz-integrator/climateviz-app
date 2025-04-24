from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class HourCreate(BaseModel):
    forecast_id: int
    date_time: datetime
    temp_pred: float
    humidity_pred: float