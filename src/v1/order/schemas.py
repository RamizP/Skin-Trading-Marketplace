from pydantic import BaseModel, validator
from datetime import datetime




class OrderCreate(BaseModel):
    entity_id: int
    price: float
    amount: float = 1

    @validator('amount', pre=True, always=True)
    def force_amount_one(cls, v):
        return 1

    class Config:
        orm_mode = True
        from_attributes=True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    price: float
    amount: float = 1
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

class OrderBuy(BaseModel):
    order_id: int