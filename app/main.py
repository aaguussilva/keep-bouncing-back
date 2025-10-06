from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, pegues, tricks, equipment
from app.database import engine
from app.models import user, pegue, trick, equipment as equipment_model
from app.utils.seed import seed_tricks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas
user.Base.metadata.create_all(bind=engine)

# Seed inicial
seed_tricks()

# Incluir routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(pegues.router, prefix="/pegues", tags=["Pegues"])
app.include_router(tricks.router, prefix="/tricks", tags=["Tricks"])
app.include_router(equipment.router, prefix="/equipment", tags=["Equipment"])
