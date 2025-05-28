import os
from fastapi import HTTPException
from inventory.schemas import InventoryResponse, InventoryCharge
from inventory.repository import InventoryRepository
from auth.schemas import UserResponse
from inventory.models import Base, UserInventory


class InventoryService:
    def charge(charge_inventory: InventoryCharge, user: UserResponse, db):
        return InventoryRepository().charge_my_inventory(charge_inventory, user, db)