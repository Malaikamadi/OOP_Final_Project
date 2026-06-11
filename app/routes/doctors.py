from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.utils.dependencies import require_clinic_admin

router = APIRouter()


def _get_clinic_or_404(clinic_id: int, db: Session) -> Clinic:
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id, Clinic.is_active == True).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.get("/clinics/{clinic_id}/doctors", response_model=List[DoctorResponse])
def list_doctors(clinic_id: int, db: Session = Depends(get_db)):
    """Get all doctors at a clinic."""
    _get_clinic_or_404(clinic_id, db)
    return db.query(Doctor).filter(Doctor.clinic_id == clinic_id).all()


@router.post(
    "/clinics/{clinic_id}/doctors",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_doctor(
    clinic_id: int,
    data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Add a doctor to a clinic (clinic owner or admin only)."""
    clinic = _get_clinic_or_404(clinic_id, db)
    if clinic.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    doctor = Doctor(clinic_id=clinic_id, **data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/clinics/{clinic_id}/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    clinic_id: int,
    doctor_id: int,
    data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Update a doctor's profile."""
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id, Doctor.clinic_id == clinic_id
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/clinics/{clinic_id}/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    clinic_id: int,
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Remove a doctor from a clinic."""
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id, Doctor.clinic_id == clinic_id
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
