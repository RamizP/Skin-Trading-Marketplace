import os
from fastapi import HTTPException
from inventory.schemas import InventoryResponse, InventoryCharge
from inventory.repository import InventoryRepository
from auth.schemas import UserResponse
from inventory.models import Base, UserInventory


class InventoryService:
    def charge(charge_inventory: InventoryCharge, user: UserResponse, db):
        inventory = InventoryRepository().charge_my_inventory(
            charge_inventory, user, db
        )
        if inventory is None:
            raise HTTPException(status_code=404, detail="Inventory not found for user")

        return inventory
