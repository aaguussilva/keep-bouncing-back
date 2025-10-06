from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import equipment
from app.schemas import equipment as equipment_schemas

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[equipment_schemas.EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    return db.query(equipment.Equipment).all()

@router.post("/", response_model=equipment_schemas.EquipmentOut)
def create_equipment(equipment_data: equipment_schemas.EquipmentCreate, db: Session = Depends(get_db)):
    new_equipment = equipment.Equipment(
        name=equipment_data.name
    )
    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)
    return new_equipment
