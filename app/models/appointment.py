from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    pending = "Pending"
    confirmed = "Confirmed"
    cancelled = "Cancelled"
    completed = "Completed"
    no_show = "No Show"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    patient_name = Column(String(255), nullable=False)
    patient_phone = Column(String(20), nullable=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(
        SAEnum(AppointmentStatus),
        default=AppointmentStatus.pending,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("User", back_populates="appointments")
    clinic = relationship("Clinic", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
