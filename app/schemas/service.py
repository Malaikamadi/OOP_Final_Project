from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ServiceCreate(BaseModel):
    service_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: bool = True


class ServiceUpdate(BaseModel):
    service_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: Optional[bool] = None


class ServiceResponse(BaseModel):
    id: int
    clinic_id: int
    service_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
