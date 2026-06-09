from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName, FailureCategory
from backend.models.schemas import AgentContext, ClassificationResult, RuleEvaluation


class ClassifierAgent(BaseAgent):
    name = AgentName.CLASSIFIER

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        rule_specs = [
            ("P1_Data_Leakage", 1, FailureCategory.DATA_LEAKAGE, exp.has_leakage_signal, [self.cite_evidence("suspected_leakage_columns", exp.suspected_leakage_columns, "leakage signal")]),
            ("P2_Responsible_AI", 2, FailureCategory.RESPONSIBLE_AI, exp.has_bias_language, [self.cite_evidence("failure_observation", exp.failure_observation, "fairness/protected language")]),
            ("P3_Deployment_Drift", 3, FailureCategory.DEPLOYMENT_DRIFT, exp.has_drift_indicators or exp.pipeline_stage in {"deployment", "monitoring"}, [self.cite_evidence("drift_indicators", exp.drift_indicators, "deployment or drift signal")]),
            ("P4_Evaluation_Methodology", 4, FailureCategory.EVALUATION_METHODOLOGY, exp.minority_pct < 20 and exp.reported_metric == "accuracy", [self.cite_evidence("class_balance", exp.class_balance, "imbalanced accuracy risk"), self.cite_evidence("minority_f1", exp.minority_f1, "minority class weakness")]),
            ("P5_Feature_Engineering", 5, FailureCategory.FEATURE_ENGINEERING, exp.pipeline_stage == "feature_engineering" or "feature" in exp.failure_observation.lower(), [self.cite_evidence("feature_set", exp.feature_set, "feature process signal")]),
            ("P6_Data_Quality", 6, FailureCategory.DATA_QUALITY, bool(exp.error_logs and exp.data_quality_signals), [self.cite_evidence("data_quality_signals", exp.data_quality_signals, "data quality signal")]),
        ]
        evaluations: list[RuleEvaluation] = []
        triggered: list[tuple[int, FailureCategory]] = []
        for name, priority, category, did_trigger, evidence in rule_specs:
            evaluations.append(
                RuleEvaluation(
                    rule_name=name,
                    priority=priority,
                    triggered=bool(did_trigger),
                    evidence=evidence if did_trigger else [],
                    confidence_contribution=round(0.85 - (priority * 0.08), 4) if did_trigger else 0.0,
                )
            )
            if did_trigger:
                triggered.append((priority, category))
        triggered.sort(key=lambda item: item[0])
        category = triggered[0][1] if triggered else FailureCategory.UNKNOWN
        conflicts = [item[1] for item in triggered[1:]]
        conflict_penalty = min(len(conflicts) * 0.15, 0.45)
        confidence = 0.32 if category == FailureCategory.UNKNOWN else max(0.42, 0.82 - conflict_penalty)
        ctx.classification = ClassificationResult(
            failure_category=category,
            rules_evaluated=evaluations,
            conflicting_categories=conflicts,
            conflict_resolution=(
                f"Selected {category.value} by highest-priority triggered rule; conflicts={', '.join(c.value for c in conflicts) or 'none'}."
            ),
            confidence=round(confidence, 4),
            grounding_citations=["ml_failure_taxonomy.md § Cross-Category Conflict Resolution"],
        )
        steps = [
            self.build_reasoning_step(1, "Evaluated six deterministic rules", f"{len(triggered)} rules triggered.", ["failure_observation", "metrics", "drift_indicators"], 0.12),
            self.build_reasoning_step(2, "Resolved category conflicts", ctx.classification.conflict_resolution, ["rules_evaluated"], -conflict_penalty),
            self.build_reasoning_step(3, "Calculated classification confidence", f"Classification confidence is {ctx.classification.confidence:.3f}.", ["rules_evaluated"], 0.04),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("failure_category", category.value, "selected category")], ctx.classification.confidence, ctx.classification.grounding_citations)
        return ctx
