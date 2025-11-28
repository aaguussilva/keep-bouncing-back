from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.trick import TrickOut

class PegueCreate(BaseModel):
    user_id: int
    equipment: str
    date: datetime
    duration: int
    tricks_ids: list[int]
    notes: str

class PegueOut(BaseModel):
    id: int
    user_id: int
    equipment: str
    date: datetime
    duration: int
    notes: str
    tricks: list[TrickOut]

    model_config = ConfigDict(from_attributes=True)
