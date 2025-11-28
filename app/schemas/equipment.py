from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EquipmentCreate(BaseModel):
    name: str

class EquipmentOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
