from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import models, schemas
from database import SessionLocal, engine


app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        avatar_url="https://example.com/default-avatar.png"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/login", response_model=schemas.LoginResponse)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario por email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Email no encontrado")
    
    # Verificar password
    if not bcrypt.verify(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return {
        "message": "Login exitoso",
        "user": user
    }
