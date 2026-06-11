from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from backend.azure.config import AzureConfig


class AzureAISearchClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_ai_search"]

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        if not self.enabled:
            return [
                {
                    "warning": "Azure AI Search credentials are not configured; no production retrieval was performed.",
                    "reason": "credentials_missing",
                }
            ]

        semantic_body = {
            "search": query,
            "top": top_k,
            "queryType": "semantic",
            "semanticConfiguration": "default",
        }
        simple_body = {"search": query, "top": top_k}
        semantic_response = await self._post_search(semantic_body)
        if semantic_response["ok"]:
            return self._normalize_results(semantic_response["payload"])

        simple_response = await self._post_search(simple_body)
        if simple_response["ok"]:
            results = self._normalize_results(simple_response["payload"])
            if results:
                results[0]["warning"] = "Semantic search failed; Azure AI Search simple query fallback was used."
                results[0]["semantic_error"] = semantic_response["detail"]
            return results

        return [
            {
                "warning": "Azure AI Search request failed; no production retrieval was performed.",
                "status_code": simple_response.get("status_code") or semantic_response.get("status_code"),
                "message": simple_response.get("detail") or semantic_response.get("detail"),
            }
        ]

    async def _post_search(self, body: dict[str, object]) -> dict[str, Any]:
        from backend.core.config import settings
        import asyncio

        index = quote(self.config.azure_ai_search_index, safe="")
        url = f"{self.config.azure_ai_search_endpoint}/indexes/{index}/docs/search?api-version=2023-11-01"
        headers = {"api-key": self.config.azure_ai_search_key, "Content-Type": "application/json"}
        
        max_retries = 2
        delay = 0.5
        response = None
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=float(settings.REQUEST_TIMEOUT_SECONDS)) as client:
                    response = await client.post(url, headers=headers, json=body)
                if response.status_code < 500 and response.status_code != 429:
                    break
            except httpx.HTTPError as exc:
                last_exception = exc
                if attempt == max_retries:
                    return {"ok": False, "detail": str(exc)}
            
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2

        if response is None:
            return {"ok": False, "detail": str(last_exception) if last_exception else "Request failed"}

        if response.status_code >= 400:
            return {"ok": False, "status_code": response.status_code, "detail": response.text[:500]}
        try:
            return {"ok": True, "payload": response.json()}
        except ValueError:
            return {"ok": False, "status_code": response.status_code, "detail": "Azure AI Search returned non-JSON response."}

    def _normalize_results(self, payload: dict[str, Any]) -> list[dict[str, object]]:
        normalized: list[dict[str, object]] = []
        for item in payload.get("value", []):
            if not isinstance(item, dict):
                continue
            score = item.get("@search.rerankerScore", item.get("@search.score", item.get("score", 0.0)))
            normalized.append(
                {
                    "source_id": str(item.get("source_id") or item.get("id") or item.get("experiment_id") or ""),
                    "title": str(item.get("title") or item.get("experiment_id") or "Azure AI Search result"),
                    "content": str(item.get("content") or item.get("chunk") or item.get("text") or ""),
                    "score": float(score or 0.0),
                    "url": str(item.get("url") or ""),
                    "chunk_id": str(item.get("chunk_id") or item.get("id") or ""),
                    "source_type": str(item.get("source_type") or "azure_ai_search"),
                }
            )
        return normalized
