from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Basic info
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=True)
    district = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Location
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Specialty flags
    is_emergency = Column(Boolean, default=False)
    is_maternal = Column(Boolean, default=False)
    is_vaccination = Column(Boolean, default=False)
    is_telemedicine = Column(Boolean, default=False)

    # Ratings (computed)
    avg_rating = Column(Numeric(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="clinics")
    services = relationship("Service", back_populates="clinic", cascade="all, delete-orphan")
    doctors = relationship("Doctor", back_populates="clinic", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="clinic")
    reviews = relationship("Review", back_populates="clinic", cascade="all, delete-orphan")
    opening_hours = relationship("OpeningHours", back_populates="clinic", cascade="all, delete-orphan")
