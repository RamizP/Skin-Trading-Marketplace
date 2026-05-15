from inventory.schemas import InventoryResponse, InventoryCharge, InventoryItem
from inventory.models import Base, UserInventory
from entity.models import Entity
from auth.schemas import UserResponse
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import HTTPException


class InventoryRepository:

    def __init__(self, db):
        self.db = db

    def get_my_inventory(self, user_id, db: Session):
        return db.query(UserInventory).filter(UserInventory.user_id == user_id).all()

    def charge_my_inventory(
        self, charge_inventory: InventoryCharge, user: UserResponse, db
    ):
        entity = (
            db.query(Entity).filter(Entity.id == charge_inventory.entity_id).first()
        )
        if not entity:
            raise HTTPException(status_code=400, detail="Not existing entity")

        inventory = self.create_inventory(charge_inventory, user)
        db.add(inventory)
        return inventory

    def create_inventory(
        self, charge_inventory: InventoryCharge, user: UserResponse
    ):
        db_post = UserInventory(
            user_id=user.id,
            entity_id=charge_inventory.entity_id,
            entity_wear=charge_inventory.entity_wear
        )
        return db_post

    def create_inventory_item(
        self, inventory_item: InventoryItem, user: UserResponse
    ):
        db_post = UserInventory(
            user_id=user.id,
            entity_id=inventory_item.entity_id,
            entity_wear=inventory_item.entity_wear
        )
        return db_post
