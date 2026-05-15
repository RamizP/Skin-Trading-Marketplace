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
from database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
)
from typing import List

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["DELETE, POST, GET, OPTIONS"],  # or list your actual methods
    allow_headers=["Content-Type, Authorization, X-Requested-With"],
)


@app.post("/entities", dependencies=[Depends(is_admin)])
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    return EntityService.create_entity(entity, db)


@app.get("/entities", response_model=List[EntityResponse])
async def list_entities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return EntityRepository(db).get_all_entities(skip, limit)


@app.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity_by_id(entity_id: int, db: Session = Depends(get_db)):
    existing_entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not existing_entity:
        raise HTTPException(status_code=400, detail="Entity not exists")
    return existing_entity


@app.post("/category", dependencies=[Depends(is_admin)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_post = Category(name=category.name)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.post("/sub-category", dependencies=[Depends(is_admin)])
def create_sub_category(sub_category: SubCategoryCreate, db: Session = Depends(get_db)):
    db_post = SubCategory(name=sub_category.name, category_id=sub_category.category_id)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.get("/category", response_model=List[CategoryResponce])
def get_category(db: Session = Depends(get_db)):
    return db.query(Category).all()


@app.get("/sub-category", response_model=List[SubCategoryResponce])
def get_sub_category(db: Session = Depends(get_db)):
    return db.query(SubCategory).all()
