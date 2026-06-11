from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.clinic import Clinic
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.utils.dependencies import get_current_user

router = APIRouter()


def _recompute_rating(clinic: Clinic, db: Session):
    """Recompute and save the clinic's average rating after a review change."""
    result = db.query(func.avg(Review.rating), func.count(Review.id)).filter(
        Review.clinic_id == clinic.id
    ).one()
    clinic.avg_rating = result[0] or 0.00
    clinic.total_reviews = result[1]
    db.commit()


@router.get("/clinics/{clinic_id}/reviews", response_model=List[ReviewResponse])
def list_reviews(clinic_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a clinic."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return (
        db.query(Review)
        .filter(Review.clinic_id == clinic_id)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.post(
    "/clinics/{clinic_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_review(
    clinic_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Post a rating/review for a clinic. One review per user per clinic."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id, Clinic.is_active == True).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    existing = db.query(Review).filter(
        Review.clinic_id == clinic_id, Review.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this clinic")

    review = Review(
        user_id=current_user.id,
        clinic_id=clinic_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    db.flush()
    _recompute_rating(clinic, db)
    db.refresh(review)
    return review


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update your own review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    db.flush()

    clinic = db.query(Clinic).filter(Clinic.id == review.clinic_id).first()
    _recompute_rating(clinic, db)
    db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete your own review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    clinic_id = review.clinic_id
    db.delete(review)
    db.flush()
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if clinic:
        _recompute_rating(clinic, db)
