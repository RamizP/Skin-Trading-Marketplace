import os
from fastapi import HTTPException
from entity.schemas import EntityResponse, EntityCreate
from entity.models import Base, Entity


class EntityService:
    ...