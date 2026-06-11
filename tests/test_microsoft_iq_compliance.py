import httpx
import pytest

from backend.api.main import app, build_iq_provider
from backend.azure.config import AzureConfig
from backend.services.azure_foundry_iq_provider import AzureFoundryIQProvider
from backend.services.local_iq_provider import LocalIQProvider


@pytest.mark.anyio
async def test_health_includes_microsoft_iq():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    payload = response.json()
    assert payload["microsoft_iq"]["selected_layer"] == "Foundry IQ"
    assert "azure_ai_search_configured" in payload["microsoft_iq"]


@pytest.mark.anyio
async def test_demo_run_includes_microsoft_iq_compliance():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")
    payload = response.json()
    assert payload["microsoft_iq_compliance"]["required_iq_layer"] == "Foundry IQ"
    assert payload["microsoft_iq_compliance"]["implemented"] is True
    assert "source_types" in payload["microsoft_iq_compliance"]["proof"]


def test_provider_selection_demo_and_production():
    assert isinstance(build_iq_provider(AzureConfig(app_mode="demo"), None, object()), LocalIQProvider)
    assert isinstance(build_iq_provider(AzureConfig(app_mode="production"), None, object()), AzureFoundryIQProvider)
