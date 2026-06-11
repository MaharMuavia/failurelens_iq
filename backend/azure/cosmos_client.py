from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

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
                "reason": "credentials_missing",
                "warning": "Azure Cosmos DB credentials are not configured; trace persistence is local/demo only.",
            }
        document = {
            "id": f"{analysis_id}-{uuid4()}",
            "analysis_id": analysis_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "app_name": "FailureLens IQ",
            "trace": trace,
            "source": "FailureLens IQ",
        }
        try:
            result = await asyncio.to_thread(self._store_document, document)
        except Exception as exc:
            return {"stored": False, "analysis_id": analysis_id, "reason": "cosmos_error", "detail": str(exc)[:500]}
        return {
            "stored": True,
            "analysis_id": analysis_id,
            "database": self.config.azure_cosmos_database,
            "container": self.config.azure_cosmos_container,
            "document_id": result.get("id", document["id"]) if isinstance(result, dict) else document["id"],
        }

    def _store_document(self, document: dict) -> dict:
        try:
            from azure.cosmos import CosmosClient
        except ImportError as exc:
            raise RuntimeError("azure-cosmos is not installed. Run pip install -r requirements.txt.") from exc

        client = CosmosClient(self.config.azure_cosmos_endpoint, credential=self.config.azure_cosmos_key)
        database = client.get_database_client(self.config.azure_cosmos_database)
        container = database.get_container_client(self.config.azure_cosmos_container)
        return container.upsert_item(document)
