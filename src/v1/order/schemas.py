from pydantic import BaseModel
from datetime import datetime


# class EntityResponse(BaseModel):
#     id: int
#     name: str
#     symbol: str
#     image_url: str | None = None

#     class Config:
#         orm_mode = True
#         from_attributes=True


# class EntityCreate(BaseModel):
#     name: str
#     symbol: str
#     image_url: str | None = None

#     class Config:
#         orm_mode = True
#         from_attributes=True