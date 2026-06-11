from pydantic import BaseModel
from typing import Optional
from datetime import time
from app.models.opening_hours import DayOfWeek


class OpeningHoursCreate(BaseModel):
    day_of_week: DayOfWeek
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool = False


class OpeningHoursUpdate(BaseModel):
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: Optional[bool] = None


class OpeningHoursResponse(BaseModel):
    id: int
    clinic_id: int
    day_of_week: DayOfWeek
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool

    model_config = {"from_attributes": True}
