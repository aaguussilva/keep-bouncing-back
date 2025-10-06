from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class Trick(Base):
    __tablename__ = "tricks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

    pegues = relationship("Pegue", secondary="pegue_trick", back_populates="tricks")
