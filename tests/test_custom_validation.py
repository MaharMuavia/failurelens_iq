import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_bad_payload_returns_structured_422(client):
    # Missing required fields like experiment_id, failure_observation, etc.
    payload = {"experiment_id": "BAD-EXP"}
    response = client.post("/analysis/custom", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_experiment_payload"
    assert "details" in data

def test_unknown_experiment_returns_404(client):
    response = client.post("/analysis/run", json={"experiment_id": "EXP-NONEXISTENT"})
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "http_error"
    assert "Unknown experiment_id" in data["detail"]
