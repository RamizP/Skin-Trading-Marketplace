from pydantic import BaseModel
from datetime import datetime
from order.models import Side

from inventory.schemas import InventoryResponse


class OrderCreate(BaseModel):
    entity_in_inventory_id: int | None = None
    entity_id: int | None = None
    price: float
    side: Side
    class Config:
        orm_mode = True
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    price: float
    side: Side
    inventory: InventoryResponse | None = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class OrderBuy(BaseModel):
    order_id: int


class OrderDelete(BaseModel):
    order_id: int
