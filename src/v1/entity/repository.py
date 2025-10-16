from fastapi import HTTPException
from entity.schemas import EntityResponse, EntityCreate
from entity.models import Base, Entity, Category, SubCategory
from database import SessionLocal, engine
from sqlalchemy.orm import Session


class EntityRepository:

    def create_entity(entity: EntityCreate, db: Session):
        if EntityRepository.category_validate(entity.category_id, entity.sub_category_id, db) == False:
            raise HTTPException(status_code=400, detail="Invalid Params")
        db_post = Entity(
            name=entity.name,
            symbol=entity.symbol,
            image_url=entity.image_url,
            entity_rarity=entity.entity_rarity,
            category_id=entity.category_id,
            sub_category_id=entity.sub_category_id
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        return db_post

    def get_all_entities(db: Session, skip, limit):
        return db.query(Entity).offset(skip).limit(limit)

    def category_validate(category_id: int, sub_category_id: int, db):
        if (category_id != None and not db.query(Category).filter(Category.id == category_id).first()):
            return False
        if (sub_category_id != None and not db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()):
            return False

        sub_category = db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()

        if sub_category.category_id != category_id:
            return False
        return True