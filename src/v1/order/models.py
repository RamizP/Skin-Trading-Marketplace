from enum import Enum as PyEnum

from database import Base
from sqlalchemy import Column, DateTime, Enum, Float, Integer
from sqlalchemy.sql import func


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
