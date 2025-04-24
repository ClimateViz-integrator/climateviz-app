from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class HourSchema(BaseModel):
    date_time: datetime
    temp_pred: float
    humidity_pred: float

    class Config:
        from_attributes = True