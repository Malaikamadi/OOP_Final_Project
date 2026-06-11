from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.clinic import Clinic
from app.models.user import User
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse, ClinicListResponse
from app.utils.dependencies import get_current_user, require_clinic_admin
from app.utils.geo import filter_by_radius

router = APIRouter()


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
def create_clinic(
    data: ClinicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Create a new clinic (clinic_admin or admin only)."""
    clinic = Clinic(**data.model_dump(), owner_id=current_user.id)
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic


@router.get("", response_model=ClinicListResponse)
def list_clinics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all active clinics with pagination."""
    query = db.query(Clinic).filter(Clinic.is_active == True)
    total = query.count()
    clinics = query.offset(skip).limit(limit).all()
    return {"total": total, "clinics": clinics}


@router.get("/search", response_model=List[ClinicResponse])
def search_clinics(
    service: Optional[str] = Query(None, description="Filter by service name"),
    district: Optional[str] = Query(None, description="Filter by district"),
    lat: Optional[float] = Query(None, description="User latitude for GPS search"),
    lng: Optional[float] = Query(None, description="User longitude for GPS search"),
    radius_km: float = Query(10.0, description="Search radius in km (default 10km)"),
    is_emergency: Optional[bool] = Query(None),
    is_maternal: Optional[bool] = Query(None),
    is_vaccination: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Search clinics by service name, district, GPS coordinates, or specialty flags.
    - Combine any filters freely.
    - If lat+lng are provided, results are sorted by distance and filtered by radius_km.
    """
    query = db.query(Clinic).filter(Clinic.is_active == True)

    if district:
        query = query.filter(Clinic.district.ilike(f"%{district}%"))
    if is_emergency is not None:
        query = query.filter(Clinic.is_emergency == is_emergency)
    if is_maternal is not None:
        query = query.filter(Clinic.is_maternal == is_maternal)
    if is_vaccination is not None:
        query = query.filter(Clinic.is_vaccination == is_vaccination)

    if service:
        from app.models.service import Service
        query = query.join(Clinic.services).filter(
            Service.service_name.ilike(f"%{service}%"),
            Service.is_available == True,
        )

    clinics = query.all()

    if lat is not None and lng is not None:
        results = filter_by_radius(clinics, lat, lng, radius_km)
        output = []
        for clinic, dist in results:
            c = ClinicResponse.model_validate(clinic)
            c.distance_km = round(dist, 2)
            output.append(c)
        return output

    return clinics


@router.get("/emergency", response_model=List[ClinicResponse])
def list_emergency_clinics(db: Session = Depends(get_db)):
    """Get all active emergency clinics."""
    return db.query(Clinic).filter(Clinic.is_active == True, Clinic.is_emergency == True).all()


@router.get("/maternal", response_model=List[ClinicResponse])
def list_maternal_clinics(db: Session = Depends(get_db)):
    """Get all active maternal health clinics."""
    return db.query(Clinic).filter(Clinic.is_active == True, Clinic.is_maternal == True).all()


@router.get("/vaccination", response_model=List[ClinicResponse])
def list_vaccination_centers(db: Session = Depends(get_db)):
    """Get all active vaccination centers."""
    return db.query(Clinic).filter(Clinic.is_active == True, Clinic.is_vaccination == True).all()


@router.get("/{clinic_id}", response_model=ClinicResponse)
def get_clinic(clinic_id: int, db: Session = Depends(get_db)):
    """Get a single clinic by ID."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id, Clinic.is_active == True).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.put("/{clinic_id}", response_model=ClinicResponse)
def update_clinic(
    clinic_id: int,
    data: ClinicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Update clinic details (owner or admin only)."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    from app.models.user import UserRole
    if clinic.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this clinic")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(clinic, field, value)

    db.commit()
    db.refresh(clinic)
    return clinic


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clinic(
    clinic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    """Soft-delete a clinic (sets is_active = False)."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    from app.models.user import UserRole
    if clinic.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    clinic.is_active = False
    db.commit()
