from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import user
from app.schemas import user as user_schemas

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
    # Verificar si el email ya existe
    existing_user = db.query(user.User).filter(user.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = user.User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password  # Guardar password simple (sin hash por simplicidad)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/update/{user_id}", response_model=user_schemas.UserOut)
def update_user(user_id: int, user_data: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar contraseña actual si se quiere cambiar
    if user_data.newPassword:
        if not user_data.currentPassword:
            raise HTTPException(status_code=400, detail="Debes ingresar la contraseña actual para cambiarla")

        if db_user.password != user_data.currentPassword:
            raise HTTPException(status_code=401, detail="La contraseña actual no es correcta")

        # Actualizar contraseña
        db_user.password = user_data.newPassword

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
    
    # Verificar password (comparación simple sin hash)
    if user_obj.password != login_data.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return {
        "message": "Login exitoso",
        "user": user_obj
    }

@router.get("/{user_id}", response_model=user_schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    # Buscar el usuario por ID
    db_user = db.query(user.User).filter(user.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return db_user
