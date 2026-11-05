from enum import Enum as PyEnum

from database import Base
from sqlalchemy import Column, Enum, Integer, String


class EntityRarity(PyEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHICAL = "mythical"
    LEGENDARY = "legendary"
    EXCEEDINGLY_RARE = "exceedingly_rare"


class Entity(Base):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    symbol = Column(String(255), nullable=False, unique=True)
    image_url = Column(String(512), nullable=True)
    entity_rarity = Column(Enum(EntityRarity), default=EntityRarity.COMMON)
    category_id = Column(Integer, nullable=True)
    sub_category_id = Column(Integer, nullable=True)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)


class SubCategory(Base):
    __tablename__ = "sub_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category_id = Column(Integer, nullable=False)
