from auth.schemas import UserResponse
from database import get_db
from Dependencies import get_current_user
from entity.models import Entity
from entity.schemas import EntityResponse
from fastapi import APIRouter, Depends, HTTPException
from inventory.models import UserInventory
from inventory.schemas import InventoryCharge, InventoryResponse
from inventory.services import InventoryService
from sqlalchemy.orm import Session

router = APIRouter(tags=["Inventory"])


@router.get("/inventory/me", response_model=list[InventoryResponse])
def get_my_inventory(
    db: Session = Depends(get_db), user: UserResponse = Depends(get_current_user)
):
    """
    Get current user inventory.
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


@router.post("/inventory/me/charge", response_model=list[InventoryResponse])
def charge_my_inventory(
    charge_inventory: InventoryCharge,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    """
    Add a skin to the current user inventory.
    """

    inventory = InventoryService.charge(charge_inventory, user, db)
    db.commit()
    inventory_entities = (
        db.query(UserInventory, Entity)
        .join(Entity, UserInventory.entity_id == Entity.id)
        .filter(UserInventory.user_id == user.id)
        .filter(UserInventory.id == inventory.id)
        .all()
    )
    return inventory_with_entity(inventory_entities)


def inventory_with_entity(inventory) -> list[InventoryResponse]:

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
