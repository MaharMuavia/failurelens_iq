from pathlib import Path

from backend.api.main import build_iq_provider, create_app_state_for_tests
from backend.azure.config import AzureConfig
from backend.azure.grounding_adapter import GroundingAdapter
from backend.services.azure_foundry_iq_provider import AzureFoundryIQProvider
from backend.services.knowledge_index import KnowledgeIndex
from backend.services.local_iq_provider import LocalIQProvider


def test_demo_mode_uses_local_iq_provider(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("IQ_PROVIDER", "local")
    state = create_app_state_for_tests()
    assert isinstance(state["iq_provider"], LocalIQProvider)


def test_production_mode_with_azure_foundry_uses_azure_provider(monkeypatch):
    monkeypatch.setenv("APP_MODE", "production")
    monkeypatch.setenv("IQ_PROVIDER", "azure_foundry")
    state = create_app_state_for_tests()
    assert isinstance(state["iq_provider"], AzureFoundryIQProvider)


def test_build_iq_provider_honors_iq_provider_override(monkeypatch):
    monkeypatch.setenv("IQ_PROVIDER", "azure_foundry")
    index = KnowledgeIndex(Path("knowledge/foundry_docs"))
    adapter = GroundingAdapter(AzureConfig(app_mode="demo"), knowledge_index=index)
    provider = build_iq_provider(AzureConfig(app_mode="demo"), adapter, index)
    assert isinstance(provider, AzureFoundryIQProvider)
