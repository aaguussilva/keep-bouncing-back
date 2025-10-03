from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Cambiado de password_hash a password simple
    created_at = Column(DateTime, default=datetime.utcnow)

class Pegue(Base):
    __tablename__ = "pegue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer)
    tricks = Column(Integer, ForeignKey("tricks.id"), nullable=False)
    notes = Column(Text)

class Trick(Base):
    __tablename__ = "tricks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
