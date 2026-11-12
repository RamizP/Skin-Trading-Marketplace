from decimal import Decimal
from uuid import uuid4

import bcrypt
import pytest
from auth.models import User, UserRole
from database import Base, get_db
from entity.models import Entity, EntityRarity
from fastapi.testclient import TestClient
from inventory.models import EntityWear, UserInventory
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.v1.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def override_database_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_test_database(override_database_dependency, monkeypatch):
    monkeypatch.setenv("DEMO_DATA", "false")
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(clean_test_database):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(clean_test_database):
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_factory(db_session):
    def create_user(*, balance="0.00", role=UserRole.user):
        unique_id = uuid4().hex
        user = User(
            username=f"user_{unique_id}",
            email=f"{unique_id}@example.com",
            password_hashed=bcrypt.hashpw(
                b"TestPassword123!", bcrypt.gensalt()
            ).decode(),
            balance=Decimal(balance),
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def entity_factory(db_session):
    def create_entity(*, category_id=None):
        unique_id = uuid4().hex
        entity = Entity(
            name=f"Test item {unique_id}",
            symbol=f"ITEM_{unique_id[:8]}",
            entity_rarity=EntityRarity.COMMON,
            category_id=category_id,
        )
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)
        return entity

    return create_entity


@pytest.fixture
def inventory_factory(db_session):
    def create_inventory(user, entity, *, wear=EntityWear.NONE):
        item = UserInventory(
            user_id=user.id,
            entity_id=entity.id,
            entity_wear=wear,
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    return create_inventory


@pytest.fixture
def auth_headers(client):
    def login(user):
        response = client.post(
            "/login",
            json={"username": user.username, "password": "TestPassword123!"},
        )
        assert response.status_code == 200, response.text
        return {"Authentication": response.json()["token"]}

    return login
