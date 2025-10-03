from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine
import json
from contextlib import asynccontextmanager


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_tricks()
    yield


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_tricks():
    db = next(get_db())
    try:
        with open('highline_tricks.json', 'r', encoding='utf-8') as file:
            tricks_by_level = json.load(file)
            inserted = 0
            for level, tricks in tricks_by_level.items():
                for name in tricks:
                    if not db.query(models.Trick).filter_by(name=name).first():
                        db.add(models.Trick(name=name, level=int(level)))
                        inserted += 1
            db.commit()
            print(f"{inserted} trucos insertados correctamente.")
    except Exception as e:
        print(f"Error al insertar trucos: {e}")
        db.rollback()
    finally:
        db.close()


# Ejecutar seed al iniciar
seed_tricks()


@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password  # Guardar password simple (sin hash por simplicidad)
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
    
    # Verificar password (comparación simple sin hash)
    if user.password != login_data.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return {
        "message": "Login exitoso",
        "user": user
    }

@app.post("/pegue", response_model=bool)
def create_pegue(pegue: schemas.PegueCreate, db: Session = Depends(get_db)):
    new_pegue = models.Pegue(
        user_id=pegue.user_id,
        equipment=pegue.equipment,
        date=pegue.date,
        duration=pegue.duration,
        tricks=pegue.tricks,
        notes=pegue.notes)
    db.add(new_pegue)
    db.commit()
    db.refresh(new_pegue)
    return True

@app.get("/tricks", response_model=list[schemas.TrickOut])
def list_tricks(db: Session = Depends(get_db)):
    return db.query(models.Trick).all()

