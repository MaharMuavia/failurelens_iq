import pytest

from backend.azure.config import AzureConfig
from backend.azure.cosmos_client import AzureCosmosTraceClient


@pytest.mark.anyio
async def test_cosmos_missing_credentials_returns_reason():
    result = await AzureCosmosTraceClient(AzureConfig()).store_trace("run-1", {"steps": []})
    assert result["stored"] is False
    assert result["reason"] == "credentials_missing"


@pytest.mark.anyio
async def test_cosmos_store_trace_uses_configured_client(monkeypatch):
    captured = {}

    def fake_store(self, document):
        captured.update(document)
        return {"id": document["id"]}

    monkeypatch.setattr(AzureCosmosTraceClient, "_store_document", fake_store)
    config = AzureConfig(
        azure_cosmos_endpoint="https://cosmos.example.test",
        azure_cosmos_key="key",
        azure_cosmos_database="failurelens",
        azure_cosmos_container="traces",
    )
    result = await AzureCosmosTraceClient(config).store_trace("analysis-1", {"confidence": 0.8})
    assert result["stored"] is True
    assert result["database"] == "failurelens"
    assert result["container"] == "traces"
    assert captured["analysis_id"] == "analysis-1"
    assert captured["source"] == "FailureLens IQ"
