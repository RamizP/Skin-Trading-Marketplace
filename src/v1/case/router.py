from fastapi import APIRouter, Depends, HTTPException

from case.services import CaseService
from case.models import CaseDrop
from case.schemas import CaseDropResponse, CaseDropAdd, CaseDropWithEntityResponse

from entity.schemas import EntityResponse
from entity.models import Entity, Category

from inventory.schemas import InventoryItem
from inventory.repository import InventoryRepository
from inventory.services import InventoryService

from auth.schemas import UserResponse

from database import get_db
from sqlalchemy.orm import Session
from typing import List
from Dependencies import is_admin, get_current_user

router = APIRouter(prefix="/cases", tags=["Case"])

def get_inventory_repository(db: Session = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(db)
def get_inventory_service(repository: InventoryRepository = Depends(get_inventory_repository)) -> InventoryService:
    return InventoryService(repository)

def get_case_service(db: Session = Depends(get_db), user: UserResponse = Depends(get_current_user), inventory_service: InventoryService = Depends(get_inventory_service)) -> CaseService:
    return CaseService(db, user, inventory_service)

def get_public_case_service(
    db: Session = Depends(get_db),
) -> CaseService:
    return CaseService(db)


@router.post("/{case_in_inventory_id}/open", response_model=InventoryItem)
def open_case(case_in_inventory_id: int, case_service: CaseService = Depends(get_case_service)):
    return case_service.open_case(case_in_inventory_id)


@router.post("/drops", dependencies=[Depends(is_admin)])
def add_entity_into_case(case_drop: CaseDropAdd, db: Session = Depends(get_db)):
    existing_drop = db.query(CaseDrop).filter(CaseDrop.reward_entity_id == case_drop.reward_entity_id, CaseDrop.case_entity_id == case_drop.case_entity_id).first()
    if existing_drop:
        raise HTTPException(status_code=400, detail="Drop exists")

    case_entity = db.get(Entity, case_drop.case_entity_id)
    if not case_entity:
        raise HTTPException(
            status_code=404,
            detail="Case entity not found",
        )

    reward_entity = db.get(Entity, case_drop.reward_entity_id)
    if not reward_entity:
        raise HTTPException(
            status_code=404,
            detail="Reward entity not found",
        )

    if case_entity.id == reward_entity.id:
        raise HTTPException(
            status_code=400,
            detail="Case cannot contain itself",
        )

    case_category = (
        db.query(Category)
        .filter(Category.name == "case")
        .first()
    )

    if not case_category or case_entity.category_id != case_category.id:
        raise HTTPException(
            status_code=400,
            detail="Entity is not a case",
        )

    if reward_entity.category_id==case_category.id:
        raise HTTPException(
            status_code=400,
            detail="Reward cannot be a case",
        )


    db_post = CaseDrop(case_entity_id = case_drop.case_entity_id, reward_entity_id = case_drop.reward_entity_id, weight = case_drop.weight)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post

@router.get("/{case_id}/drops", response_model=List[CaseDropWithEntityResponse])
def get_case_drops(case_id: int, db: Session = Depends(get_db), case_service: CaseService = Depends(get_public_case_service)):
    case_drops = case_service.get_case_drops_with_entities(case_id)
    return validate_drops_with_entity(case_drops)

def validate_drops_with_entity(case_drops) -> List[CaseDropWithEntityResponse]:

    return [
        CaseDropWithEntityResponse(
            id=drop.id,
            case_entity_id=drop.case_entity_id,
            reward_entity_id=drop.reward_entity_id,
            weight=drop.weight,
            entity=EntityResponse.model_validate(ent),
        )
        for drop, ent in case_drops
    ]
