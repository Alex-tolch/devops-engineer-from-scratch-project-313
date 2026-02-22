from main import app


def test_ping_returns_pong():
    client = app.test_client()
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data.decode() == "pong"
