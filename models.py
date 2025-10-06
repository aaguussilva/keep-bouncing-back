from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

pegue_trick_association = Table(
    "pegue_trick",
    Base.metadata,
    Column("pegue_id", Integer, ForeignKey("pegue.id"), primary_key=True),
    Column("trick_id", Integer, ForeignKey("tricks.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pegues = relationship("Pegue", back_populates="user")
    equipment = relationship("Equipment", secondary="user_equipment", back_populates="users")

class Pegue(Base):
    __tablename__ = "pegue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer)
    notes = Column(Text)

    user = relationship("User", back_populates="pegues")
    tricks = relationship("Trick", secondary=pegue_trick_association, back_populates="pegues")

class Trick(Base):
    __tablename__ = "tricks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

    pegues = relationship("Pegue", secondary=pegue_trick_association, back_populates="tricks")

user_equipment = Table(
    "user_equipment",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id"), primary_key=True)
)

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)

    equipment_obj = relationship("Equipment", back_populates="pegues")
    users = relationship("User", secondary="user_equipment", back_populates="equipment")
    pegues = relationship("Pegue", back_populates="equipment_obj")
