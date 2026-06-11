from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.clinic import Clinic
from app.models.service import Service
from app.models.user import User, UserRole
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.utils.dependencies import get_current_user, require_clinic_admin

router = APIRouter()


def _get_clinic_or_404(clinic_id: int, db: Session) -> Clinic:
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id, Clinic.is_active == True).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.get("/clinics/{clinic_id}/services", response_model=List[ServiceResponse])
def list_services(clinic_id: int, db: Session = Depends(get_db)):
    """Get all services offered by a clinic."""
    _get_clinic_or_404(clinic_id, db)
    return db.query(Service).filter(Service.clinic_id == clinic_id).all()


@router.post(
    "/clinics/{clinic_id}/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_service(
    clinic_id: int,
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Add a service to a clinic (clinic owner or admin only)."""
    clinic = _get_clinic_or_404(clinic_id, db)
    if clinic.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    service = Service(clinic_id=clinic_id, **data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/clinics/{clinic_id}/services/{service_id}", response_model=ServiceResponse)
def update_service(
    clinic_id: int,
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Update a service."""
    service = db.query(Service).filter(
        Service.id == service_id, Service.clinic_id == clinic_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/clinics/{clinic_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    clinic_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Delete a service from a clinic."""
    service = db.query(Service).filter(
        Service.id == service_id, Service.clinic_id == clinic_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
