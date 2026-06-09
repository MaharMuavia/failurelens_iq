from __future__ import annotations

from backend.models.enums import RetrievalMode
from backend.models.schemas import RetrievalResult
from backend.services.iq_provider import IQProvider
from backend.services.knowledge_index import KnowledgeIndex


class LocalIQProvider(IQProvider):
    def __init__(self, knowledge_index: KnowledgeIndex) -> None:
        self.knowledge_index = knowledge_index

    async def retrieve(self, query: str, top_k: int = 3, cert_filter: str | None = None) -> RetrievalResult:
        hits = self.knowledge_index.search(query, top_k=top_k, cert_filter=cert_filter)
        return RetrievalResult(
            query=query,
            hits=hits,
            top_relevance=hits[0].relevance_score if hits else 0.0,
            retrieval_mode=RetrievalMode.LOCAL,
        )
