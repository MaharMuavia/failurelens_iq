from __future__ import annotations

import math
from dataclasses import dataclass

from backend.models.enums import EvidenceStrength


@dataclass
class ScoringInputs:
    evidence_coverage: float = 0.0
    category_evidence: float = 0.0
    metric_degradation: float = 0.0
    iq_relevance: float = 0.0
    planner_agreement: float = 0.0
    conflict_penalty: float = 0.0
    missing_critical_fields_penalty: float = 0.0


@dataclass
class ScoringResult:
    confidence: float
    raw_score: float
    factors: dict[str, float]
    penalties: dict[str, float]
    evidence_strength: EvidenceStrength


class ScoringService:
    def compute(self, inputs: ScoringInputs | None = None, **kwargs: float) -> ScoringResult:
        if inputs is None:
            inputs = ScoringInputs(**kwargs)
        raw_score = (
            0.30 * inputs.evidence_coverage
            + 0.25 * inputs.category_evidence
            + 0.15 * inputs.metric_degradation
            + 0.15 * inputs.iq_relevance
            + 0.10 * inputs.planner_agreement
            - 0.15 * inputs.conflict_penalty
            - 0.10 * inputs.missing_critical_fields_penalty
        )
        raw_score = max(0.0, min(1.0, raw_score))
        confidence = 1 / (1 + math.exp(-(raw_score * 6 - 3)))
        if confidence >= 0.75:
            strength = EvidenceStrength.STRONG
        elif confidence >= 0.55:
            strength = EvidenceStrength.MODERATE
        elif confidence >= 0.40:
            strength = EvidenceStrength.WEAK
        else:
            strength = EvidenceStrength.INSUFFICIENT
        return ScoringResult(
            confidence=round(confidence, 4),
            raw_score=round(raw_score, 4),
            factors={
                "evidence_coverage": inputs.evidence_coverage,
                "category_evidence": inputs.category_evidence,
                "metric_degradation": inputs.metric_degradation,
                "iq_relevance": inputs.iq_relevance,
                "planner_agreement": inputs.planner_agreement,
            },
            penalties={
                "conflict_penalty": inputs.conflict_penalty,
                "missing_critical_fields_penalty": inputs.missing_critical_fields_penalty,
            },
            evidence_strength=strength,
        )
