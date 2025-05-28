from inventory.schemas import InventoryResponse, InventoryCharge
from inventory.models import Base, UserInventory
from entity.models import Entity
from auth.schemas import UserResponse
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import HTTPException

class InventoryRepository:

    def get_my_inventory(self, user_id, db: Session):
        return db.query(UserInventory).filter(UserInventory.user_id == user_id).all()

    def charge_my_inventory(self, charge_inventory: InventoryCharge, user: UserResponse, db):
        inventory = (
            db.query(UserInventory)
            .filter(UserInventory.user_id == user.id, UserInventory.entity_id == charge_inventory.entity_id)
            .first()
        )
        entity = (
            db.query(Entity)
            .filter(Entity.id == charge_inventory.entity_id)
            .first()
            )
        if not entity:
            raise HTTPException(status_code=400, detail="Not existing entity")

        if not inventory:
            inventory = self.create_inventory(charge_inventory, user, db)
        else:
            inventory.amount += charge_inventory.amount
            db.commit()
            db.refresh(inventory)
            return inventory
        return inventory

    def create_inventory(self, charge_inventory: InventoryCharge, user: UserResponse, db):
        db_post = UserInventory(
            user_id=user.id,
            entity_id=charge_inventory.entity_id,
            amount=charge_inventory.amount
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post