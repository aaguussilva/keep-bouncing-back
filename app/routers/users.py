from fastapi import APIRouter, Depends, HTTPException
import re
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import user
from app.schemas import user as user_schemas
from app import auth 

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=user_schemas.UserOut)
def create_user(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    email_normalized = user_data.email.strip().lower()
    name_clean = user_data.name.strip()
    password = user_data.password

    if not name_clean or len(name_clean) < 3 or len(name_clean) > 50:
        raise HTTPException(status_code=400, detail="Invalid name (must be between 3 and 50 characters)")

    # Allow letters (including common accented latin letters), spaces, apostrophes and hyphens only
    # Disallow other special characters
    name_pattern = r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$"
    if not re.match(name_pattern, name_clean):
        raise HTTPException(status_code=400, detail="Invalid name: only letters, spaces, hyphens and apostrophes are allowed")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (minimum 8 characters)")

    MAX_PASSWORD_LENGTH = 128
    if len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"Password too long (max {MAX_PASSWORD_LENGTH} characters)")

    existing_user = db.query(user.User).filter(user.User.email == email_normalized).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = user.User(
        name=name_clean,
        email=email_normalized,
        password=auth.hash_password(password)  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/update/{user_id}", response_model=user_schemas.UserOut)
def update_user(user_id: int, user_data: user_schemas.UserUpdate, 
                db: Session = Depends(get_db),
                current_user: user.User = Depends(auth.get_current_user)):
    # Sólo el dueño puede actualizar su cuenta
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    db_user = db.query(user.User).filter(user.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar contraseña actual si se quiere cambiar
    if user_data.newPassword:
        if not user_data.currentPassword:
            raise HTTPException(status_code=400, detail="Debes ingresar la contraseña actual para cambiarla")

        if not auth.verify_password(user_data.currentPassword, db_user.password):
            raise HTTPException(status_code=401, detail="La contraseña actual no es correcta")

        db_user.password = auth.hash_password(user_data.newPassword)

    # Actualizar otros campos
    if user_data.name:
        db_user.name = user_data.name

    if user_data.email:
        db_user.email = user_data.email

    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[user_schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(user.User).all()

@router.post("/login", response_model=user_schemas.LoginResponse)
def login_user(login_data: user_schemas.UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario por email
    user_obj = db.query(user.User).filter(user.User.email == login_data.email).first()
    
    if not user_obj:
        raise HTTPException(status_code=401, detail="Email no encontrado")
    
    # Verificar password hasheado
    if not auth.verify_password(login_data.password, user_obj.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Crear token JWT (sub = id)
    access_token = auth.create_access_token(subject=str(user_obj.id))
    
    return {
        "message": "Login exitoso",
        "user": user_obj,
        "token": access_token
    }

@router.get("/{user_id}", response_model=user_schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db),
             current_user: user.User = Depends(auth.get_current_user)):
    # Solo el dueño puede acceder a su información
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Buscar el usuario por ID
    db_user = db.query(user.User).filter(user.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int,db: Session = Depends(get_db),
                current_user: user.User = Depends(auth.get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"detail": "User deleted"}
