import enum

from database import Base
from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.sql import func


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class UserStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    password_hashed = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    image_url = Column(String(512), nullable=True)
    bio = Column(String(512), nullable=True)
    location = Column(String(255), nullable=True)
    balance = Column(Numeric(12, 2), nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
