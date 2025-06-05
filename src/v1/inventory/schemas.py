from pydantic import BaseModel, conint
from datetime import datetime
from decimal import Decimal
from entity.schemas import EntityResponse

class EntityData(BaseModel):
    id: int
    name: str
    symbol: str
    image_url: str | None

    class Config:
        orm_mode = True
        from_attributes = True

class InventoryResponse(BaseModel):
    user_id: int
    entity_id: int
    amount: int
    entity: EntityResponse

    class Config:
        orm_mode = True
        from_attributes = True


class InventoryCharge(BaseModel):
    entity_id: int
    amount: conint(gt=0)

    class Config:
        orm_mode = True
        from_attributes = True
