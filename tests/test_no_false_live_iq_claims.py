import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_mode_has_no_false_live_azure_verified_claim(monkeypatch):
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
            iq_response = await client.get("/iq/status")
            demo_response = await client.post("/demo/run?force_refresh=true")
    
        combined = f"{iq_response.text}\n{demo_response.text}".lower()
        assert "live azure verified" not in combined
        assert "live_microsoft_iq\":true" not in combined
        assert "foundry iq local adapter mode" in combined
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider
