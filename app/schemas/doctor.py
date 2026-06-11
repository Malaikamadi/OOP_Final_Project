from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoctorCreate(BaseModel):
    full_name: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    qualification: Optional[str] = None
    is_available: bool = True


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    qualification: Optional[str] = None
    is_available: Optional[bool] = None


class DoctorResponse(BaseModel):
    id: int
    clinic_id: int
    full_name: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    qualification: Optional[str] = None
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
