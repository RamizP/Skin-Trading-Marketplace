from entity.schemas import EntityResponse
from inventory.models import EntityWear
from pydantic import BaseModel, ConfigDict


class EntityData(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class InventoryResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    entity_wear: EntityWear
    entity: EntityResponse
    in_sale: bool

    model_config = ConfigDict(from_attributes=True)


class InventoryCharge(BaseModel):
    entity_id: int
    entity_wear: EntityWear


class InventoryItem(BaseModel):
    entity_id: int
    entity_wear: EntityWear
