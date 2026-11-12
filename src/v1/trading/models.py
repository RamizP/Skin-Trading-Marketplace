from database import Base
from inventory.models import EntityWear
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TradeHistory(Base):
    __tablename__ = "trade_history"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_trade_history_price_positive"),
        CheckConstraint(
            "seller_id != buyer_id", name="ck_trade_history_different_users"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False)
    entity_wear = Column(Enum(EntityWear), nullable=False)
    item_id = Column(
        Integer,
        ForeignKey("user_inventory.id", ondelete="SET NULL"),
        nullable=True,
    )
    price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
