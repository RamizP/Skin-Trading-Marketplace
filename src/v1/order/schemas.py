from pydantic import BaseModel, validator
from datetime import datetime

from inventory.schemas import InventoryResponse


class OrderCreate(BaseModel):
    entity_in_inventory_id: int
    price: float
    class Config:
        orm_mode = True
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    price: float
    inventory: InventoryResponse
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class OrderBuy(BaseModel):
    order_id: int


class OrderDelete(BaseModel):
    order_id: int
