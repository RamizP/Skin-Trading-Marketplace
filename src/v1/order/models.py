from sqlalchemy import String, Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id =  Column(Integer, nullable=False)
    seller_id =  Column(Integer, nullable=False)
    entity_id =  Column(Integer, nullable=False)
    price =  Column(String(255), nullable=False, unique=True)