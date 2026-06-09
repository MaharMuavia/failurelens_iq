from __future__ import annotations

from datetime import datetime, timezone

from backend.core.similarity_engine import SimilarityEngine
from backend.models.enums import AgentName, FailureCategory
from backend.models.schemas import ExecutionPlan, ExperimentLog, FailureHypothesis, PlannerContext
from backend.utils.data_loader import DataLoader


class Planner:
    def __init__(self) -> None:
        self.similarity_engine = SimilarityEngine()

    async def plan(
        self,
        experiment: ExperimentLog,
        past_experiments: list[ExperimentLog],
        data_loader: DataLoader | None = None,
    ) -> PlannerContext:
        completeness = self._data_completeness(experiment)
        signals = self._signals(experiment)
        ranked = [category for category, triggered in signals if triggered]
        suspected = ranked[0] if ranked else FailureCategory.UNKNOWN
        alternatives = ranked[1:]
        threshold = 0.40 if completeness >= 0.70 else 0.45 if completeness >= 0.40 else 0.55
        similar = self.similarity_engine.find_similar(
            experiment,
            [item for item in past_experiments if item.experiment_id != experiment.experiment_id],
            top_k=3,
        )
        skill_context = {}
        if data_loader:
            skill_context = {
                "team_profile": data_loader.get_team_profile(experiment.team_id),
                "work_context": data_loader.get_work_context(experiment.team_id),
            }
        key_signals = self._key_signals(experiment, suspected)
        hypothesis = FailureHypothesis(
            suspected_category=suspected,
            alternative_categories=alternatives,
            hypothesis_statement=self._hypothesis_statement(experiment, suspected, key_signals),
            key_signals=key_signals,
            confidence_estimate=round(0.25 + completeness * 0.5 + (0.15 if suspected != FailureCategory.UNKNOWN else 0.0), 4),
        )
        plan = ExecutionPlan(
            planned_agents=[
                AgentName.INTAKE,
                AgentName.CLASSIFIER,
                AgentName.DIAGNOSTIC,
                AgentName.CERT_MAPPER,
                AgentName.REMEDIATION,
                AgentName.ASSESSMENT,
                AgentName.MANAGER,
            ],
            dynamic_threshold=threshold,
            requires_human_review_flag=completeness < 0.40,
            data_completeness=round(completeness, 4),
            planning_reasoning=[
                f"Completeness computed from critical evidence fields is {completeness:.2f}.",
                f"Primary suspected category is {suspected.value} from {', '.join(key_signals) or 'limited signals'}.",
                f"Dynamic threshold set to {threshold:.2f} based on evidence completeness.",
                f"Retrieved {len(similar)} structurally similar prior experiments for organizational memory.",
            ],
            similar_experiments=similar,
            team_skill_context=skill_context,
        )
        return PlannerContext(hypothesis=hypothesis, plan=plan, planned_at=datetime.now(timezone.utc))

    def _data_completeness(self, experiment: ExperimentLog) -> float:
        fields = [
            bool(experiment.metrics),
            bool(experiment.baseline_metrics),
            bool(experiment.validation_strategy),
            bool(experiment.class_balance),
            bool(experiment.failure_observation),
            bool(experiment.feature_set),
            bool(experiment.preprocessing_steps),
            bool(experiment.training_config),
            bool(experiment.deployment_context),
            bool(experiment.failure_symptoms),
        ]
        return sum(fields) / len(fields)

    def _signals(self, experiment: ExperimentLog) -> list[tuple[FailureCategory, bool]]:
        text = f"{experiment.failure_observation} {experiment.engineer_notes}".lower()
        feature_keywords = any(term in text for term in ["feature", "encoding", "embedding", "tokenization"])
        return [
            (FailureCategory.DATA_LEAKAGE, experiment.has_leakage_signal),
            (FailureCategory.RESPONSIBLE_AI, experiment.has_bias_language),
            (FailureCategory.DEPLOYMENT_DRIFT, experiment.has_drift_indicators or experiment.pipeline_stage in {"deployment", "monitoring"}),
            (FailureCategory.EVALUATION_METHODOLOGY, experiment.minority_pct < 20 and experiment.reported_metric == "accuracy"),
            (FailureCategory.FEATURE_ENGINEERING, feature_keywords or experiment.pipeline_stage == "feature_engineering"),
            (FailureCategory.DATA_QUALITY, bool(experiment.error_logs and experiment.data_quality_signals)),
        ]

    def _key_signals(self, experiment: ExperimentLog, category: FailureCategory) -> list[str]:
        mapping = {
            FailureCategory.DATA_LEAKAGE: ["suspected_leakage_columns", "failure_observation"],
            FailureCategory.RESPONSIBLE_AI: ["failure_observation", "engineer_notes", "metrics"],
            FailureCategory.DEPLOYMENT_DRIFT: ["drift_indicators", "pipeline_stage", "metric_degradation_score"],
            FailureCategory.EVALUATION_METHODOLOGY: ["class_balance", "accuracy", "minority_f1", "validation_strategy"],
            FailureCategory.FEATURE_ENGINEERING: ["feature_set", "preprocessing_steps", "pipeline_stage"],
            FailureCategory.DATA_QUALITY: ["error_logs", "data_quality_signals"],
        }
        return mapping.get(category, ["failure_observation"])

    def _hypothesis_statement(self, experiment: ExperimentLog, category: FailureCategory, key_signals: list[str]) -> str:
        if category == FailureCategory.EVALUATION_METHODOLOGY:
            return (
                f"{experiment.experiment_id} likely reflects evaluation methodology risk because class_balance="
                f"{experiment.class_balance}, accuracy={experiment.metrics.get('accuracy')}, "
                f"minority_f1={experiment.minority_f1}, and validation_strategy={experiment.validation_strategy}."
            )
        if category == FailureCategory.RESPONSIBLE_AI:
            return f"{experiment.experiment_id} likely reflects responsible AI risk because fairness language and group metrics appear in the experiment evidence."
        if category == FailureCategory.UNKNOWN:
            return f"{experiment.experiment_id} has insufficient evidence for a specific failure hypothesis."
        return f"{experiment.experiment_id} likely reflects {category.value} based on {', '.join(key_signals)}."
