from fastapi import APIRouter, Depends, HTTPException
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
    # Verificar si el email ya existe
    existing_user = db.query(user.User).filter(user.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = user.User(
        name=user_data.name,
        email=user_data.email,
        password=auth.hash_password(user_data.password)  # <-- almacenar hasheada
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
