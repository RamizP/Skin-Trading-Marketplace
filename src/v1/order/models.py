from sqlalchemy import String, Column, Integer, DateTime, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class Side(PyEnum):
    SELL = "sell"
    BUY = "buy"

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_in_inventory_id = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    side = Column(Enum(Side))
    created_at = Column(DateTime, server_default=func.now())
