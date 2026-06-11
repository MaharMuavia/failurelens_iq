import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.core.config import settings

@pytest.fixture
def rate_limited_client(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_MINUTE", 2)
    app = create_app()
    return TestClient(app)

def test_rate_limiting_triggers_429(rate_limited_client):
    # Perform 2 requests, which should succeed
    response1 = rate_limited_client.get("/experiments")
    assert response1.status_code == 200
    
    response2 = rate_limited_client.get("/experiments")
    assert response2.status_code == 200
    
    # 3rd request should trigger 429
    response3 = rate_limited_client.get("/experiments")
    assert response3.status_code == 429
    assert response3.json()["error"] == "rate_limit_exceeded"
    assert "retry_after_seconds" in response3.json()

def test_health_and_agents_exempt_from_rate_limit(rate_limited_client):
    # Perform many health calls
    for _ in range(5):
        response = rate_limited_client.get("/health")
        assert response.status_code == 200
        
    for _ in range(5):
        response = rate_limited_client.get("/agents")
        assert response.status_code == 200
