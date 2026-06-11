from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class ClinicCreate(BaseModel):
    name: str
    address: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_emergency: bool = False
    is_maternal: bool = False
    is_vaccination: bool = False
    is_telemedicine: bool = False


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_emergency: Optional[bool] = None
    is_maternal: Optional[bool] = None
    is_vaccination: Optional[bool] = None
    is_telemedicine: Optional[bool] = None
    is_active: Optional[bool] = None


class ClinicResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_emergency: bool
    is_maternal: bool
    is_vaccination: bool
    is_telemedicine: bool
    avg_rating: Optional[Decimal] = None
    total_reviews: int
    is_active: bool
    created_at: datetime
    # Optional computed field for GPS search
    distance_km: Optional[float] = None

    model_config = {"from_attributes": True}


class ClinicListResponse(BaseModel):
    total: int
    clinics: List[ClinicResponse]
