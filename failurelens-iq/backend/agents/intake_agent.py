from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName
from backend.models.schemas import AgentContext, IntakeResult


class IntakeAgent(BaseAgent):
    name = AgentName.INTAKE

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        missing: list[str] = []
        critical = {
            "metrics": bool(exp.metrics),
            "baseline_metrics": bool(exp.baseline_metrics),
            "feature_set": bool(exp.feature_set),
            "failure_observation": bool(exp.failure_observation),
            "validation_strategy": bool(exp.validation_strategy),
            "training_config": bool(exp.training_config),
        }
        missing = [field for field, present in critical.items() if not present]
        detected = []
        if exp.has_leakage_signal:
            detected.append("leakage")
        if exp.has_bias_language:
            detected.append("bias")
        if exp.has_drift_indicators:
            detected.append("drift")
        if exp.minority_pct < 20 and exp.reported_metric == "accuracy":
            detected.append("evaluation methodology")
        if exp.pipeline_stage == "feature_engineering":
            detected.append("feature engineering")
        if exp.data_quality_signals or exp.error_logs:
            detected.append("data quality")
        completeness = 1 - (len(missing) / len(critical))
        ctx.intake_result = IntakeResult(
            completeness_score=round(completeness, 4),
            missing_critical_fields=missing,
            detected_signals=detected,
            team_profile=self.data_loader.get_team_profile(exp.team_id) if self.data_loader else {},
            work_context=self.data_loader.get_work_context(exp.team_id) if self.data_loader else {},
            validation_warnings=[f"Missing critical field: {field}" for field in missing],
            confidence=round(max(0.15, completeness), 4),
        )
        steps = [
            self.build_reasoning_step(1, "Checked critical fields", f"Missing fields: {missing or 'none'}.", ["metrics", "baseline_metrics", "feature_set"], 0.1),
            self.build_reasoning_step(2, "Detected evidence signals", f"Signals detected: {detected or 'limited evidence'}.", ["failure_observation", "engineer_notes"], 0.1),
            self.build_reasoning_step(3, "Loaded team context", f"Team context loaded for {exp.team_id}.", ["team_id"], 0.05),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("missing_critical_fields", missing, "drives completeness and review risk")], ctx.intake_result.confidence)
        return ctx
