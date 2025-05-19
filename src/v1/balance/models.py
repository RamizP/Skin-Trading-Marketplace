from sqlalchemy import Column, ForeignKey, Numeric, UniqueConstraint, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class UserBalance(Base):
    __tablename__ = "user_balance"
    __table_args__ = (UniqueConstraint("user_id", "entity_id", name="uix_user_entity"),)

    # id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("user.id"), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("entity.id"), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Numeric, nullable=False, default=0)

    user = relationship("User", backref="balances")
    entity = relationship("Entity", backref="balances") 