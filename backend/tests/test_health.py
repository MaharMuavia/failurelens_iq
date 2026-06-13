from __future__ import annotations

import httpx
import pytest
from backend.app.main import app

@pytest.mark.anyio
async def test_health_endpoint_custom_keys():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "FailureLens IQ API"
    assert "foundry_mode" in data
    assert "credentials_configured" in data
    assert isinstance(data["credentials_configured"], bool)
