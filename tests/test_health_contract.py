import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_health_contract_has_mode_and_integrations():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_mode"] == "demo"
    assert payload["version"] == "1.0.0"
    assert payload["experiments_loaded"] == 25
    assert payload["knowledge_chunks_indexed"] >= 24
    assert payload["enabled_integrations"]["local_iq"] is True
    assert payload["enabled_integrations"]["azure_openai"] is False
    assert payload["demo_ready"] is True
