import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_cost_estimate_endpoint_works():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/cost/estimate")
    payload = response.json()
    assert response.status_code == 200
    assert payload["azure_openai"]["cost_guard_enabled"] is True
    assert payload["azure_openai"]["max_tokens_per_demo"] == 500
    assert "Use Azure AI Search Free tier" in payload["recommendations"]
