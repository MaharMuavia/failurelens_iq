from __future__ import annotations

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
