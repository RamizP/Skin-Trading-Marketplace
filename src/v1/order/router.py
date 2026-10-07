from typing import List
from sqlalchemy.orm import Session
from Dependencies import get_current_user
from database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException

from order.services import OrderService
from inventory.repository import InventoryRepository
from inventory.services import InventoryService

from auth.schemas import UserResponse
from auth.repository import AuthRepository
from order.schemas import OrderResponse, OrderCreate, OrderBuy, OrderDelete, orders_with_entity
from order.repository import OrderRepository
from entity.repository import EntityRepository

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="OrderService",
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

def get_user_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)

def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

def get_entity_repository(db: Session = Depends(get_db)) -> EntityRepository:
    return EntityRepository(db)

def get_inventory_repository(db: Session = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(db)

def get_inventory_service(repository: InventoryRepository = Depends(get_inventory_repository)) -> InventoryService:
    return InventoryService(repository)

def get_order_service(
        db: Session = Depends(get_db),
        order_repository: OrderRepository = Depends(get_order_repository),
        user_repository: AuthRepository = Depends(get_user_repository),
        entity_repository: EntityRepository = Depends(get_entity_repository),
        inventory_service: InventoryService = Depends(get_inventory_service)
    ) -> OrderService:
    return OrderService(db, order_repository, user_repository, entity_repository, inventory_service)

# /orders               Get all Entities that has a sell order in trading market with it's lowest price
# /orders/{entity_id}   Get all orders for an exact entity but an entity id
# /orders               Create an order (buy or sell)
# /order/buy            Buy an order
# /order                Delete an order

@app.get("/orders")
def get_entities_having_sell_order(
    repository: OrderRepository = Depends(get_order_repository),
):
    orders = repository.get_all_orders_by_lowest_price()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found.")

    response = []

    for entity, price in orders:
        response.append({
            "entity": entity,
            "lowest_price": float(price) if price is not None else None,
        })

    return response

@app.get("/orders/{entity_id}", response_model=List[OrderResponse])
def get_orders_by_entity(entity_id: int, repository: OrderRepository = Depends(get_order_repository)):

    orders = repository.get_orders_by_id(entity_id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this entity.")

    return orders_with_entity(orders)


@app.get("/buy-orders/{entity_id}/me", response_model=List[OrderResponse])
def get_my_buy_orders_by_entity(
    entity_id: int,
    user: UserResponse = Depends(get_current_user),
    repository: OrderRepository = Depends(get_order_repository),
):
    return repository.get_user_buy_orders_by_entity(entity_id, user.id)


@app.get("/buy-orders/{entity_id}/highest", response_model=OrderResponse)
def get_highest_buy_order_by_entity(
    entity_id: int,
    repository: OrderRepository = Depends(get_order_repository),
):
    order = repository.get_highest_buy_orders_by_entity(entity_id)
    if not order:
        raise HTTPException(status_code=404, detail="No orders found for this entity.")
    return order


@app.post("/orders")
def create_order(
    order: OrderCreate,
    user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    return order_service.create_order(order, user)


@app.post("/order/buy", response_model=OrderResponse)
def order_buy(
    order_buy: OrderBuy,
    user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    return order_service.order_buy(order_buy, user, in_transaction=False)


@app.delete("/order")
def order_delete(
    order_delete: OrderDelete,
    user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    return order_service.order_delete(order_delete, user)
