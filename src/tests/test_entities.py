from uuid import uuid4

import bcrypt
from fastapi.testclient import TestClient

from src.v1.main import app
from auth.models import User, UserRole
from database import SessionLocal
from entity.models import Category


client = TestClient(app)


def entity_payload():
    unique_id = uuid4().hex

    return {
        "name": f"Test entity {unique_id}",
        "symbol": f"TE_{unique_id[:8]}",
        "entity_rarity": "common",
        "category_id": 1,
    }


def test_list_entities():
    response = client.get("/entities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_unknown_entity():
    response = client.get("/entities/999999999")

    assert response.status_code == 400
    assert response.json()["detail"] == "Entity not exists"


def test_get_entity_with_invalid_id():
    response = client.get("/entities/not-an-id")

    assert response.status_code == 422


def test_create_entity_requires_authentication():
    response = client.post("/entities", json=entity_payload())

    assert response.status_code == 401


def test_admin_can_create_entity():
    unique_id = uuid4().hex
    username = f"admin_{unique_id}"
    password = "AdminPassword123!"

    db = SessionLocal()
    try:
        category = Category(name=f"Test category {unique_id}")
        admin = User(
            username=username,
            email=f"{unique_id}@example.com",
            password_hashed=bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            role=UserRole.admin,
        )

        db.add_all([category, admin])
        db.commit()
        db.refresh(category)
    finally:
        db.close()

    login_response = client.post(
        "/login",
        json={"username": username, "password": password},
    )

    assert login_response.status_code == 200
    token = login_response.json()["token"]

    payload = entity_payload()
    payload["category_id"] = category.id

    response = client.post(
        "/entities",
        json=payload,
        headers={"Authentication": token},
    )

    assert response.status_code == 200
    assert response.json() == "success"
