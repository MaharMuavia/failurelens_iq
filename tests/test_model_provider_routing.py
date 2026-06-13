import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.llm_reasoning_provider import LLMReasoningProvider
from backend.services.foundry_openai_client import FoundryOpenAIClient
from backend.services.foundry_agent_client import FoundryAgentClient
from backend.azure.openai_client import AzureOpenAIClient
from backend.services.openai_client import OpenAIClient
from backend.core.config import settings

@pytest.mark.anyio
async def test_provider_routing_foundry_openai(monkeypatch):
    original_provider = settings.MODEL_PROVIDER
    settings.MODEL_PROVIDER = "foundry_openai"
    
    mock_foundry_openai = MagicMock(spec=FoundryOpenAIClient)
    mock_foundry_openai.enabled = True
    
    provider = LLMReasoningProvider(
        azure_openai_client=MagicMock(spec=AzureOpenAIClient),
        openai_client=MagicMock(spec=OpenAIClient),
        foundry_openai_client=mock_foundry_openai,
        foundry_agent_client=MagicMock(spec=FoundryAgentClient)
    )
    
    client, provider_name, provider_label = provider._select_client()
    try:
        assert client == mock_foundry_openai
        assert provider_name == "MicrosoftFoundryOpenAI"
        assert provider_label == "Microsoft Foundry OpenAI"
    finally:
        settings.MODEL_PROVIDER = original_provider

@pytest.mark.anyio
async def test_provider_routing_foundry_agent_fallback_to_openai(monkeypatch):
    original_provider = settings.MODEL_PROVIDER
    settings.MODEL_PROVIDER = "foundry_agent"
    
    mock_foundry_openai = MagicMock(spec=FoundryOpenAIClient)
    mock_foundry_openai.enabled = True
    
    # Agent client is not enabled (missing configuration)
    mock_foundry_agent = MagicMock(spec=FoundryAgentClient)
    mock_foundry_agent.enabled = False
    
    provider = LLMReasoningProvider(
        azure_openai_client=MagicMock(spec=AzureOpenAIClient),
        openai_client=MagicMock(spec=OpenAIClient),
        foundry_openai_client=mock_foundry_openai,
        foundry_agent_client=mock_foundry_agent
    )
    
    client, provider_name, provider_label = provider._select_client()
    try:
        # Should fallback to foundry_openai since agent client is not configured
        assert client == mock_foundry_openai
        assert provider_name == "MicrosoftFoundryOpenAI"
        assert provider_label == "Microsoft Foundry OpenAI"
    finally:
        settings.MODEL_PROVIDER = original_provider
