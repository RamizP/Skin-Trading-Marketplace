from uuid import uuid4


def test_user_can_login(client):
    unique_id = uuid4().hex
    username = f"login_user_{unique_id}"
    password = "StrongPassword123!"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "password": password,
            "email": f"{unique_id}@example.com",
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200
    assert "token" in login_response.json()
    assert "Authentication" in login_response.cookies


def test_wrong_password_login(client):
    unique_id = uuid4().hex
    username = f"login_user_{unique_id}"
    password = "StrongPassword123!"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "password": password,
            "email": f"{unique_id}@example.com",
        },
    )

    assert register_response.status_code == 200

    wrong_password = "WrongPassword"

    login_response = client.post(
        "/login",
        json={
            "username": username,
            "password": wrong_password,
        },
    )

    assert login_response.status_code == 401
    assert "token" not in login_response.json()
    assert "Authentication" not in login_response.cookies


def test_login_unknown_user(client):
    response = client.post(
        "/login",
        json={
            "username": "unknown_user",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
