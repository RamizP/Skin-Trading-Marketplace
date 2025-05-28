from sqlalchemy import String, Column, Integer, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    user_id =  Column(Integer, nullable=False)
    entity_id =  Column(Integer, nullable=False)
    price =  Column(Float, nullable=False)
    amount =  Column(Float, nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())