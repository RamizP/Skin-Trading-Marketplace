from typing import Annotated

from entity.schemas import EntityResponse
from pydantic import BaseModel, ConfigDict, Field


class CaseDropResponse(BaseModel):
    id: int
    case_entity_id: int
    reward_entity_id: int
    weight: int

    model_config = ConfigDict(from_attributes=True)


class CaseDropWithEntityResponse(CaseDropResponse):
    entity: EntityResponse


class CaseDropAdd(BaseModel):
    case_entity_id: int
    reward_entity_id: int
    weight: Annotated[int, Field(gt=0)]
