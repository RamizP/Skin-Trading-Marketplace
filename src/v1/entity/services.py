import os
from fastapi import HTTPException
from entity.schemas import EntityResponse, EntityCreate
from entity.models import Base, Entity
from entity.repository import EntityRepository
from fastapi.responses import JSONResponse


class EntityService:
    def create_entity(entity: EntityCreate, db):
        existing_entity = db.query(Entity).filter(Entity.name == entity.name).first()
        if existing_entity:
            raise HTTPException(status_code=400, detail="Entity already exists")

        entity = EntityRepository.create_entity(entity, db)
        response = JSONResponse(content="true")
        return response
