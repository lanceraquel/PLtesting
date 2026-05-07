from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_renders():
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "SI Research Agent" in response.text
    assert "Create Research Task" in response.text
    assert "Run interval" in response.text
