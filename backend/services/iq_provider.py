from __future__ import annotations

from abc import ABC, abstractmethod

from backend.models.schemas import RetrievalResult


class IQProvider(ABC):
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 3, cert_filter: str | None = None) -> RetrievalResult:
        return RetrievalResult(query=query, hits=[], top_relevance=0.0)

    async def retrieve_failure_taxonomy(self, query: str, top_k: int = 3) -> RetrievalResult:
        return await self.retrieve(query, top_k=top_k)
