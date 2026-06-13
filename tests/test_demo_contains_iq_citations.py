import httpx
import pytest
from backend.api.main import app

@pytest.mark.anyio
async def test_demo_run_contains_iq_citations(monkeypatch):
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
        assert response.status_code == 200
        payload = response.json()
        
        # Assert requested demo fields are present at the top level
        assert "foundry_iq_layer" in payload
        assert "iq_grounding_story" in payload
        assert "citations" in payload
        assert "source_types" in payload
        assert "how_agents_used_knowledge_sources" in payload
    
        # Assert content details inside foundry_iq_layer
        layer = payload["foundry_iq_layer"]
        assert layer["mode"] == "local_foundry_iq_adapter"
        assert layer["citations_count"] >= 0
        assert len(layer["knowledge_sources"]) >= 11  # 5 md files + 6 json experiments
    
        # Assert content details inside iq_grounding_story
        story = payload["iq_grounding_story"]
        assert "how_agents_used_iq" in story
        assert isinstance(payload["citations"], list)
        
        # Check that the source types list is populated
        assert "failure_taxonomy" in payload["source_types"]
        assert "experiment_history" in payload["source_types"]
    
        # Verify agent usage notes dictionary
        usage = payload["how_agents_used_knowledge_sources"]
        assert "ClassifierAgent" in usage
        assert "RootCauseAnalyzerAgent" in usage
        assert "PrescriptiveCoachAgent" in usage
        assert "Uses failure_taxonomy.md" in usage["ClassifierAgent"]
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider
