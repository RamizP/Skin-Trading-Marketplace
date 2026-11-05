from datetime import datetime
from decimal import Decimal

from entity.schemas import EntityResponse
from inventory.schemas import InventoryResponse
from order.models import Order, Side
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderCreate(BaseModel):
    entity_in_inventory_id: int | None = Field(default=None, gt=0)
    entity_id: int = Field(gt=0)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    side: Side

    @model_validator(mode="after")
    def validate_order_type(self):
        if self.side == Side.SELL and self.entity_in_inventory_id is None:
            raise ValueError("Sell orders require an inventory item.")

        if self.side == Side.BUY and self.entity_in_inventory_id is not None:
            raise ValueError("Buy orders cannot reference an inventory item.")

        return self


class OrderResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    price: Decimal
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
