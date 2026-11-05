from datetime import datetime

from entity.schemas import EntityResponse
from inventory.schemas import InventoryResponse
from order.models import Order, Side
from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    entity_in_inventory_id: int | None = None
    entity_id: int | None = None
    price: float
    side: Side


class OrderResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    price: float
    side: Side
    inventory: InventoryResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderBuy(BaseModel):
    order_id: int


class OrderDelete(BaseModel):
    order_id: int


# Mapping
def orders_with_entity(orders: list[Order]) -> list[OrderResponse]:
    return [
        OrderResponse(
            **ord.__dict__,
            inventory=InventoryResponse(
                id=inv.id,
                user_id=inv.user_id,
                entity_id=inv.entity_id,
                entity_wear=inv.entity_wear,
                entity=EntityResponse.model_validate(ent),
                in_sale=inv.in_sale,
            ),
        )
        for ord, inv, ent in orders
    ]
