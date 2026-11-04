from fastapi.testclient import TestClient

from src.v1.main import app


client = TestClient(app)


def test_logout():
    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"