from sqlalchemy import Row, Tuple
from sqlalchemy.orm import Session
from order.models import Base, Order
from inventory.models import Base, UserInventory
from entity.models import Base, Entity
from entity.schemas import EntityResponse
from order.repository import OrderRepository
from order.services import OrderService
from order.utils import OrderUtils
from order.schemas import OrderResponse, OrderCreate, OrderBuy, OrderDelete
import Exceptions
from Dependencies import is_admin, get_current_user
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    APIRouter,
)
from fastapi.responses import JSONResponse
from typing import List

from auth.models import User
from auth.schemas import UserResponse
from inventory.schemas import InventoryResponse

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)


# List of allowed origins
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specifies allowed origins
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/orders", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    orders = (
        db.query(Order, UserInventory)
        .join(UserInventory, UserInventory.id == Order.entity_in_inventory_id)
        .filter(Order.user_id == user.id)
        .all()
    )

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user.")

    return orders_with_entity(orders, db)


@app.get("/orders/{entity_id}", response_model=List[OrderResponse])
def get_orders_by_entity(
    entity_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    orders = (
        db.query(Order, UserInventory)
        .join(UserInventory, UserInventory.id == Order.entity_in_inventory_id)
        .filter(Order.entity_id == entity_id)
        .order_by(Order.price.asc())
        .all()
    )

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this entity.")

    return orders_with_entity(orders, db)


@app.post("/orders")
def create_order(
    order: OrderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return OrderService.create_order(order, db, user)


@app.post("/order/buy", response_model=List[OrderResponse])
def order_buy(
    order_buy: OrderBuy, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return OrderService.order_buy(order_buy, db, user)


@app.delete("/order", response_model=List[OrderResponse])
def order_delete(
    order_delete: OrderDelete,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return OrderService.order_delete(order_delete, db, user)


def orders_with_entity(orders, db) -> List[OrderResponse]:
    return [
        OrderResponse(
            **ord.__dict__,
            inventory=InventoryResponse(
                id=inv.id,
                user_id=inv.user_id,
                entity_id=inv.entity_id,
                entity_wear=inv.entity_wear,
                entity=EntityResponse.model_validate(db.query(Entity).filter(Entity.id == inv.entity_id).first()),
                in_sale="false",
            )
        )
        for ord, inv in orders
    ]
