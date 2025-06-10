from pydantic import BaseModel
from datetime import datetime
from entity.models import EntityRarity

class EntityResponse(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity

    class Config:
        orm_mode = True
        from_attributes = True


class EntityCreate(BaseModel):
    name: str
    symbol: str
    image_url: str | None = None
    entity_rarity: EntityRarity

    class Config:
        orm_mode = True
        from_attributes = True
