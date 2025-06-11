from pydantic import BaseModel, conint
from datetime import datetime
from decimal import Decimal
from entity.schemas import EntityResponse
from inventory.models import EntityWear

class EntityData(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None

    class Config:
        orm_mode = True
        from_attributes = True

class InventoryResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    entity_wear: EntityWear
    entity: EntityResponse
    in_sale: str

    class Config:
        orm_mode = True
        from_attributes = True


class InventoryCharge(BaseModel):
    entity_id: int
    entity_wear: EntityWear

    class Config:
        orm_mode = True
        from_attributes = True
