import os
from fastapi import HTTPException
from inventory.schemas import InventoryResponse, InventoryCharge
from inventory.repository import InventoryRepository
from auth.schemas import UserResponse
from inventory.models import Base, UserInventory


class InventoryService:

    def __init__(self, repository):
        self.inventory_repository: InventoryRepository = repository

    def charge(charge_inventory: InventoryCharge, user: UserResponse, db):
        inventory = InventoryRepository(db).charge_my_inventory(
            charge_inventory, user, db
        )
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found for user")

        return inventory

    def create_inventory_item(self, item, user):
        return self.inventory_repository.create_inventory_item(item, user)

    def get_inventory_item_locked(
        self, inventory_id: int, user_id: int = None
    ):
        # lock the Inventory
        item_from_inventory: UserInventory = self.inventory_repository.lock_inventory_by_id(inventory_id, user_id)

        if not item_from_inventory:
            raise HTTPException(status_code=404, detail="Item not found.")
        return item_from_inventory