from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.models.enums import FailureCategory
from backend.models.schemas import ExperimentLog


class DataLoader:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd()
        self.synthetic_dir = self.root / "data" / "synthetic"
        self.ontology_dir = self.root / "data" / "ontology"
        self.experiments: list[ExperimentLog] = []
        self.team_profiles: dict[str, dict[str, Any]] = {}
        self.work_context: dict[str, dict[str, Any]] = {}
        self.assessment_results: dict[str, Any] = {}
        self.semantic_model: dict[str, Any] = {}

    def load_all(self) -> None:
        self.experiments = [
            ExperimentLog.model_validate(item)
            for item in self._read_json(self.synthetic_dir / "ml_experiment_logs.json", [])
        ]
        self.team_profiles = {
            item["team_id"]: item for item in self._read_json(self.synthetic_dir / "team_profiles.json", [])
        }
        self.work_context = {
            item["team_id"]: item for item in self._read_json(self.synthetic_dir / "work_context.json", [])
        }
        self.assessment_results = self._read_json(self.synthetic_dir / "assessment_results.json", {})
        self.semantic_model = self._read_json(self.ontology_dir / "semantic_model.json", {})

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def get_experiment(self, experiment_id: str) -> ExperimentLog:
        for experiment in self.experiments:
            if experiment.experiment_id == experiment_id:
                return experiment
        raise KeyError(f"Unknown experiment_id: {experiment_id}")

    def get_team_profile(self, team_id: str) -> dict[str, Any]:
        return self.team_profiles.get(team_id, {})

    def get_work_context(self, team_id: str) -> dict[str, Any]:
        return self.work_context.get(team_id, {})

    def experiments_for_team(self, team_id: str) -> list[ExperimentLog]:
        return [experiment for experiment in self.experiments if experiment.team_id == team_id]

    def infer_category(self, experiment: ExperimentLog) -> FailureCategory:
        if experiment.failure_category_label:
            for category in FailureCategory:
                if category.value == experiment.failure_category_label:
                    return category
        if experiment.has_leakage_signal:
            return FailureCategory.DATA_LEAKAGE
        if experiment.has_bias_language:
            return FailureCategory.RESPONSIBLE_AI
        stage = experiment.pipeline_stage.lower()
        if experiment.has_drift_indicators or stage in {"deployment", "monitoring"}:
            return FailureCategory.DEPLOYMENT_DRIFT
        if experiment.minority_pct < 20 and experiment.reported_metric == "accuracy":
            return FailureCategory.EVALUATION_METHODOLOGY
        feature_text = " ".join(experiment.feature_set + experiment.preprocessing_steps + [experiment.failure_observation]).lower()
        if any(term in feature_text for term in ["feature", "encoding", "embedding", "tokenization"]):
            return FailureCategory.FEATURE_ENGINEERING
        if experiment.error_logs and experiment.data_quality_signals:
            return FailureCategory.DATA_QUALITY
        return FailureCategory.UNKNOWN

    def team_category_counts(self, team_id: str) -> Counter[str]:
        return Counter(self.infer_category(exp).value for exp in self.experiments_for_team(team_id) if exp.outcome == "failure")
