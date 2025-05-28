from pydantic import BaseModel, conint
from datetime import datetime
from decimal import Decimal

class InventoryResponse(BaseModel):
    user_id: int
    entity_id: int
    amount: int

    class Config:
        orm_mode = True
        from_attributes=True

class InventoryCharge(BaseModel):
    entity_id: int
    amount: conint(gt=0)

    class Config:
        orm_mode = True
        from_attributes=True