from uuid import uuid4


def test_user_can_register(client):
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


def test_no_double_registration(client):
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


def test_registration_rejects_invalid_email(client):
    response = client.post(
        "/register",
        json={
            "username": "invalid_email_user",
            "password": "StrongPassword123!",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422
