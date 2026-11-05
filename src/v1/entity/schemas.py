from entity.models import EntityRarity
from pydantic import BaseModel, ConfigDict


class EntityResponse(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity
    category_id: int | None = None
    sub_category_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class EntityCreate(BaseModel):
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity
    category_id: int
    sub_category_id: int | None = None


class CategoryResponce(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SubCategoryResponce(BaseModel):
    id: int
    name: str
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str


class SubCategoryCreate(BaseModel):
    name: str
    category_id: int
