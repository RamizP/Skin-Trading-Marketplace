from typing import Annotated

from entity.schemas import EntityResponse
from pydantic import BaseModel, Field


class CaseDropResponse(BaseModel):
    id: int
    case_entity_id: int
    reward_entity_id: int
    weight: int

    class Config:
        orm_mode = True
        from_attributes = True


class CaseDropWithEntityResponse(CaseDropResponse):
    entity: EntityResponse

    class Config:
        orm_mode = True
        from_attributes = True


class CaseDropAdd(BaseModel):
    case_entity_id: int
    reward_entity_id: int
    weight: Annotated[int, Field(gt=0)]

    class Config:
        orm_mode = True
        from_attributes = True
