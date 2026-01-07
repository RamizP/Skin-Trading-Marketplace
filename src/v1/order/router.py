from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from Dependencies import get_current_user
from database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException

from order.services import OrderService

from order.models import Order
from entity.models import Entity
from inventory.models import UserInventory

from auth.schemas import UserResponse
from entity.schemas import EntityResponse
from inventory.schemas import InventoryResponse
from order.schemas import OrderResponse, OrderCreate, OrderBuy, OrderDelete

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/orders")                 Get all Entities with it's lowest price on the market
# @app.get("/orders/{entity_id}")     Get all oders for an exact entity but an entity id
# @app.post("/orders")                Create an order
# @app.post("/order/buy")             Buy an order
# @app.delete("/order")               Delete an order

@app.get("/orders")
def get_orders(
    db: Session = Depends(get_db)
):
    lowest_price = func.min(Order.price)

    results = (
        db.query(Entity, lowest_price)
        .join(Order, Order.entity_id == Entity.id)
        .group_by(Entity.id)
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="No orders found.")

    response = []
    for entity, price in results:
        response.append({
            "entity": entity,
            "lowest_price": float(price) if price is not None else None,
        })

    return response



@app.get("/orders/{entity_id}", response_model=List[OrderResponse])
def get_orders_by_entity(entity_id: int, db: Session = Depends(get_db)):

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
    order: OrderCreate,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    return OrderService(db).create_order(order, user)


@app.post("/order/buy", response_model=OrderResponse)
def order_buy(
    order_buy: OrderBuy,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    return OrderService(db).order_buy(order_buy, user)


@app.delete("/order")
def order_delete(
    order_delete: OrderDelete,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    return OrderService(db).order_delete(order_delete, user)


def orders_with_entity(orders: List[Order], db: Session) -> List[OrderResponse]:
    return [
        OrderResponse(
            **ord.__dict__,
            inventory=InventoryResponse(
                id=inv.id,
                user_id=inv.user_id,
                entity_id=inv.entity_id,
                entity_wear=inv.entity_wear,
                entity=EntityResponse.model_validate(
                    db.query(Entity).filter(Entity.id == inv.entity_id).first()
                ),
                in_sale=inv.in_sale,
            )
        )
        for ord, inv in orders
    ]