import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from backend.services.foundry_openai_client import FoundryOpenAIClient

TEST_FOUNDRY_DEPLOYMENT = "test-foundry-deployment"

@pytest.mark.anyio
async def test_foundry_openai_client_success():
    client = FoundryOpenAIClient(
        base_url="https://test.foundry.azure.com/openai/v1",
        api_key="secret-key-1234",
        deployment=TEST_FOUNDRY_DEPLOYMENT
    )
    
    assert client.enabled is True
    
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "{\n  \"root_cause\": \"test cause\"\n}"
                }
            }
        ]
    }
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = payload
    
    mock_post = AsyncMock(return_value=mock_response)
    
    with patch("httpx.AsyncClient.post", mock_post):
        response = await client.chat_completion_raw(
            system_prompt="System instructions",
            user_prompt="User query"
        )
        
        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer secret-key-1234"
        assert kwargs["json"]["model"] == TEST_FOUNDRY_DEPLOYMENT
        
        assert response["ok"] is True
        assert response["provider"] == "MicrosoftFoundryOpenAI"
        assert response["model"] == TEST_FOUNDRY_DEPLOYMENT
        assert "test cause" in response["content"]

@pytest.mark.anyio
async def test_foundry_openai_client_failures():
    client = FoundryOpenAIClient(
        base_url="https://test.foundry.azure.com/openai/v1",
        api_key="secret-key-1234",
        deployment=TEST_FOUNDRY_DEPLOYMENT
    )
    
    # Auth Failure (401)
    mock_resp_401 = MagicMock(spec=httpx.Response)
    mock_resp_401.status_code = 401
    mock_post_401 = AsyncMock(return_value=mock_resp_401)
    with patch("httpx.AsyncClient.post", mock_post_401):
        res = await client.chat_completion_raw("sys", "user")
        assert res["ok"] is False
        assert "auth failure" in res["detail"]
        assert "secret-key" not in res["detail"]
    
    # Not Found (404)
    mock_resp_404 = MagicMock(spec=httpx.Response)
    mock_resp_404.status_code = 404
    mock_post_404 = AsyncMock(return_value=mock_resp_404)
    with patch("httpx.AsyncClient.post", mock_post_404):
        res = await client.chat_completion_raw("sys", "user")
        assert res["ok"] is False
        assert "404" in res["detail"]
    
    # Rate Limit (429)
    mock_resp_429 = MagicMock(spec=httpx.Response)
    mock_resp_429.status_code = 429
    mock_post_429 = AsyncMock(return_value=mock_resp_429)
    with patch("httpx.AsyncClient.post", mock_post_429):
        res = await client.chat_completion_raw("sys", "user")
        assert res["ok"] is False
        assert "429" in res["detail"]

