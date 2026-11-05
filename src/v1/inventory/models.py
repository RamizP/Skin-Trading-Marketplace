from enum import Enum as PyEnum

from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
)


class EntityWear(PyEnum):
    NONE = "NONE"
    FACTORY_NEW = "Factory New"
    MINIMAL_WEAR = "Minimal Wear"
    FIELD_TESTED = "Field-Tested"
    WELL_WORN = "Well-Worn"
    BATTLE_SCARRED = "Battle-Scarred"


class UserInventory(Base):
    __tablename__ = "user_inventory"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False)
    entity_wear = Column(Enum(EntityWear), nullable=False, server_default="NONE")
    in_sale = Column(Boolean, default=0)
