from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    clinic_id: int
    service_id: Optional[int] = None
    patient_name: str
    patient_phone: Optional[str] = None
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    id: int
    patient_id: Optional[int] = None
    clinic_id: int
    service_id: Optional[int] = None
    patient_name: str
    patient_phone: Optional[str] = None
    appointment_date: datetime
    notes: Optional[str] = None
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
