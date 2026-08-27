from pydantic import BaseModel
from datetime import datetime
from entity.models import EntityRarity

class EntityResponse(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity
    category_id: int | None = None
    sub_category_id: int | None = None

    class Config:
        orm_mode = True
        from_attributes = True


class EntityCreate(BaseModel):
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity
    category_id: int
    sub_category_id: int | None = None

    class Config:
        orm_mode = True
        from_attributes = True

class CategoryResponce(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class SubCategoryResponce(BaseModel):
    id: int
    name: str
    category_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class SubCategoryCreate(BaseModel):
    name: str
    category_id: int

    class Config:
        orm_mode = True
        from_attributes = True
