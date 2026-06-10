from __future__ import annotations

from pathlib import Path

from backend.azure.ai_search_client import AzureAISearchClient
from backend.azure.blob_client import AzureBlobClient
from backend.azure.config import AzureConfig, load_azure_config
from backend.azure.cosmos_client import AzureCosmosTraceClient
from backend.models.schemas import GroundingRef
from backend.services.knowledge_index import KnowledgeIndex
from backend.utils.data_loader import DataLoader


DEMO_NOTE = "Demo mode: local grounding simulates Microsoft IQ retrieval."


class GroundingAdapter:
    def __init__(
        self,
        config: AzureConfig | None = None,
        data_loader: DataLoader | None = None,
        knowledge_index: KnowledgeIndex | None = None,
    ) -> None:
        self.config = config or load_azure_config()
        self.data_loader = data_loader or DataLoader()
        if not self.data_loader.experiments:
            self.data_loader.load_all()
        self.knowledge_index = knowledge_index or KnowledgeIndex(Path("knowledge/foundry_docs"))
        self.search_client = AzureAISearchClient(self.config)
        self.blob_client = AzureBlobClient(self.config)
        self.cosmos_client = AzureCosmosTraceClient(self.config)

    async def retrieve_experiment_context(self, experiment_id: str) -> list[GroundingRef]:
        try:
            exp = self.data_loader.get_experiment(experiment_id)
        except KeyError:
            return []
        if self.config.is_demo or not self.search_client.enabled:
            return [
                GroundingRef(
                    source_type="local_demo_grounding",
                    source_id=experiment_id,
                    title=f"Experiment packet {experiment_id}",
                    excerpt=f"{DEMO_NOTE} {exp.failure_observation}",
                    citation=f"data/synthetic/ml_experiment_logs.json#{experiment_id}",
                    confidence=0.82,
                )
            ]
        results = await self.search_client.search(experiment_id, top_k=3)
        return [
            GroundingRef(
                source_type="azure_ai_search",
                source_id=experiment_id,
                title="Azure AI Search experiment context",
                excerpt=str(results[0]),
                citation=self.config.azure_ai_search_index,
                confidence=0.7,
            )
        ]

    async def retrieve_historical_failures(self, query: str, top_k: int = 5) -> list[GroundingRef]:
        if self.config.is_demo or not self.search_client.enabled:
            hits = self.knowledge_index.search(query, top_k=top_k)
            return [
                GroundingRef(
                    source_type="local_demo_grounding",
                    source_id=hit.source_file,
                    title=hit.section_title,
                    excerpt=f"{DEMO_NOTE} {hit.excerpt}",
                    citation=hit.citation,
                    confidence=hit.relevance_score,
                )
                for hit in hits
            ]
        results = await self.search_client.search(query, top_k=top_k)
        return [
            GroundingRef(
                source_type="azure_ai_search",
                source_id=f"search:{index}",
                title="Azure AI Search result",
                excerpt=str(item),
                citation=self.config.azure_ai_search_index,
                confidence=0.65,
            )
            for index, item in enumerate(results, start=1)
        ]

    async def retrieve_remediation_playbook(self, failure_category: str) -> list[GroundingRef]:
        return await self.retrieve_historical_failures(f"{failure_category} remediation playbook", top_k=5)

    async def store_reasoning_trace(self, analysis_id: str, trace: dict) -> dict:
        if self.config.is_demo:
            return {"stored": False, "analysis_id": analysis_id, "mode": "demo", "message": DEMO_NOTE}
        return await self.cosmos_client.store_trace(analysis_id, trace)

    async def build_grounding_summary(self, refs: list[GroundingRef]) -> dict:
        return {
            "mode": "demo" if self.config.is_demo else "production",
            "message": DEMO_NOTE if self.config.is_demo else "Production mode uses configured Azure adapters only.",
            "enabled_integrations": self.config.enabled_integrations,
            "source_count": len(refs),
            "source_types": sorted({ref.source_type for ref in refs}),
            "citations": [ref.citation for ref in refs[:8]],
            "warnings": [] if self.config.is_demo else self._production_warnings(),
        }

    def _production_warnings(self) -> list[str]:
        warnings = []
        for key, enabled in self.config.enabled_integrations.items():
            if key != "local_iq" and not enabled:
                warnings.append(f"{key} credentials are missing; that Azure integration is disabled.")
        return warnings
