from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.clinic import Clinic
from app.models.opening_hours import OpeningHours
from app.models.user import User, UserRole
from app.schemas.opening_hours import OpeningHoursCreate, OpeningHoursUpdate, OpeningHoursResponse
from app.utils.dependencies import get_current_user, require_clinic_admin

router = APIRouter()


@router.get("/clinics/{clinic_id}/opening-hours", response_model=List[OpeningHoursResponse])
def get_opening_hours(clinic_id: int, db: Session = Depends(get_db)):
    """Get the opening hours schedule for a clinic."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return db.query(OpeningHours).filter(OpeningHours.clinic_id == clinic_id).all()


@router.post(
    "/clinics/{clinic_id}/opening-hours",
    response_model=OpeningHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_opening_hours(
    clinic_id: int,
    data: OpeningHoursCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Add an opening hours entry for a specific day."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    if clinic.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Prevent duplicate day entries
    existing = db.query(OpeningHours).filter(
        OpeningHours.clinic_id == clinic_id,
        OpeningHours.day_of_week == data.day_of_week,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Opening hours for {data.day_of_week} already exist. Use PUT to update.",
        )

    oh = OpeningHours(clinic_id=clinic_id, **data.model_dump())
    db.add(oh)
    db.commit()
    db.refresh(oh)
    return oh


@router.put("/clinics/{clinic_id}/opening-hours/{oh_id}", response_model=OpeningHoursResponse)
def update_opening_hours(
    clinic_id: int,
    oh_id: int,
    data: OpeningHoursUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Update an opening hours entry."""
    oh = db.query(OpeningHours).filter(
        OpeningHours.id == oh_id, OpeningHours.clinic_id == clinic_id
    ).first()
    if not oh:
        raise HTTPException(status_code=404, detail="Opening hours entry not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(oh, field, value)
    db.commit()
    db.refresh(oh)
    return oh


@router.delete("/clinics/{clinic_id}/opening-hours/{oh_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opening_hours(
    clinic_id: int,
    oh_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Delete an opening hours entry."""
    oh = db.query(OpeningHours).filter(
        OpeningHours.id == oh_id, OpeningHours.clinic_id == clinic_id
    ).first()
    if not oh:
        raise HTTPException(status_code=404, detail="Opening hours entry not found")
    db.delete(oh)
    db.commit()
