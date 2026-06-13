from pathlib import Path

from backend.api.main import build_iq_provider, create_app_state_for_tests
from backend.azure.config import AzureConfig
from backend.azure.grounding_adapter import GroundingAdapter
from backend.services.azure_foundry_iq_provider import AzureFoundryIQProvider
from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter
from backend.services.knowledge_index import KnowledgeIndex


def test_demo_mode_uses_local_iq_provider(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("IQ_PROVIDER", "local")
    
    import backend.core.config
    import backend.api.main
    old_settings = backend.core.config.settings
    old_main_settings = backend.api.main.settings
    new_settings = backend.core.config.Settings.load_from_env()
    backend.core.config.settings = new_settings
    backend.api.main.settings = new_settings
    
    try:
        state = create_app_state_for_tests()
        assert isinstance(state["iq_provider"], FoundryIQLocalAdapter)
    finally:
        backend.core.config.settings = old_settings
        backend.api.main.settings = old_main_settings


def test_production_mode_without_live_azure_uses_local_adapter(monkeypatch):
    monkeypatch.setenv("APP_MODE", "production")
    monkeypatch.setenv("IQ_PROVIDER", "azure_foundry")
    # Make sure we don't have live azure search keys in env during this test
    monkeypatch.delenv("AZURE_AI_SEARCH_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_AI_SEARCH_KEY", raising=False)
    
    import backend.core.config
    import backend.api.main
    old_settings = backend.core.config.settings
    old_main_settings = backend.api.main.settings
    new_settings = backend.core.config.Settings.load_from_env()
    backend.core.config.settings = new_settings
    backend.api.main.settings = new_settings
    
    try:
        state = create_app_state_for_tests()
        assert isinstance(state["iq_provider"], FoundryIQLocalAdapter)
    finally:
        backend.core.config.settings = old_settings
        backend.api.main.settings = old_main_settings


def test_build_iq_provider_uses_azure_only_when_live_requirements_exist(monkeypatch):
    index = KnowledgeIndex(Path("knowledge/foundry_docs"))
    config = AzureConfig(
        app_mode="production",
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_api_key="test",
        azure_openai_deployment="gpt-test",
        azure_ai_search_endpoint="https://example.search.windows.net",
        azure_ai_search_key="test",
        azure_ai_search_index="failurelens",
    )
    adapter = GroundingAdapter(config, knowledge_index=index)
    provider = build_iq_provider(config, adapter, index)
    assert isinstance(provider, AzureFoundryIQProvider)
