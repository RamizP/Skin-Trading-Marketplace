import os
from fastapi import HTTPException
# from order.schemas import OrderResponse, OrderCreate
from order.models import Base, Order


class OrderService:
    ...