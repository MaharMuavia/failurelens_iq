import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_health_contract_has_mode_and_integrations(monkeypatch):
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
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider
