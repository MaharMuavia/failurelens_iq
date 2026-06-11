import pytest

from backend.azure.config import AzureConfig
from backend.azure.grounding_adapter import GroundingAdapter
from backend.api.routes.demo import maybe_upload_report
from backend.core.config import settings


@pytest.mark.anyio
async def test_cosmos_skipped_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_AZURE_TRACE_STORAGE", False)
    adapter = GroundingAdapter(
        AzureConfig(
            app_mode="production",
            azure_cosmos_endpoint="https://cosmos.example.test",
            azure_cosmos_key="key",
            azure_cosmos_database="failurelens",
            azure_cosmos_container="traces",
        )
    )
    result = await adapter.store_reasoning_trace("run-1", {"steps": []})
    assert result["stored"] is False
    assert result["reason"] == "disabled_by_cost_guard"


@pytest.mark.anyio
async def test_cosmos_attempted_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_AZURE_TRACE_STORAGE", True)
    called = {}

    async def fake_store_trace(analysis_id, trace):
        called["analysis_id"] = analysis_id
        return {"stored": True, "analysis_id": analysis_id}

    adapter = GroundingAdapter(
        AzureConfig(
            app_mode="production",
            azure_cosmos_endpoint="https://cosmos.example.test",
            azure_cosmos_key="key",
            azure_cosmos_database="failurelens",
            azure_cosmos_container="traces",
        )
    )
    monkeypatch.setattr(adapter.cosmos_client, "store_trace", fake_store_trace)
    result = await adapter.store_reasoning_trace("run-2", {"steps": []})
    assert result["stored"] is True
    assert called["analysis_id"] == "run-2"
    monkeypatch.setattr(settings, "ENABLE_AZURE_TRACE_STORAGE", False)


@pytest.mark.anyio
async def test_blob_skipped_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_AZURE_REPORT_UPLOAD", False)

    class Blob:
        async def upload_report(self, experiment_id, report_text):
            raise AssertionError("upload should not be called")

    result = await maybe_upload_report(Blob(), "EXP-1", "# Report")
    assert result["uploaded"] is False
    assert result["reason"] == "disabled_by_cost_guard"


@pytest.mark.anyio
async def test_blob_attempted_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_AZURE_REPORT_UPLOAD", True)
    called = {}

    class Blob:
        async def upload_report(self, experiment_id, report_text):
            called["experiment_id"] = experiment_id
            return {"uploaded": True}

    result = await maybe_upload_report(Blob(), "EXP-2", "# Report")
    assert result["uploaded"] is True
    assert called["experiment_id"] == "EXP-2"
    monkeypatch.setattr(settings, "ENABLE_AZURE_REPORT_UPLOAD", False)
