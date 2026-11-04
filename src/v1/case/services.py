from sqlalchemy import func, select
from entity.models import Entity
from case.models import CaseDrop
from case.schemas import CaseDropResponse
from auth.schemas import UserResponse
from inventory.schemas import InventoryCharge
from inventory.models import EntityWear
from inventory.services import InventoryService
import random
from fastapi import FastAPI, HTTPException


class CaseService:
    def __init__(self, db, user = None, inventory_service = None):
        self.db = db
        self.user: UserResponse = user
        self.inventory_service: InventoryService = inventory_service

    def open_case(self, case_in_inventory_id):
        try:
            inventory_item = self.inventory_service.get_inventory_item_locked(
                case_in_inventory_id, self.user.id
            )

            if inventory_item.in_sale:
                raise HTTPException(status_code=400, detail="Case is listed for sale")
            case_drops = self.get_case_drops(inventory_item.entity_id)

            if not case_drops:
                raise HTTPException(
                    status_code=400,
                    detail="Case has no drops",
                )

            random_drop = self.get_random_entity_id(case_drops)

            random_wear = self.get_random_wear()

            item_to_add = InventoryCharge(entity_id=random_drop, entity_wear=random_wear)

            reward = InventoryService.charge(item_to_add, self.user, self.db)

            self.db.delete(inventory_item)
            self.db.commit()

            return reward


        except Exception as e:
            self.db.rollback()
            raise

    def get_random_entity_id(self, case_drops):
        random_drop = random.choices(
            case_drops, weights=[drop.weight for drop in case_drops], k=1
        )[0]
        return random_drop.reward_entity_id

    def get_random_wear(self):
        random_wear = random.choice(list(EntityWear)[1:])
        return random_wear

    def get_case_drops(self, case_id):
        case_drops = (
            self.db.query(CaseDrop).filter(CaseDrop.case_entity_id == case_id).all()
        )
        return case_drops

    def get_case_drops_with_entities(self, case_id):
        case_drops = (
            self.db.query(CaseDrop, Entity)
            .join(Entity, CaseDrop.reward_entity_id == Entity.id)
            .filter(CaseDrop.case_entity_id == case_id)
            .all()
        )
        return case_drops
