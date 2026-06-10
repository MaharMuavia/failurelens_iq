from __future__ import annotations

from collections import Counter

from backend.agents.base_agent import BaseAgent
from backend.core.similarity_engine import SimilarityEngine
from backend.models.enums import AgentName
from backend.models.schemas import AgentContext, HistoricalMemoryResult


class ExperimentHistorianAgent(BaseAgent):
    name = AgentName.HISTORIAN

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.similarity_engine = SimilarityEngine()

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        candidates = [item for item in (self.data_loader.experiments if self.data_loader else []) if item.experiment_id != exp.experiment_id]
        similar = self.similarity_engine.find_similar(exp, candidates, top_k=5)
        pattern_counts = Counter(signal for item in similar for signal in item.shared_signals)
        repeated_patterns = [f"{pattern} ({count} similar runs)" for pattern, count in pattern_counts.most_common(3)]
        prior_fixes = [
            f"Inspect {item.experiment_id}: {item.outcome_note}; reuse the review checklist for {', '.join(item.shared_signals[:2])}."
            for item in similar[:3]
        ]
        team_gap = (
            ctx.diagnosis.knowledge_gap
            if ctx.diagnosis
            else "Experiment review memory needs more labeled historical evidence."
        )
        confidence = round(0.45 + min(len(similar), 5) * 0.08, 4)
        ctx.historical_memory = HistoricalMemoryResult(
            similar_historical_experiments=similar,
            repeated_patterns=repeated_patterns or ["No strong repeated pattern reached the threshold."],
            prior_fixes=prior_fixes or ["Collect more labeled failures before recommending a reusable fix."],
            team_learning_gap=team_gap,
            confidence=min(confidence, 0.85),
        )
        steps = [
            self.build_reasoning_step(
                1,
                "Compared this run with historical experiments",
                f"{len(similar)} similar historical experiments returned.",
                ["experiment_id", "metrics", "pipeline_stage"],
                0.08,
                thought_type="evidence_check",
                next_action="Use similar runs as grounding for the remediation plan.",
            ),
            self.build_reasoning_step(
                2,
                "Extracted repeated failure patterns",
                "; ".join(ctx.historical_memory.repeated_patterns[:2]),
                ["similar_historical_experiments.shared_signals"],
                0.06,
                thought_type="inference",
            ),
            self.build_reasoning_step(
                3,
                "Converted memory into a team learning gap",
                ctx.historical_memory.team_learning_gap,
                ["diagnosis.knowledge_gap", "team_id"],
                0.04,
                thought_type="decision",
                uncertainty=["Similarity is based on local synthetic experiment fields, not a production vector index."],
                next_action="Attach the repeated pattern to the manager summary.",
            ),
        ]
        self.complete_trace(
            ctx,
            trace,
            started,
            steps,
            [f"similar_experiments={len(similar)} -> historical memory generated"],
            ctx.historical_memory.confidence,
            [item.experiment_id for item in similar[:3]],
        )
        return ctx
