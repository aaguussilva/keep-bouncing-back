from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # plain password, to be hashed

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user: UserOut
    token: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    currentPassword: str | None = None
    newPassword: str | None = None
