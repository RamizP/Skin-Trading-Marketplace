from sqlalchemy.orm import Session
from inventory.models import UserInventory
from entity.models import Entity
from inventory.services import InventoryService
from Dependencies import get_current_user
from inventory.schemas import InventoryResponse, InventoryCharge
from entity.schemas import EntityResponse
from database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Request
from typing import List

from auth.schemas import UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    versmion="1.0.0",
    openapi_url="/custom_openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/inventory/me", response_model=List[InventoryResponse])
def get_my_inventory(
    db: Session = Depends(get_db), user: UserResponse = Depends(get_current_user)
):
    """
    Get current user inventory.

    Args:
        user (UserResponse): Current user.
        db (Session): Database.

    Returns:
        List[InventoryResponse]: Users Inventory.
    """

    inventory_entities = (
        db.query(UserInventory, Entity)
        .join(Entity, UserInventory.entity_id == Entity.id)
        .filter(UserInventory.user_id == user.id)
        .all()
    )
    if not inventory_entities:
        raise HTTPException(status_code=404, detail="Inventory not found for user")

    return inventory_with_entity(inventory_entities)

@app.post("/inventory/me/charge", response_model=List[InventoryResponse])
def charge_my_inventory(
    charge_inventory: InventoryCharge,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    """
    Add a skin to the current user inventory.

    Args:
        charge_inventory (InventoryCharge): Schema.
        user (UserResponse): Current user.
        db (Session): Database.

    Returns:
        List[InventoryResponse]: Users Inventory.
    """

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
