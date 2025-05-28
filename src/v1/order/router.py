from sqlalchemy.orm import Session
from order.models import Base, Order
from inventory.models import Base, UserInventory
from order.repository import OrderRepository
from order.services import OrderService
from order.utils import OrderUtils
from order.schemas import OrderResponse, OrderCreate
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

@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    inventory = db.query(UserInventory).filter(UserInventory.entity_id == order.entity_id, UserInventory.user_id == user.id).first()

    try:
        if not inventory or inventory.amount < order.amount or order.amount <= 0:
            db.rollback()
            raise HTTPException(status_code=400, detail="Not enough inventory")

        inventory.amount -= order.amount

        if inventory.amount <= 0:
            db.delete(inventory)

        db_post = Order(
             orderer_id=user.id,
             entity_id=order.entity_id,
             price=order.price,
             amount=order.amount
         )

        db.add(db_post)
        db.commit()
    except:
        db.rollback()
        raise

    response = JSONResponse(content="true")
    return response

@app.get("/orders", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.orderer_id == user.id).all()
    return order