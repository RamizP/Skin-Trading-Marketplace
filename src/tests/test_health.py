def test_app_is_available(client):
    response = client.get("/docs")

    assert response.status_code == 200
