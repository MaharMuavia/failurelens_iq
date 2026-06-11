import pytest
import httpx
from unittest.mock import MagicMock
from backend.api.main import app
from backend.azure.grounding_adapter import GroundingAdapter
from backend.models.schemas import GroundingRef


@pytest.mark.anyio
async def test_health_includes_microsoft_iq_proof_level():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    payload = response.json()
    assert "microsoft_iq" in payload
    assert "proof_level" in payload["microsoft_iq"]
    assert payload["microsoft_iq"]["proof_level"] in {"live_azure", "local_demo_fallback"}


@pytest.mark.anyio
async def test_demo_run_includes_compliance_proof_level():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run")
    payload = response.json()
    assert "microsoft_iq_compliance" in payload
    compliance = payload["microsoft_iq_compliance"]
    assert "proof_level" in compliance
    assert compliance["proof_level"] == "local_demo_fallback"
    assert "honest_limitation" in compliance
    assert "local grounding" in compliance["honest_limitation"].lower()


@pytest.mark.anyio
async def test_mocked_azure_search_uses_correct_source_type(monkeypatch):
    # If search is enabled and is_demo is False, it should use azure_ai_search source type
    async def mock_search(self, query, top_k=3):
        return [
            {
                "source_id": "doc1",
                "title": "Title 1",
                "content": "excerpt text",
                "score": 0.85,
                "url": "https://url.example",
                "citation": "citation 1",
            }
        ]

    monkeypatch.setattr("backend.azure.grounding_adapter.AzureAISearchClient.search", mock_search)
    
    config = MagicMock()
    config.is_demo = False
    config.enabled_integrations = {"azure_ai_search": True}
    
    adapter = GroundingAdapter(config=config)
    
    refs = await adapter.retrieve_experiment_context("EXP-1001")
    assert len(refs) == 1
    assert refs[0].source_type == "azure_ai_search"
    assert refs[0].source_system == "azure_ai_search"
