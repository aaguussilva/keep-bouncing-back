from pydantic import BaseModel

class TrickOut(BaseModel):
    id: int
    name: str
    level: int

    class Config:
        from_attributes = True
