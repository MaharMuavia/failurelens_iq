from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from backend.models.enums import RetrievalMode
from backend.models.schemas import CertSkillMapping, GroundingResult, IQSearchResult, KnowledgeHit, RetrievalResult, SimilarExperiment
from backend.services.iq_provider import IQProvider
from backend.services.knowledge_index import KnowledgeIndex, tokenize
from backend.core.similarity_engine import SimilarityEngine
from backend.utils.data_loader import DataLoader


HONEST_LIMITATION = (
    "This is local Foundry IQ adapter mode. Live Azure Foundry IQ requires Azure AI Search "
    "and deployed model quota."
)


class FoundryRetrieval(dict):
    @property
    def hits(self) -> list[KnowledgeHit]:
        return self["_retrieval_result"].hits

    @property
    def top_relevance(self) -> float:
        return self["_retrieval_result"].top_relevance

    @property
    def retrieval_mode(self) -> RetrievalMode:
        return self["_retrieval_result"].retrieval_mode

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        payload = {key: value for key, value in self.items() if key != "_retrieval_result"}
        payload.update(self["_retrieval_result"].model_dump(mode=mode))
        return payload

    def to_retrieval_result(self) -> RetrievalResult:
        return self["_retrieval_result"]


class FoundryIQLocalAdapter(IQProvider):
    """Local Foundry IQ-compatible adapter.

    Simulates the core Foundry IQ concepts:
    - knowledge sources
    - knowledge base
    - retrieval
    - citations
    - source metadata
    - permission-aware filtering
    - grounded answer context

    This is adapter-ready and can be replaced with Azure AI Search / Foundry IQ later.
    """

    def __init__(
        self,
        source_dir: Path | str = Path("knowledge/foundry_iq_sources"),
        knowledge_dir: Path | str = Path("knowledge/foundry_docs"),
        data_loader: DataLoader | None = None,
    ) -> None:
        self.source_dir = Path(source_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_index = KnowledgeIndex(self.knowledge_dir)
        self.data_loader = data_loader or DataLoader()
        if not self.data_loader.experiments:
            self.data_loader.load_all()
        self.similarity_engine = SimilarityEngine()
        self.total_retrievals = 0
        self._sources: list[dict[str, Any]] | None = None

    def load_knowledge_sources(self) -> list[dict[str, Any]]:
        if self._sources is not None:
            return self._sources
        sources: list[dict[str, Any]] = []
        if not self.source_dir.exists():
            self._sources = []
            return self._sources
        for path in sorted(self.source_dir.iterdir()):
            if path.suffix.lower() == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                items = payload if isinstance(payload, list) else payload.get("items", [payload])
                for item in items:
                    sources.append(self._normalize_source(item, path))
            elif path.suffix.lower() == ".md":
                sources.append(self._parse_markdown_source(path))
        self._sources = sources
        return self._sources

    def index_documents(self) -> list[dict[str, Any]]:
        return self.load_knowledge_sources()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        user_scope: str = "demo",
        cert_filter: str | None = None,
    ) -> FoundryRetrieval:
        self.total_retrievals += 1
        sources = self.load_knowledge_sources()
        scored_sources = []
        for source in sources:
            if source.get("permission_scope") == user_scope or user_scope == "demo":
                score = self._score_source(query, source, cert_filter)
                scored_sources.append((score, source))

        scored_sources.sort(key=lambda item: item[0], reverse=True)
        top_sources = scored_sources[:top_k]

        citations = []
        for score, source in top_sources:
            citations.append({
                "id": source["citation_id"],
                "title": source["title"],
                "source_type": source["source_type"],
                "citation": source["citation"],
                "excerpt": source["content"],
                "permission_scope": source["permission_scope"],
                "relevance_score": score,
                "example_evidence": source.get("example_evidence", ""),
            })

        hits = [
            KnowledgeHit(
                source_file=item["citation"],
                section_title=item["title"],
                relevance_score=item["relevance_score"],
                excerpt=item["excerpt"],
                matched_terms=self._matched_terms(query, item["excerpt"]),
                citation=item["citation"],
                retrieval_mode=RetrievalMode.LOCAL,
            )
            for item in citations
        ]
        retrieval_result = RetrievalResult(
            query=query,
            hits=hits,
            top_relevance=hits[0].relevance_score if hits else 0.0,
            retrieval_mode=RetrievalMode.LOCAL,
        )
        return FoundryRetrieval(
            {
                "provider": "FoundryIQLocalAdapter",
                "mode": "local_foundry_iq_adapter",
                "selected_iq_layer": "Foundry IQ",
                "live_microsoft_iq": False,
                "live_azure": False,
                "adapter_ready": True,
                "azure_quota_blocked": True,
                "query": query,
                "retrieval_mode": "local_agentic_retrieval",
                "total_retrievals": self.total_retrievals,
                "knowledge_sources": [
                    {
                        "title": source["title"],
                        "source_type": source["source_type"],
                        "citation_id": source["citation_id"],
                        "permission_scope": source["permission_scope"],
                        "tags": source["tags"],
                        "example_evidence": source.get("example_evidence", ""),
                    }
                    for source in sources
                ],
                "citations": citations,
                "grounding_context": " ".join(item["excerpt"] for item in citations)[:1200],
                "honest_limitation": "This is Foundry IQ Local Adapter Mode. Live Azure Foundry IQ requires Azure AI Search, Foundry project credentials, and model quota.",
                "_retrieval_result": retrieval_result,
            }
        )

    async def retrieve_failure_taxonomy(self, query: str, top_k: int = 3) -> RetrievalResult:
        retrieval = await self.retrieve(query, top_k=top_k)
        return retrieval.to_retrieval_result()

    async def search_knowledge(self, query: str, top_k: int = 5, cert_filter: str | None = None) -> list[IQSearchResult]:
        self.total_retrievals += 1
        hits = self.knowledge_index.search(query, top_k=top_k, cert_filter=cert_filter)
        return [
            IQSearchResult(
                source=hit.source_file,
                source_file=hit.source_file,
                section_heading=hit.section_title,
                excerpt=hit.excerpt,
                relevance_score=hit.relevance_score,
                matched_terms=hit.matched_terms,
                citation=hit.citation,
                grounding_confidence=hit.relevance_score,
            )
            for hit in hits
        ]

    async def ground_reasoning(self, claim: str, evidence: list[str]) -> GroundingResult:
        scores = [(item, await self.get_relevance_score(claim, item)) for item in evidence if item]
        supporting = [item for item, score in scores if score >= 0.12]
        confidence = round(sum(score for _, score in scores) / len(scores), 4) if scores else 0.0
        return GroundingResult(
            claim=claim,
            supported=bool(supporting) and confidence >= 0.12,
            grounding_confidence=confidence,
            supporting_evidence=supporting[:5],
        )

    async def get_relevance_score(self, query: str, document: str) -> float:
        query_tokens = Counter(tokenize(query))
        doc_tokens = Counter(tokenize(document))
        if not query_tokens or not doc_tokens:
            return 0.0
        terms = set(query_tokens).union(doc_tokens)
        dot = sum(query_tokens.get(term, 0) * doc_tokens.get(term, 0) for term in terms)
        query_norm = math.sqrt(sum(value * value for value in query_tokens.values()))
        doc_norm = math.sqrt(sum(value * value for value in doc_tokens.values()))
        return round(dot / (query_norm * doc_norm), 4) if query_norm and doc_norm else 0.0

    async def retrieve_certification_mapping(self, failure_category: str) -> list[CertSkillMapping]:
        results = await self.search_knowledge(f"{failure_category} certification skill guide", top_k=5)
        mappings: list[CertSkillMapping] = []
        for result in results:
            source = result.source_file.lower()
            if "ai102" in source or "responsible" in failure_category.lower() or "bias" in failure_category.lower():
                cert_code, domain = "AI-102", "Responsible AI and fairness"
            elif "dp203" in source or "data quality" in failure_category.lower():
                cert_code, domain = "DP-203", "Data quality and pipeline reliability"
            elif "pl300" in source:
                cert_code, domain = "PL-300", "Manager analytics and dashboard interpretation"
            else:
                cert_code, domain = "DP-100", "ML evaluation and model operations"
            mappings.append(
                CertSkillMapping(
                    failure_category=failure_category,
                    cert_code=cert_code,
                    skill_domain=domain,
                    source=result.source_file,
                    grounding_confidence=result.grounding_confidence,
                    relevant_excerpt=result.excerpt,
                )
            )
        return mappings

    async def get_experiment_memory(self, experiment_id: str, team_id: str) -> list[SimilarExperiment]:
        self.total_retrievals += 1
        try:
            target = self.data_loader.get_experiment(experiment_id)
        except KeyError:
            team_candidates = self.data_loader.experiments_for_team(team_id)
            target = team_candidates[0] if team_candidates else None
        if target is None:
            return []
        candidates = [
            item
            for item in self.data_loader.experiments
            if item.experiment_id != target.experiment_id and item.team_id == team_id
        ]
        return self.similarity_engine.find_similar(target, candidates, top_k=5)

    def get_status(self) -> dict[str, Any]:
        sources = self.load_knowledge_sources()
        return {
            "provider": "FoundryIQLocalAdapter",
            "mode": "local_foundry_iq_adapter",
            "label": "Foundry IQ Local Adapter Mode",
            "live_azure": False,
            "adapter_ready": True,
            "foundry_iq_base_architecture": True,
            "knowledge_sources_configured": bool(sources),
            "knowledge_source_count": len(self.knowledge_index.sources()),
            "total_retrievals": self.total_retrievals,
            "citations_supported": True,
            "permission_metadata_supported": True,
            "agentic_retrieval_supported": True,
            "honest_limitation": (
                "Azure quota is 0, so this demo uses local Foundry IQ adapter mode. "
                "The adapter is designed to switch to live Azure Foundry IQ when quota is available."
            ),
        }

    def _parse_markdown_source(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        metadata: dict[str, str] = {}
        content_lines: list[str] = []
        in_content = False
        for line in text.splitlines():
            if not in_content and ":" in line:
                key, value = line.split(":", 1)
                normalized = key.strip().lower().replace(" ", "_")
                if normalized in {"id", "citation", "agent_usage_notes", "title", "source_type", "permission_scope", "citation_id", "tags", "relevance_tags", "content", "example_evidence"}:
                    if normalized == "content":
                        in_content = True
                        if value.strip():
                            content_lines.append(value.strip())
                    else:
                        metadata[normalized] = value.strip()
                    continue
            if in_content or line.strip():
                content_lines.append(line.strip())
        return self._normalize_source(
            {
                **metadata,
                "content": " ".join(line for line in content_lines if line),
            },
            path,
        )

    def _normalize_source(self, item: dict[str, Any], path: Path) -> dict[str, Any]:
        tags = item.get("tags") or item.get("relevance_tags") or []
        if isinstance(tags, str):
            tags = [part.strip() for part in tags.split(",") if part.strip()]
        title = str(item.get("title") or path.stem.replace("_", " ").title())
        source_type = str(item.get("source_type") or path.stem)
        citation_id = str(item.get("id") or item.get("citation_id") or f"{path.stem}-001")
        citation = str(item.get("citation") or f"{path.as_posix()}#{citation_id}")
        return {
            "id": citation_id,
            "title": title,
            "source_type": source_type,
            "citation": citation,
            "citation_id": citation_id,
            "excerpt": str(item.get("excerpt") or item.get("content") or "")[:500],
            "content": str(item.get("content") or item.get("excerpt") or ""),
            "permission_scope": str(item.get("permission_scope") or "demo"),
            "tags": tags,
            "path": path.as_posix(),
            "example_evidence": str(item.get("example_evidence") or ""),
            "agent_usage_notes": str(item.get("agent_usage_notes") or ""),
        }

    def _score_source(self, query: str, source: dict[str, Any], cert_filter: str | None) -> float:
        haystack = " ".join(
            [
                source["title"],
                source["source_type"],
                source["content"],
                " ".join(source["tags"]),
            ]
        ).lower()
        terms = self._terms(query)
        overlap = sum(1 for term in terms if term in haystack)
        tag_bonus = sum(1 for tag in source["tags"] if str(tag).lower() in query.lower()) * 0.08
        cert_bonus = 0.12 if cert_filter and cert_filter.lower() in haystack else 0.0
        score = min(0.95, 0.28 + overlap * 0.09 + tag_bonus + cert_bonus)
        return round(score, 4)

    def _citation_payload(self, source: dict[str, Any], score: float) -> dict[str, Any]:
        return {
            "id": source["citation_id"],
            "title": source["title"],
            "source_type": source["source_type"],
            "citation": source["citation"],
            "excerpt": source["excerpt"],
            "permission_scope": source["permission_scope"],
            "relevance_score": round(max(0.0, min(score, 0.95)), 4),
        }

    def _terms(self, query: str) -> list[str]:
        return [term for term in re.findall(r"[a-z0-9_]+", query.lower()) if len(term) > 2]

    def _matched_terms(self, query: str, text: str) -> list[str]:
        lowered = text.lower()
        return [term for term in self._terms(query) if term in lowered][:8]


FoundryIQAdapter = FoundryIQLocalAdapter
