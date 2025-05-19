from sqlalchemy import String, Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Entity(Base):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    symbol = Column(String(255), nullable=False, unique=True)
    image_url = Column(String(512), nullable=True)