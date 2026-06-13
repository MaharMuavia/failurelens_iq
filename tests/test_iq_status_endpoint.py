import httpx
import pytest

from backend.api.main import app
from backend.core.config import settings
from backend.services.azure_foundry_iq_provider import AzureFoundryIQProvider


@pytest.mark.anyio
async def test_iq_status_demo_mode_returns_local_fallback(monkeypatch):
    from backend.azure.config import AzureConfig
    from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

    original_mode = settings.APP_MODE
    original_config = app.state.azure_config
    original_provider = app.state.iq_provider

    monkeypatch.setattr(settings, "APP_MODE", "demo")
    app.state.azure_config = AzureConfig(app_mode="demo")
    app.state.iq_provider = FoundryIQLocalAdapter()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/iq/status")
    finally:
        monkeypatch.setattr(settings, "APP_MODE", original_mode)
        app.state.azure_config = original_config
        app.state.iq_provider = original_provider

    payload = response.json()
    assert payload["required_by_hackathon"] is True
    assert payload["selected_iq_layer"] == "Foundry IQ"
    assert payload["proof_level"] == "local_foundry_iq_adapter"
    assert payload["compliance_status"] == "ready_for_demo"
    assert "Azure AI Search is not live" in payload["honest_limitation"]


@pytest.mark.anyio
async def test_iq_status_production_with_mocked_azure_search_requires_proof_run():
    original_mode = settings.APP_MODE
    original_config = app.state.azure_config
    original_provider = app.state.iq_provider

    class MockAzureConfig:
        enabled_integrations = {
            "local_iq": True,
            "azure_ai_search": True,
            "azure_openai": True,
            "azure_cosmos_db": False,
            "azure_blob_storage": False,
        }

    settings.APP_MODE = "production"
    app.state.azure_config = MockAzureConfig()
    app.state.iq_provider = AzureFoundryIQProvider(app.state.grounding_adapter)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/iq/status")
    finally:
        settings.APP_MODE = original_mode
        app.state.azure_config = original_config
        app.state.iq_provider = original_provider

    payload = response.json()
    assert payload["proof_level"] == "configuration_ready_requires_run"
    assert payload["compliance_status"] == "configured_requires_proof_run"
    assert payload["live_microsoft_iq"] is False
    assert payload["live_services"]["azure_ai_search_configured"] is True
    assert payload["live_services"]["azure_ai_search_used_this_run"] is False
    assert payload["active_provider"] == "AzureFoundryIQProvider"
