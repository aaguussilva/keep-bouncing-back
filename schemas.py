from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # plain password, to be hashed

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user: UserOut

class TrickOut(BaseModel):
    id: int
    name: str
    level: int

    class Config:
        from_attributes = True

class PegueCreate(BaseModel):
    user_id: int
    equipment: str
    date: datetime
    duration: int
    tricks: list[int]
    notes: str
