from __future__ import annotations

from backend.azure.config import AzureConfig


class AzureAISearchClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_ai_search"]

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        if not self.enabled:
            return [{"warning": "Azure AI Search credentials are not configured; no production retrieval was performed."}]
        return [
            {
                "warning": "Azure AI Search adapter is configured but live search is not invoked during local tests.",
                "query": query,
                "top_k": top_k,
            }
        ]
