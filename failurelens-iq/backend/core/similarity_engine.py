from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from backend.models.enums import FailureCategory
from backend.models.schemas import ExperimentLog, SimilarExperiment


class SimilarityEngine:
    def build_feature_vector(self, experiment: ExperimentLog) -> np.ndarray:
        stage = experiment.pipeline_stage.lower()
        return np.array(
            [
                min(experiment.minority_pct / 50.0, 1.0),
                experiment.metric_degradation_score,
                float(experiment.has_error_logs),
                float(experiment.has_drift_indicators),
                float(experiment.has_leakage_signal),
                float(experiment.has_bias_language),
                float(experiment.reported_metric == "accuracy"),
                float(stage in {"deployment", "monitoring"}),
                min(len(experiment.preprocessing_steps) / 8.0, 1.0),
                min(len(experiment.feature_set) / 12.0, 1.0),
                min(len(experiment.data_quality_signals) / 5.0, 1.0),
            ],
            dtype=float,
        )

    def cosine_similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        denom = float(np.linalg.norm(left) * np.linalg.norm(right))
        if denom == 0:
            return 0.0
        return float(np.dot(left, right) / denom)

    def find_similar(self, target: ExperimentLog, others: list[ExperimentLog], top_k: int = 3) -> list[SimilarExperiment]:
        target_vec = self.build_feature_vector(target)
        scored: list[tuple[float, ExperimentLog, list[str]]] = []
        for other in others:
            score = self.cosine_similarity(target_vec, self.build_feature_vector(other))
            signals = self._shared_signals(target, other)
            if score > 0:
                scored.append((score, other, signals))
        scored.sort(key=lambda item: item[0], reverse=True)
        now = datetime.now(timezone.utc)
        return [
            SimilarExperiment(
                experiment_id=other.experiment_id,
                team_id=other.team_id,
                similarity_score=round(score, 4),
                shared_signals=signals or ["Both experiments share a similar metric and pipeline evidence profile."],
                outcome_note=f"{other.outcome} / {other.failure_category_label or FailureCategory.UNKNOWN.value}",
                days_ago=max((now - other.timestamp).days, 0),
            )
            for score, other, signals in scored[:top_k]
        ]

    def _shared_signals(self, left: ExperimentLog, right: ExperimentLog) -> list[str]:
        signals: list[str] = []
        if left.reported_metric == right.reported_metric == "accuracy" and left.minority_pct < 25 and right.minority_pct < 25:
            signals.append("Both used accuracy as primary metric on imbalanced data.")
        if left.has_leakage_signal and right.has_leakage_signal:
            signals.append("Both had suspected leakage columns or leakage language.")
        if left.has_drift_indicators and right.has_drift_indicators:
            signals.append("Both showed drift indicators.")
        if left.has_bias_language and right.has_bias_language:
            signals.append("Both involved protected-attribute fairness language.")
        if left.data_quality_signals and right.data_quality_signals:
            signals.append("Both had schema or data quality signals.")
        return signals
