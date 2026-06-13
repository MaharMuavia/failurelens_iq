import pytest
import httpx
from backend.api.main import app
from backend.core.config import settings

@pytest.mark.anyio
async def test_demo_run_includes_foundry_proofs():
    transport = httpx.ASGITransport(app=app)
    
    orig_provider = settings.MODEL_PROVIDER
    orig_endpoint = settings.FOUNDRY_PROJECT_ENDPOINT
    orig_base_url = settings.FOUNDRY_OPENAI_BASE_URL
    
    # Configure mock settings so that proofs can be populated
    settings.MODEL_PROVIDER = "foundry_openai"
    settings.FOUNDRY_PROJECT_ENDPOINT = "https://test.foundry.azure.com/project"
    settings.FOUNDRY_OPENAI_BASE_URL = "https://test.foundry.azure.com/openai/v1"
    
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/demo/run?force_refresh=true")
        
        assert response.status_code == 200
        payload = response.json()
        
        assert "real_model_reasoning" in payload
        assert "foundry_model_proof" in payload
        assert "microsoft_iq_compliance" in payload
        
        # Verify compliance block properties
        compliance = payload["microsoft_iq_compliance"]
        assert compliance["selected_iq_layer"] == "Foundry IQ"
        assert isinstance(compliance["live_microsoft_foundry_model"], bool)
        assert isinstance(compliance["live_microsoft_iq_grounding"], bool)
        assert compliance["foundry_iq_adapter_ready"] is True
    finally:
        settings.MODEL_PROVIDER = orig_provider
        settings.FOUNDRY_PROJECT_ENDPOINT = orig_endpoint
        settings.FOUNDRY_OPENAI_BASE_URL = orig_base_url
