from entity.schemas import EntityResponse, EntityCreate
from entity.models import Base, Entity
from database import SessionLocal, engine
from sqlalchemy.orm import Session


class EntityRepository:
    def create_entity(entity: EntityCreate, db: Session):
        db_post = Entity(
            name=entity.name, symbol=entity.symbol, image_url=entity.image_url
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        return db_post

    def get_all_entities(db: Session):
        return db.query(Entity).all()
