from enum import Enum as PyEnum

from database import Base
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.sql import func


class Side(PyEnum):
    SELL = "sell"
    BUY = "buy"


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_order_price_positive"),
        CheckConstraint(
            "(side = 'SELL' AND entity_in_inventory_id IS NOT NULL) "
            "OR (side = 'BUY' AND entity_in_inventory_id IS NULL)",
            name="ck_order_side_inventory",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False)
    entity_in_inventory_id = Column(
        Integer,
        ForeignKey("user_inventory.id"),
        nullable=True,
    )
    price = Column(Numeric(12, 2), nullable=False)
    side = Column(Enum(Side), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
