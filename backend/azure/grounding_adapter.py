from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from backend.azure.ai_search_client import AzureAISearchClient
from backend.azure.blob_client import AzureBlobClient
from backend.azure.config import AzureConfig, load_azure_config
from backend.azure.cosmos_client import AzureCosmosTraceClient
from backend.core.config import settings
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
        self.warnings: list[str] = []

    async def retrieve_experiment_context(self, experiment_id: str) -> list[GroundingRef]:
        try:
            exp = self.data_loader.get_experiment(experiment_id)
        except KeyError:
            return []
        if not self.search_client.enabled:
            return [
                GroundingRef(
                    source_type="local_demo_grounding",
                    source_id=experiment_id,
                    title=f"Experiment packet {experiment_id}",
                    excerpt=f"{DEMO_NOTE} {exp.failure_observation}",
                    citation=f"data/synthetic/ml_experiment_logs.json#{experiment_id}",
                    confidence=0.82,
                    source_system="local_demo_grounding",
                    retrieved_at=datetime.now(timezone.utc),
                    iq_layer="Foundry IQ",
                    retrieval_system="Local demo grounding",
                    grounding_mode="demo",
                )
            ]
        results = await self.search_client.search(experiment_id, top_k=3)
        self._capture_result_warnings(results)
        return self._refs_from_search_results(results)

    async def retrieve_historical_failures(self, query: str, top_k: int = 5) -> list[GroundingRef]:
        if not self.search_client.enabled:
            hits = self.knowledge_index.search(query, top_k=top_k)
            return [
                GroundingRef(
                    source_type="local_demo_grounding",
                    source_id=hit.source_file,
                    title=hit.section_title,
                    excerpt=f"{DEMO_NOTE} {hit.excerpt}",
                    citation=hit.citation,
                    confidence=hit.relevance_score,
                    source_system="local_demo_grounding",
                    retrieved_at=datetime.now(timezone.utc),
                    iq_layer="Foundry IQ",
                    retrieval_system="Local demo grounding",
                    grounding_mode="demo",
                )
                for hit in hits
            ]
        results = await self.search_client.search(query, top_k=top_k)
        self._capture_result_warnings(results)
        return self._refs_from_search_results(results)

    async def retrieve_remediation_playbook(self, failure_category: str) -> list[GroundingRef]:
        return await self.retrieve_historical_failures(f"{failure_category} remediation playbook", top_k=5)

    async def store_reasoning_trace(self, analysis_id: str, trace: dict) -> dict:
        if not self.cosmos_client.enabled:
            return {
                "stored": False,
                "analysis_id": analysis_id,
                "reason": "credentials_missing",
                "warning": "Azure Cosmos DB credentials are not configured; trace persistence is local/demo only.",
            }
        if not settings.ENABLE_AZURE_TRACE_STORAGE:
            return {
                "stored": False,
                "analysis_id": analysis_id,
                "mode": "production" if not self.config.is_demo else "demo",
                "reason": "disabled_by_cost_guard",
                "message": "Azure Cosmos trace storage is disabled by ENABLE_AZURE_TRACE_STORAGE=false.",
            }
        return await self.cosmos_client.store_trace(analysis_id, trace)

    async def build_grounding_summary(self, refs: list[GroundingRef], active_iq_provider: str | None = None) -> dict:
        warnings = [] if self.config.is_demo else [*self._production_warnings(), *self.warnings]
        azure_services_used = sorted(
            service
            for service, enabled in {
                "azure_ai_search": any(ref.source_type == "azure_ai_search" for ref in refs),
                "azure_blob_storage": self.blob_client.enabled,
                "azure_cosmos_db": self.cosmos_client.enabled,
            }.items()
            if enabled
        )
        return {
            "mode": "demo" if self.config.is_demo else "production",
            "active_iq_provider": active_iq_provider,
            "message": DEMO_NOTE if self.config.is_demo else "Production mode uses configured Azure adapters only.",
            "enabled_integrations": self.config.enabled_integrations,
            "source_count": len(refs),
            "source_types": sorted({ref.source_type for ref in refs}),
            "azure_services_used": azure_services_used,
            "citations": [ref.citation for ref in refs[:8]],
            "citations_count": len([ref for ref in refs if ref.citation]),
            "iq_layer": "Foundry IQ",
            "retrieval_system": "Azure AI Search" if any(ref.source_type == "azure_ai_search" for ref in refs) else "Local demo grounding",
            "warnings": warnings,
        }

    def _production_warnings(self) -> list[str]:
        warnings = []
        for key, enabled in self.config.enabled_integrations.items():
            if key != "local_iq" and not enabled:
                warnings.append(f"{key} credentials are missing; that Azure integration is disabled.")
        return warnings

    def _refs_from_search_results(self, results: list[dict[str, object]]) -> list[GroundingRef]:
        refs: list[GroundingRef] = []
        for index, item in enumerate(results, start=1):
            if item.get("warning") and not (item.get("content") or item.get("excerpt")):
                continue
            score = float(item.get("score") or 0.65)
            confidence = max(0.0, min(score, 1.0))
            source_id = str(item.get("source_id") or item.get("chunk_id") or f"search:{index}")
            url = str(item.get("url") or "") or None
            citation = str(item.get("citation") or "") or url or f"{self.config.azure_ai_search_index}#{source_id}"
            refs.append(
                GroundingRef(
                    source_type="azure_ai_search",
                    source_id=source_id,
                    title=str(item.get("title") or "Azure AI Search result"),
                    excerpt=str(item.get("content") or item.get("excerpt") or "")[:400],
                    citation=citation,
                    confidence=confidence,
                    url=url,
                    source_system="azure_ai_search",
                    retrieved_at=datetime.now(timezone.utc),
                    chunk_id=str(item.get("chunk_id") or "") or None,
                    iq_layer="Foundry IQ",
                    retrieval_system="Azure AI Search",
                    grounding_mode="production",
                )
            )
        return refs

    def _capture_result_warnings(self, results: list[dict[str, object]]) -> None:
        for item in results:
            warning = item.get("warning")
            if warning and str(warning) not in self.warnings:
                self.warnings.append(str(warning))
