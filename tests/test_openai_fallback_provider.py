from backend.services.openai_client import OpenAIClient


def test_openai_client_disabled_by_default():
    client = OpenAIClient()
    assert client.enabled is False
import pytest
import httpx
from backend.services.openai_client import OpenAIClient
from backend.core.config import settings

class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload

@pytest.mark.anyio
async def test_openai_client_disabled_by_default():
    # If initialized with empty keys, it is disabled
    client = OpenAIClient(api_key="", model="gpt-4o-mini")
    assert client.enabled is False

@pytest.mark.anyio
async def test_openai_client_enabled_with_key():
    client = OpenAIClient(api_key="sk-testkey123", model="gpt-4o-mini")
    assert client.enabled is True
    assert client.model == "gpt-4o-mini"

@pytest.mark.anyio
async def test_openai_client_chat_completion_raw(monkeypatch):
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
            return FakeResponse(payload={"choices": [{"message": {"content": "{\"root_cause\": \"Test root cause\"}"}}]})

    monkeypatch.setattr("backend.services.openai_client.httpx.AsyncClient", FakeAsyncClient)

    client = OpenAIClient(api_key="sk-testkey123", model="gpt-4o-mini")
    response = await client.chat_completion_raw("System prompt", "User prompt")

    assert response["ok"] is True
    assert "Test root cause" in response["content"]
    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.openai.com/v1/chat/completions"
    assert calls[0]["headers"]["Authorization"] == "Bearer sk-testkey123"
    assert calls[0]["json"]["model"] == "gpt-4o-mini"
