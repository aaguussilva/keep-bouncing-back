from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

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

    users = relationship("User", secondary="user_equipment", back_populates="equipment")
