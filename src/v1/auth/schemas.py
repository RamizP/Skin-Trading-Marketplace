from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    role: str
    status: str
    image_url: str | None = None
    bio: str | None = None
    location: str | None = None
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None
    bio: str | None = None
    location: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class BalanceCharge(BaseModel):
    amount: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class TYPO3Auth(BaseModel):
    token: str


class JwtData(BaseModel):
    sub: str
    exp: datetime
