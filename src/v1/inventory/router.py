from sqlalchemy import Row, Tuple
from sqlalchemy.orm import Session
from inventory.models import Base, UserInventory
from entity.models import Base, Entity
from inventory.repository import InventoryRepository
from inventory.services import InventoryService
from inventory.utils import InventoryUtils
from auth.services import AuthService
import Exceptions
from Dependencies import is_admin, get_current_user
from inventory.schemas import EntityData, InventoryResponse, InventoryCharge
from entity.schemas import EntityResponse
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)

origins = ["https://car3.rpashaiev.ddev.site"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://car3.rpashaiev.ddev.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/inventory/me", response_model=List[InventoryResponse])
def get_my_inventory(
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):

    inventory_entities = (
        db.query(UserInventory, Entity)
        .join(Entity, UserInventory.entity_id == Entity.id)
        .filter(UserInventory.user_id == user.id)
        .all()
    )
    if inventory_entities is None:
        raise HTTPException(status_code=404, detail="Inventory not found for user")

    return inventory_with_entity(inventory_entities)


@app.post("/inventory/me/charge", response_model=List[InventoryResponse])
def charge_my_inventory(
    charge_inventory: InventoryCharge,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    inventory = InventoryService.charge(charge_inventory, user, db)

    inventory_entities = (
        db.query(UserInventory, Entity)
        .join(Entity, UserInventory.entity_id == Entity.id)
        .filter(UserInventory.user_id == user.id)
        .filter(UserInventory.id == inventory.id)
        .all()
    )
    return inventory_with_entity(inventory_entities)


def inventory_with_entity(inventory) -> List[InventoryResponse]:
    return [
        InventoryResponse(
            id=inv.id,
            user_id=inv.user_id,
            entity_id=inv.entity_id,
            entity_wear=inv.entity_wear,
            in_sale=inv.in_sale,
            entity=EntityResponse.model_validate(ent),
        )
        for inv, ent in inventory
    ]
