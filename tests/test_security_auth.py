import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.core.config import settings

@pytest.fixture
def auth_disabled_app(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "false")
    monkeypatch.setattr(settings, "ENABLE_AUTH", False)
    app = create_app()
    return app

@pytest.fixture
def auth_enabled_app(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("API_KEY", "secret-test-key")
    monkeypatch.setattr(settings, "ENABLE_AUTH", True)
    monkeypatch.setattr(settings, "API_KEY", "secret-test-key")
    app = create_app()
    return app

def test_auth_disabled_allows_demo(auth_disabled_app):
    client = TestClient(auth_disabled_app)
    response = client.post("/demo/run")
    assert response.status_code == 200

def test_auth_enabled_rejects_missing_key(auth_enabled_app):
    client = TestClient(auth_enabled_app)
    # Mutation endpoint should require API Key
    response = client.post("/demo/run")
    assert response.status_code == 401
    assert "Invalid or missing API Key" in response.json()["detail"]

def test_auth_enabled_accepts_correct_key(auth_enabled_app):
    client = TestClient(auth_enabled_app)
    headers = {"X-API-Key": "secret-test-key"}
    response = client.post("/demo/run", headers=headers)
    assert response.status_code == 200
