from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import trick
from app.schemas import trick as trick_schemas

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[trick_schemas.TrickOut])
def list_tricks(db: Session = Depends(get_db)):
    return db.query(trick.Trick).all()
