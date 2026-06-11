from fastapi.testclient import TestClient
from backend.api.main import create_app

def test_required_security_headers_exist():
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    
    headers = response.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("referrer-policy") == "no-referrer"
    assert "no-store" in headers.get("cache-control", "")
    assert "content-security-policy" in headers
