import pytest

from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter


@pytest.mark.anyio
async def test_foundry_iq_local_adapter_retrieves_citations_with_metadata():
    adapter = FoundryIQLocalAdapter()
    sources = adapter.load_knowledge_sources()
    assert isinstance(sources, list)

    result = await adapter.retrieve("evaluation methodology minority f1 remediation", top_k=5)

    assert result["provider"] == "FoundryIQLocalAdapter"
    assert result["mode"] == "local_foundry_iq_adapter"
    assert result["live_azure"] is False
    assert result["adapter_ready"] is True
    assert result["citations"]
    assert result["grounding_context"]
    assert all("permission_scope" in citation for citation in result["citations"])
    assert result.hits


def test_foundry_iq_local_adapter_status_is_adapter_ready():
    status = FoundryIQLocalAdapter().get_status()
    assert status["label"] == "Foundry IQ Local Adapter Mode"
    assert status["foundry_iq_base_architecture"] is True
    assert status["knowledge_sources_configured"] is True

