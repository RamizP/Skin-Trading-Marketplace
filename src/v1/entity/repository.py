from entity.models import Category, Entity, SubCategory
from entity.schemas import EntityCreate
from fastapi import HTTPException


class EntityRepository:
    def __init__(self, db):
        self.db = db

    def create_entity(self, entity: EntityCreate):
        if self.category_validate(entity.category_id, entity.sub_category_id) == False:
            raise HTTPException(status_code=400, detail="Invalid Params")
        db_post = Entity(
            name=entity.name,
            symbol=entity.symbol,
            image_url=entity.image_url,
            entity_rarity=entity.entity_rarity,
            category_id=entity.category_id,
            sub_category_id=entity.sub_category_id,
        )

        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)

        return db_post

    def get_all_entities(self, skip, limit):
        return self.db.query(Entity).offset(skip).limit(limit)

    def get_entity_by_id(self, id):
        entity: Entity = self.db.query(Entity).filter(Entity.id == id).first()
        if not entity:
            raise HTTPException(status_code=400, detail="Entity not exists")
        return entity

    def category_validate(self, category_id: int, sub_category_id: int):
        if (
            category_id != None
            and not self.db.query(Category).filter(Category.id == category_id).first()
        ):
            return False

        if sub_category_id is None:
            return True

        if (
            sub_category_id != None
            and not self.db.query(SubCategory)
            .filter(SubCategory.id == sub_category_id)
            .first()
        ):
            return False

        sub_category = (
            self.db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()
        )

        return sub_category.category_id == category_id
