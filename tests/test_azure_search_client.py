import pytest

from backend.azure.ai_search_client import AzureAISearchClient
from backend.azure.config import AzureConfig


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


@pytest.mark.anyio
async def test_missing_credentials_returns_warning():
    client = AzureAISearchClient(AzureConfig())
    result = await client.search("minority f1")
    assert result[0]["reason"] == "credentials_missing"
    assert "warning" in result[0]


@pytest.mark.anyio
async def test_configured_credentials_call_correct_url(monkeypatch):
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
            return FakeResponse(
                payload={
                    "value": [
                        {
                            "id": "doc-1",
                            "title": "Validation guidance",
                            "content": "Use stratified validation for imbalanced labels.",
                            "@search.score": 0.85,
                            "url": "https://example.test/doc-1",
                        }
                    ]
                }
            )

    monkeypatch.setattr("backend.azure.ai_search_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_ai_search_endpoint="https://search.example.test",
        azure_ai_search_key="key",
        azure_ai_search_index="failure index",
    )
    result = await AzureAISearchClient(config).search("validation", top_k=2)
    assert calls[0]["url"] == "https://search.example.test/indexes/failure%20index/docs/search?api-version=2023-11-01"
    assert calls[0]["headers"]["api-key"] == "key"
    assert calls[0]["json"]["queryType"] == "semantic"
    assert result[0]["source_id"] == "doc-1"
    assert result[0]["score"] == 0.85


@pytest.mark.anyio
async def test_failed_semantic_query_falls_back_to_simple_query(monkeypatch):
    calls = []
    responses = [
        FakeResponse(status_code=400, text="semantic configuration missing"),
        FakeResponse(payload={"value": [{"id": "doc-2", "content": "Simple search result", "@search.score": 0.7}]}),
    ]

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            calls.append(json)
            return responses.pop(0)

    monkeypatch.setattr("backend.azure.ai_search_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_ai_search_endpoint="https://search.example.test",
        azure_ai_search_key="key",
        azure_ai_search_index="idx",
    )
    result = await AzureAISearchClient(config).search("validation", top_k=3)
    assert calls[0]["queryType"] == "semantic"
    assert "queryType" not in calls[1]
    assert result[0]["source_id"] == "doc-2"
    assert "fallback was used" in result[0]["warning"]


@pytest.mark.anyio
async def test_simple_search_failure_returns_warning(monkeypatch):
    responses = [
        FakeResponse(status_code=400, text="semantic configuration missing"),
        FakeResponse(status_code=403, text="forbidden"),
    ]

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            return responses.pop(0)

    monkeypatch.setattr("backend.azure.ai_search_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_ai_search_endpoint="https://search.example.test",
        azure_ai_search_key="key",
        azure_ai_search_index="idx",
    )
    result = await AzureAISearchClient(config).search("validation")
    assert "request failed" in result[0]["warning"]
    assert result[0]["status_code"] == 403


@pytest.mark.anyio
async def test_normalized_result_includes_citation_and_top_k_is_clamped(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            calls.append(json)
            return FakeResponse(
                payload={
                    "value": [
                        {
                            "id": "doc-3",
                            "title": "Cited guidance",
                            "content": "Cited content",
                            "citation": "docs/source.md#chunk-1",
                            "@search.score": 0.8,
                        }
                    ]
                }
            )

    monkeypatch.setattr("backend.azure.ai_search_client.httpx.AsyncClient", FakeAsyncClient)
    config = AzureConfig(
        azure_ai_search_endpoint="https://search.example.test",
        azure_ai_search_key="key",
        azure_ai_search_index="idx",
    )
    result = await AzureAISearchClient(config).search("validation", top_k=99)
    assert calls[0]["top"] == 5
    assert result[0]["citation"] == "docs/source.md#chunk-1"
