import pytest
import httpx
from backend.api.main import app
from backend.core.config import settings

@pytest.mark.anyio
async def test_iq_status_endpoint_foundry_openai(monkeypatch):
    from backend.azure.config import AzureConfig
    from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

    transport = httpx.ASGITransport(app=app)
    
    orig_provider = settings.MODEL_PROVIDER
    orig_endpoint = settings.FOUNDRY_PROJECT_ENDPOINT
    orig_base_url = settings.FOUNDRY_OPENAI_BASE_URL
    orig_config = app.state.azure_config
    orig_provider_obj = app.state.iq_provider

    monkeypatch.setattr(settings, "APP_MODE", "demo")
    app.state.azure_config = AzureConfig(app_mode="demo")
    app.state.iq_provider = FoundryIQLocalAdapter()
    
    settings.MODEL_PROVIDER = "foundry_openai"
    settings.FOUNDRY_PROJECT_ENDPOINT = "https://test.foundry.azure.com/project"
    settings.FOUNDRY_OPENAI_BASE_URL = "https://test.foundry.azure.com/openai/v1"
    
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/iq/status")
        
        assert response.status_code == 200
        payload = response.json()
        
        assert payload["selected_iq_layer"] == "Foundry IQ"
        assert payload["current_reasoning_provider"] == "MicrosoftFoundryOpenAI"
        assert payload["foundry_project_connected"] is True
        assert payload["live_microsoft_foundry_model"] is True
        assert payload["live_microsoft_iq_grounding"] is False  # Grounding should not be claimed live without search credentials
        assert payload["foundry_iq_adapter_ready"] is True
        assert "Honest Status" in payload.get("honest_limitation", "") or "uses Microsoft Foundry model reasoning" in payload.get("honest_limitation", "")
    finally:
        settings.MODEL_PROVIDER = orig_provider
        settings.FOUNDRY_PROJECT_ENDPOINT = orig_endpoint
        settings.FOUNDRY_OPENAI_BASE_URL = orig_base_url
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider_obj
