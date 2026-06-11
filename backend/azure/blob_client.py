from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import PurePosixPath

from backend.azure.config import AzureConfig


class AzureBlobClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_blob_storage"]

    async def get_artifact_context(self, experiment_id: str) -> list[dict[str, object]]:
        if not self.enabled:
            return [{"warning": "Azure Blob Storage credentials are not configured; local artifacts are used instead."}]
        return [{"experiment_id": experiment_id, "container": self.config.azure_blob_container, "status": "configured"}]

    async def upload_text_artifact(self, experiment_id: str, filename: str, content: str) -> dict[str, object]:
        if not self.enabled:
            return {
                "uploaded": False,
                "reason": "credentials_missing",
                "warning": "Azure Blob Storage credentials are not configured; local artifacts are used instead.",
            }
        blob_name = str(PurePosixPath(experiment_id) / filename)
        try:
            result = await asyncio.to_thread(self._upload_blob, blob_name, content)
        except Exception as exc:
            return {"uploaded": False, "reason": "blob_error", "detail": str(exc)[:500], "blob_name": blob_name}
        return {
            "uploaded": True,
            "blob_name": blob_name,
            "url": result["url"],
            "container": self.config.azure_blob_container,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def upload_report(self, experiment_id: str, markdown_report: str) -> dict[str, object]:
        return await self.upload_text_artifact(experiment_id, f"{experiment_id}.md", markdown_report)

    def _upload_blob(self, blob_name: str, content: str) -> dict[str, str]:
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError as exc:
            raise RuntimeError("azure-storage-blob is not installed. Run pip install -r requirements.txt.") from exc

        service = BlobServiceClient.from_connection_string(self.config.azure_storage_connection_string)
        blob_client = service.get_blob_client(container=self.config.azure_blob_container, blob=blob_name)
        blob_client.upload_blob(content, overwrite=True, content_type="text/markdown; charset=utf-8")
        return {"url": blob_client.url}
