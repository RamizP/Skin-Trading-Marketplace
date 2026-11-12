from datetime import datetime
from decimal import Decimal

from inventory.models import EntityWear
from pydantic import BaseModel, ConfigDict, Field


class TradeHistoryAdd(BaseModel):
    seller_id: int = Field(gt=0)
    buyer_id: int = Field(gt=0)
    entity_id: int = Field(gt=0)
    entity_wear: EntityWear
    item_id: int | None = Field(default=None, gt=0)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class TradeHistoryResponse(TradeHistoryAdd):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
