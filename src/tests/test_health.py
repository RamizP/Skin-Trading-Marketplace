from fastapi.testclient import TestClient
from src.v1.main import app

client = TestClient(app)


def test_app_is_available():
    response = client.get("/docs")

    assert response.status_code == 200