import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app

@pytest.fixture
def client():
    app = create_app()
    # Reset/clear cache
    app.state.demo_cache.clear()
    return TestClient(app)

def test_demo_cache_usage_and_refresh(client):
    # First call - cached should be False
    res1 = client.post("/demo/run")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1.get("cached") is False
    
    # Second call - cached should be True
    res2 = client.post("/demo/run")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2.get("cached") is True
    assert "cache_age_seconds" in data2
    
    # Force refresh - cached should be False
    res3 = client.post("/demo/run?force_refresh=true")
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3.get("cached") is False
