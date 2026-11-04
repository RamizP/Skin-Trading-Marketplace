from uuid import uuid4

from fastapi.testclient import TestClient

from src.v1.main import app


client = TestClient(app)


def test_user_can_register():
    unique_id = uuid4().hex

    response = client.post(
        "/register",
        json={
            "username": f"test_user_{unique_id}",
            "password": "StrongPassword123!",
            "email": f"{unique_id}@example.com",
            "bio": "Test user",
            "location": "Berlin",
        },
    )

    assert response.status_code == 200
    assert "token" in response.json()
    assert "Authentication" in response.cookies

def test_no_double_registration():
    unique_id = uuid4().hex

    response = client.post(
        "/register",
        json={
            "username": f"test_user_{unique_id}",
            "password": "StrongPassword123!",
            "email": f"{unique_id}@example.com",
            "bio": "Test user",
            "location": "Berlin",
        },
    )

    response = client.post(
        "/register",
        json={
            "username": f"test_user_{unique_id}",
            "password": "StrongPassword123!",
            "email": f"{unique_id}@example.com",
            "bio": "Test user",
            "location": "Berlin",
        },
    )

    assert response.status_code == 400


def test_registration_rejects_invalid_email():
    response = client.post(
        "/register",
        json={
            "username": "invalid_email_user",
            "password": "StrongPassword123!",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422