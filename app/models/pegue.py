from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from app.database import Base
from sqlalchemy.orm import relationship

pegue_trick_association = Table(
    "pegue_trick",
    Base.metadata,
    Column("pegue_id", Integer, ForeignKey("pegue.id"), primary_key=True),
    Column("trick_id", Integer, ForeignKey("tricks.id"), primary_key=True)
)

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
