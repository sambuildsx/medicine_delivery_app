from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.models import Medicine
from app.schemas import MedicineOut

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.get("", response_model=List[MedicineOut])
def list_medicines(db: Session = Depends(get_db)):
    """List all medicines in the database."""
    return db.query(Medicine).all()

@router.get("/search", response_model=List[MedicineOut])
def search_medicines(q: str = "", db: Session = Depends(get_db)):
    """Search medicines by name or salt composition (case-insensitive)."""
    if not q:
        return db.query(Medicine).all()
        
    search_pattern = f"%{q.lower()}%"
    medicines = db.query(Medicine).filter(
        or_(
            Medicine.name.ilike(search_pattern),
            Medicine.salt_composition.ilike(search_pattern)
        )
    ).all()
    
    return medicines

@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine_detail(medicine_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a single medicine."""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    return medicine
