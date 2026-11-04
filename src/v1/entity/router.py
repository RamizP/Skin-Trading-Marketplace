from sqlalchemy.orm import Session
from entity.models import Entity, Category, SubCategory
from entity.repository import EntityRepository
from entity.services import EntityService
from Dependencies import is_admin
from entity.schemas import (
    CategoryCreate,
    CategoryResponce,
    EntityResponse,
    EntityCreate,
    SubCategoryCreate,
    SubCategoryResponce,
)
from database import get_db
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from typing import List

router = APIRouter(tags=["Entity"])


@router.post("/entities", dependencies=[Depends(is_admin)])
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    return EntityService.create_entity(entity, db)


@router.get("/entities", response_model=List[EntityResponse])
async def list_entities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return EntityRepository(db).get_all_entities(skip, limit)


@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity_by_id(entity_id: int, db: Session = Depends(get_db)):
    existing_entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not existing_entity:
        raise HTTPException(status_code=400, detail="Entity not exists")
    return existing_entity


@router.post("/category", dependencies=[Depends(is_admin)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category exists")
    db_post = Category(name=category.name)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.post("/sub-category", dependencies=[Depends(is_admin)])
def create_sub_category(sub_category: SubCategoryCreate, db: Session = Depends(get_db)):
    existing_sub_category = db.query(SubCategory).filter(SubCategory.name == sub_category.name).first()
    if existing_sub_category:
        raise HTTPException(status_code=400, detail="SubCategory exists")
    db_post = SubCategory(name=sub_category.name, category_id=sub_category.category_id)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.get("/category", response_model=List[CategoryResponce])
def get_category(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/sub-category", response_model=List[SubCategoryResponce])
def get_sub_category(db: Session = Depends(get_db)):
    return db.query(SubCategory).all()
