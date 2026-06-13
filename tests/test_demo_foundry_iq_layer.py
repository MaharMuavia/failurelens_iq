import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_run_includes_foundry_iq_layer_and_story(monkeypatch):
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
            response = await client.post("/demo/run?force_refresh=true")
    
        payload = response.json()
        layer = payload["foundry_iq_layer"]
        story = payload["iq_grounding_story"]
    
        assert layer["mode"] == "local_foundry_iq_adapter"
        assert layer["selected_iq_layer"] == "Foundry IQ"
        assert layer["live_azure"] is False
        assert layer["adapter_ready"] is True
        assert layer["citations_count"] >= 5
        assert layer["permission_aware_metadata"] is True
        assert story["citations"]
        assert story["retrieved_evidence"]
        assert "Classifier used taxonomy evidence" in story["how_agents_used_iq"]
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider

