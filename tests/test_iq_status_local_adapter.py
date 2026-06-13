import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_iq_status_in_demo_has_foundry_adapter(monkeypatch):
    from backend.core.config import settings
    from backend.azure.config import AzureConfig
    from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

    orig_mode = settings.APP_MODE
    orig_config = app.state.azure_config
    orig_provider = app.state.iq_provider

    monkeypatch.setattr(settings, "APP_MODE", "demo")
    app.state.azure_config = AzureConfig(app_mode="demo")
    app.state.iq_provider = FoundryIQLocalAdapter()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/iq/status")
        payload = response.json()
        assert payload["selected_iq_layer"] == "Foundry IQ"
        assert payload["current_mode"] == "local_foundry_iq_adapter"
        assert payload["live_microsoft_iq"] is False
        assert payload["adapter_ready"] is True
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider


@pytest.mark.anyio
async def test_iq_status_reports_local_foundry_adapter_mode(monkeypatch):
    from backend.core.config import settings
    from backend.azure.config import AzureConfig
    from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

    orig_mode = settings.APP_MODE
    orig_config = app.state.azure_config
    orig_provider = app.state.iq_provider

    monkeypatch.setattr(settings, "APP_MODE", "demo")
    app.state.azure_config = AzureConfig(app_mode="demo")
    app.state.iq_provider = FoundryIQLocalAdapter()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/iq/status")

        payload = response.json()
        assert payload["selected_iq_layer"] == "Foundry IQ"
        assert payload["current_mode"] == "local_foundry_iq_adapter"
        assert payload["live_microsoft_iq"] is False
        assert payload["adapter_ready"] is True
        assert payload["foundry_iq_base_architecture"] is True
        assert payload["permission_metadata_supported"] is True
        assert payload["agentic_retrieval_supported"] is True
        assert "quota-enabled subscription" in payload["live_azure_requirements"]
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider
