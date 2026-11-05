from uuid import uuid4


def test_user_can_get_me(client):
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

    token = register_response.json()["token"]

    response = client.get(
        "/user/me",
        headers={"Authentication": token},
    )

    assert response.status_code == 200
    assert response.json()["username"] == username
    assert response.json()["email"] == f"{unique_id}@example.com"


def test_me_without_token(client):
    response = client.get("/user/me")

    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get(
        "/user/me",
        headers={"Authentication": "invalid-token"},
    )

    assert response.status_code == 401
