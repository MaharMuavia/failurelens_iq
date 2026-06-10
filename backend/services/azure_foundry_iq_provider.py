from __future__ import annotations

from backend.azure.grounding_adapter import GroundingAdapter
from backend.models.enums import RetrievalMode
from backend.models.schemas import KnowledgeHit, RetrievalResult
from backend.services.iq_provider import IQProvider


class AzureFoundryIQProvider(IQProvider):
    """Credential-gated Azure grounding provider.

    Demo mode delegates to local grounding and labels the result honestly.
    Production mode uses the Azure adapter boundary and returns warnings when
    required credentials are missing.
    """

    def __init__(self, grounding_adapter: GroundingAdapter | None = None) -> None:
        self.grounding_adapter = grounding_adapter or GroundingAdapter()

    async def retrieve(self, query: str, top_k: int = 3, cert_filter: str | None = None) -> RetrievalResult:
        refs = await self.grounding_adapter.retrieve_historical_failures(query, top_k=top_k)
        hits = [
            KnowledgeHit(
                source_file=ref.source_id,
                section_title=ref.title,
                relevance_score=ref.confidence,
                excerpt=ref.excerpt,
                matched_terms=[],
                citation=ref.citation,
                retrieval_mode=RetrievalMode.LOCAL if ref.source_type == "local_demo_grounding" else RetrievalMode.AZURE,
            )
            for ref in refs
        ]
        return RetrievalResult(
            query=query,
            hits=hits,
            top_relevance=hits[0].relevance_score if hits else 0.0,
            retrieval_mode=hits[0].retrieval_mode if hits else RetrievalMode.AZURE,
        )
