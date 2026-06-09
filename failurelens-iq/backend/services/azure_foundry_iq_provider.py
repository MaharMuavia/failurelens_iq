from __future__ import annotations

from backend.models.schemas import RetrievalResult
from backend.services.iq_provider import IQProvider


class AzureFoundryIQProvider(IQProvider):
    """Offline adapter placeholder for the hackathon MVP.

    The project runs fully offline. This class documents the upgrade seam without
    performing network calls or requiring Azure credentials.
    """

    async def retrieve(self, query: str, top_k: int = 3, cert_filter: str | None = None) -> RetrievalResult:
        return RetrievalResult(query=query, hits=[], top_relevance=0.0)
