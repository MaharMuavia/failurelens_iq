import pytest

from backend.azure.blob_client import AzureBlobClient
from backend.azure.config import AzureConfig


@pytest.mark.anyio
async def test_blob_missing_credentials_returns_warning():
    result = await AzureBlobClient(AzureConfig()).upload_report("EXP-1", "# Report")
    assert result["uploaded"] is False
    assert result["reason"] == "credentials_missing"


@pytest.mark.anyio
async def test_blob_upload_report_uses_experiment_scoped_name(monkeypatch):
    captured = {}

    def fake_upload(self, blob_name, content):
        captured["blob_name"] = blob_name
        captured["content"] = content
        return {"url": f"https://blob.example.test/{blob_name}"}

    monkeypatch.setattr(AzureBlobClient, "_upload_blob", fake_upload)
    config = AzureConfig(
        azure_storage_connection_string="UseDevelopmentStorage=true",
        azure_blob_container="reports",
    )
    result = await AzureBlobClient(config).upload_report("EXP-42", "# Markdown")
    assert result["uploaded"] is True
    assert result["blob_name"] == "EXP-42/EXP-42.md"
    assert captured["content"] == "# Markdown"
