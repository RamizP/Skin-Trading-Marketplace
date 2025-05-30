from sqlalchemy.orm import Session
from entity.models import Base, Entity
from entity.repository import EntityRepository
from entity.services import EntityService
from entity.utils import EntityUtils
import Exceptions
from Dependencies import is_admin, get_current_user
from entity.schemas import EntityResponse, EntityCreate
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    APIRouter,
)
from fastapi.responses import JSONResponse
from typing import List

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)


# List of allowed origins
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specifies allowed origins
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.post("/entities", dependencies=[Depends(is_admin)])
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    return EntityService.create_entity(entity, db)


@app.get("/entities", response_model=List[EntityResponse])
def list_entities(db: Session = Depends(get_db)):
    return EntityRepository.get_all_entities(db)


@app.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity_by_id(entity_id: int, db: Session = Depends(get_db)):
    existing_entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not existing_entity:
        raise HTTPException(status_code=400, detail="Entity not exists")
    return existing_entity
