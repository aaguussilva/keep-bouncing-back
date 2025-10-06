from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import pegue, trick
from app.schemas import pegue as pegue_schemas

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=bool)
def create_pegue(pegue_data: pegue_schemas.PegueCreate, db: Session = Depends(get_db)):
    trick_objects = db.query(trick.Trick).filter(trick.Trick.id.in_(pegue_data.tricks_ids)).all()

    if len(trick_objects) != len(pegue_data.tricks_ids):
        raise HTTPException(status_code=400, detail="Uno o más trucos no existen")

    new_pegue = pegue.Pegue(
        user_id=pegue_data.user_id,
        equipment=pegue_data.equipment,
        date=pegue_data.date,
        duration=pegue_data.duration,
        notes=pegue_data.notes
    )

    new_pegue.tricks = trick_objects

    db.add(new_pegue)
    db.commit()
    db.refresh(new_pegue)
    return True

@router.get("/", response_model=list[pegue_schemas.PegueOut])
def list_pegues(db: Session = Depends(get_db)):
    return db.query(pegue.Pegue).all()
