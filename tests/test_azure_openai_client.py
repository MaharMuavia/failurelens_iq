import pytest

from backend.azure.config import AzureConfig
from backend.azure.openai_client import AzureOpenAIClient


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


@pytest.mark.anyio
async def test_missing_azure_openai_returns_deterministic_fallback():
    result = await AzureOpenAIClient(AzureConfig()).summarize("hello")
    assert result["used"] is False
    assert "summary" in result


@pytest.mark.anyio
async def test_configured_azure_openai_calls_correct_url_and_max_tokens(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            return FakeResponse(payload={"choices": [{"message": {"content": '{"executive_summary":"ok","risk_summary":"low","next_best_action":"review","confidence_caveat":"bounded"}'}}]})

    monkeypatch.setattr("backend.azure.openai_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_openai_endpoint="https://openai.example.test",
        azure_openai_api_key="key",
        azure_openai_deployment="gpt-demo",
    )
    result = await AzureOpenAIClient(config).summarize("short prompt")
    assert calls[0]["url"] == "https://openai.example.test/openai/deployments/gpt-demo/chat/completions?api-version=2024-02-15-preview"
    assert calls[0]["json"]["max_tokens"] == 500
    assert result["used"] is True
    assert result["summary"]["executive_summary"] == "ok"


@pytest.mark.anyio
async def test_non_json_model_response_does_not_crash(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            return FakeResponse(payload={"choices": [{"message": {"content": "plain text summary"}}]})

    monkeypatch.setattr("backend.azure.openai_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_openai_endpoint="https://openai.example.test",
        azure_openai_api_key="key",
        azure_openai_deployment="gpt-demo",
    )
    result = await AzureOpenAIClient(config).summarize("short prompt")
    assert result["used"] is True
    assert result["summary"]["raw"] == "plain text summary"
    assert result["summary"]["confidence_caveat"]
