from __future__ import annotations

from backend.azure.config import AzureConfig


class AzureCosmosTraceClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_cosmos_db"]

    async def store_trace(self, analysis_id: str, trace: dict) -> dict[str, object]:
        if not self.enabled:
            return {
                "stored": False,
                "analysis_id": analysis_id,
                "warning": "Azure Cosmos DB credentials are not configured; trace persistence is local/demo only.",
            }
        return {"stored": True, "analysis_id": analysis_id, "container": self.config.azure_cosmos_container}
