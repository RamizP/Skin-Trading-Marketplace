from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    role: str
    status: str
    image_url: str | None = None
    bio: str | None = None
    location: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None
    bio: str | None = None
    location: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class JwtData(BaseModel):
    sub: str
    exp: datetime
